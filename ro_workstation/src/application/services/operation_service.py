from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pandas as pd

from src.core.logging.audit import AuditLogger
from src.core.paths import project_path
from src.domain.models.enums import OperationType
from src.domain.schemas.operation import AccountRecord, OperationRequest
from src.infrastructure.persistence.json_repo import JsonRepository


DEFAULT_ACCOUNTS = [
    {
        "account_number": "1000000001",
        "branch": "RO001",
        "holder_name": "Acme Traders",
        "balance": 500000.0,
        "status": "ACTIVE",
        "remarks": "Seeded account",
    },
    {
        "account_number": "1000000002",
        "branch": "RO001",
        "holder_name": "North Field Agro",
        "balance": 150000.0,
        "status": "ACTIVE",
        "remarks": "Seeded account",
    },
    {
        "account_number": "1000000003",
        "branch": "RO002",
        "holder_name": "Closure Candidate",
        "balance": 0.0,
        "status": "ACTIVE",
        "remarks": "Eligible for closure",
    },
]


class OperationService:
    def __init__(self, accounts_path=None, operations_path=None) -> None:
        self.accounts_repo = JsonRepository(accounts_path or project_path("data", "accounts.json"), DEFAULT_ACCOUNTS)
        self.operations_repo = JsonRepository(operations_path or project_path("data", "operations.json"), [])
        self.audit_logger = AuditLogger()

    def get_accounts(self) -> pd.DataFrame:
        return pd.DataFrame(self.accounts_repo.read())

    def get_operation_history(self, limit: int = 100) -> pd.DataFrame:
        operations = self.operations_repo.read()
        if not operations:
            return pd.DataFrame(columns=["operation_id", "timestamp", "type", "account", "branch", "status", "message"])
        return pd.DataFrame(operations).sort_values("timestamp", ascending=False).head(limit)

    def process_operation(self, data: dict, user: str = "system") -> dict:
        request = OperationRequest.model_validate(data)
        validation = self._validate_operation(request)
        if validation:
            return {"success": False, "message": validation}

        accounts = self.accounts_repo.read()
        if request.type == OperationType.transfer:
            success, message, details = self._execute_transfer(request, accounts)
        elif request.type == OperationType.update:
            success, message, details = self._execute_update(request, accounts)
        else:
            success, message, details = self._execute_closure(request, accounts)

        operation_id = str(uuid.uuid4())
        record = {
            "operation_id": operation_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "user": user,
            "type": request.type.value,
            "account": request.account,
            "branch": request.branch,
            "status": "SUCCESS" if success else "FAILED",
            "message": message,
            "remarks": request.remarks,
            "details": details,
            "destination_account": request.destination_account or None,
        }
        operations = self.operations_repo.read()
        operations.append(record)
        self.operations_repo.write(operations)

        if success:
            self.accounts_repo.write(accounts)
            self.audit_logger.log(user, f"{request.type.value} executed for account {request.account}")

        return {
            "success": success,
            "message": message,
            "operation_id": operation_id,
            "details": details,
        }

    def _validate_operation(self, request: OperationRequest) -> str | None:
        if not request.branch:
            return "Branch is required"
        if not request.account:
            return "Primary account number is required"
        if request.type == OperationType.transfer:
            if request.amount <= 0:
                return "Transfer amount must be greater than zero"
            if not request.destination_account:
                return "Destination account is required for transfer"
            if request.destination_account == request.account:
                return "Source and destination accounts must be different"
        if request.type == OperationType.update:
            if not request.update_field:
                return "Select a field to update"
            if not request.update_value:
                return "Enter the new value for the selected field"
        if request.type == OperationType.closure and request.amount < 0:
            return "Closure amount cannot be negative"
        return None

    @staticmethod
    def _find_account(accounts: list[dict], account_number: str) -> dict | None:
        return next((account for account in accounts if account["account_number"] == account_number), None)

    def _execute_transfer(self, request: OperationRequest, accounts: list[dict]) -> tuple[bool, str, dict | None]:
        source = self._find_account(accounts, request.account)
        destination = self._find_account(accounts, request.destination_account)
        if not source:
            return False, "Source account not found", None
        if not destination:
            return False, "Destination account not found", None
        if source["status"] != "ACTIVE" or destination["status"] != "ACTIVE":
            return False, "Both accounts must be active for transfer", None
        if source["branch"] != request.branch:
            return False, "Branch does not match the source account", None
        if source["balance"] < request.amount:
            return False, "Insufficient balance in the source account", None

        source_before, destination_before = dict(source), dict(destination)
        source["balance"] = round(source["balance"] - request.amount, 2)
        destination["balance"] = round(destination["balance"] + request.amount, 2)
        source["remarks"] = request.remarks or source.get("remarks", "")
        destination["remarks"] = f"Received transfer from {source['account_number']}"
        return True, "Transfer completed successfully", {
            "source_before": source_before,
            "source_after": dict(source),
            "destination_before": destination_before,
            "destination_after": dict(destination),
        }

    def _execute_update(self, request: OperationRequest, accounts: list[dict]) -> tuple[bool, str, dict | None]:
        account = self._find_account(accounts, request.account)
        if not account:
            return False, "Account not found", None
        if account["branch"] != request.branch:
            return False, "Branch does not match the selected account", None
        before = dict(account)
        account[request.update_field] = request.update_value
        if request.remarks:
            account["remarks"] = request.remarks
        return True, f"Updated {request.update_field} successfully", {"before": before, "after": dict(account)}

    def _execute_closure(self, request: OperationRequest, accounts: list[dict]) -> tuple[bool, str, dict | None]:
        account = self._find_account(accounts, request.account)
        if not account:
            return False, "Account not found", None
        if account["branch"] != request.branch:
            return False, "Branch does not match the selected account", None
        if account["status"] != "ACTIVE":
            return False, "Only active accounts can be closed", None
        if round(account["balance"], 2) != 0:
            return False, "Account balance must be zero before closure", None
        before = dict(account)
        account["status"] = "CLOSED"
        account["remarks"] = request.remarks or "Closed through workstation"
        return True, "Account closed successfully", {"before": before, "after": dict(account)}
