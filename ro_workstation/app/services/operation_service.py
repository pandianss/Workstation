import json
import uuid
from datetime import datetime, UTC

import pandas as pd

from app.utils.audit import log_action
from app.utils.validators import validate_operation
from modules.utils.paths import project_path

DATA_DIR = project_path("app", "data")
ACCOUNTS_FILE = DATA_DIR / "accounts.json"
OPERATIONS_FILE = DATA_DIR / "operations.json"

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


def _ensure_storage():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ACCOUNTS_FILE.exists():
        ACCOUNTS_FILE.write_text(json.dumps(DEFAULT_ACCOUNTS, indent=2), encoding="utf-8")
    if not OPERATIONS_FILE.exists():
        OPERATIONS_FILE.write_text("[]", encoding="utf-8")


def _load_json(path: Path):
    _ensure_storage()
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _find_account(accounts, account_number):
    return next((account for account in accounts if account["account_number"] == account_number), None)


def _append_operation(record):
    operations = _load_json(OPERATIONS_FILE)
    operations.append(record)
    _save_json(OPERATIONS_FILE, operations)


def get_accounts():
    accounts = _load_json(ACCOUNTS_FILE)
    return pd.DataFrame(accounts)


def get_operation_history(limit=100):
    operations = _load_json(OPERATIONS_FILE)
    if not operations:
        return pd.DataFrame(
            columns=["operation_id", "timestamp", "type", "account", "branch", "status", "message"]
        )
    df = pd.DataFrame(operations)
    return df.sort_values("timestamp", ascending=False).head(limit)


def _execute_transfer(data, accounts):
    source = _find_account(accounts, data["account"])
    destination = _find_account(accounts, data["destination_account"])

    if not source:
        return False, "Source account not found", None
    if not destination:
        return False, "Destination account not found", None
    if source["status"] != "ACTIVE" or destination["status"] != "ACTIVE":
        return False, "Both accounts must be active for transfer", None
    if source["branch"] != data["branch"]:
        return False, "Branch does not match the source account", None
    if source["balance"] < data["amount"]:
        return False, "Insufficient balance in the source account", None

    old_source = dict(source)
    old_destination = dict(destination)

    source["balance"] = round(source["balance"] - data["amount"], 2)
    destination["balance"] = round(destination["balance"] + data["amount"], 2)
    source["remarks"] = data["remarks"] or source.get("remarks", "")
    destination["remarks"] = f"Received transfer from {source['account_number']}"

    return True, "Transfer completed successfully", {
        "source_before": old_source,
        "source_after": dict(source),
        "destination_before": old_destination,
        "destination_after": dict(destination),
    }


def _execute_update(data, accounts):
    account = _find_account(accounts, data["account"])
    if not account:
        return False, "Account not found", None
    if account["branch"] != data["branch"]:
        return False, "Branch does not match the selected account", None

    field = data["update_field"]
    old_account = dict(account)
    account[field] = data["update_value"]
    if data["remarks"]:
        account["remarks"] = data["remarks"]

    return True, f"Updated {field} successfully", {
        "before": old_account,
        "after": dict(account),
    }


def _execute_closure(data, accounts):
    account = _find_account(accounts, data["account"])
    if not account:
        return False, "Account not found", None
    if account["branch"] != data["branch"]:
        return False, "Branch does not match the selected account", None
    if account["status"] != "ACTIVE":
        return False, "Only active accounts can be closed", None
    if round(account["balance"], 2) != 0:
        return False, "Account balance must be zero before closure", None

    old_account = dict(account)
    account["status"] = "CLOSED"
    account["remarks"] = data["remarks"] or "Closed through workstation"

    return True, "Account closed successfully", {
        "before": old_account,
        "after": dict(account),
    }


def process_operation(data, user="system"):
    validation = validate_operation(data)
    if not validation["valid"]:
        return {
            "success": False,
            "message": validation["message"],
        }

    accounts = _load_json(ACCOUNTS_FILE)
    operation_type = data["type"]

    if operation_type == "Transfer":
        success, message, details = _execute_transfer(data, accounts)
    elif operation_type == "Update":
        success, message, details = _execute_update(data, accounts)
    elif operation_type == "Closure":
        success, message, details = _execute_closure(data, accounts)
    else:
        return {"success": False, "message": f"Unsupported operation type: {operation_type}"}

    operation_id = str(uuid.uuid4())
    record = {
        "operation_id": operation_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "user": user,
        "type": operation_type,
        "account": data["account"],
        "branch": data["branch"],
        "status": "SUCCESS" if success else "FAILED",
        "message": message,
        "remarks": data.get("remarks", ""),
        "details": details,
    }
    if data.get("destination_account"):
        record["destination_account"] = data["destination_account"]

    _append_operation(record)

    if success:
        _save_json(ACCOUNTS_FILE, accounts)
        log_action(user, f"{operation_type} executed for account {data['account']}")

    return {
        "success": success,
        "message": message,
        "operation_id": operation_id,
        "details": details,
    }
