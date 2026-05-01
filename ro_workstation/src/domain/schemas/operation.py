from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from src.domain.models.enums import OperationType


class AccountRecord(BaseModel):
    account_number: str
    branch: str
    holder_name: str
    balance: float = 0.0
    status: str = "ACTIVE"
    remarks: str = ""


class OperationRequest(BaseModel):
    branch: str
    account: str
    amount: float = 0.0
    type: OperationType
    remarks: str = ""
    destination_account: str = ""
    update_field: str = ""
    update_value: str = ""


class OperationRecord(BaseModel):
    operation_id: str
    timestamp: datetime
    user: str
    type: str
    account: str
    branch: str
    status: str
    message: str
    remarks: str = ""
    destination_account: str | None = None
    details: dict | None = None
