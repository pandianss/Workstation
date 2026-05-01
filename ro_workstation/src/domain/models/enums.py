from enum import Enum


class TaskPriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class OperationType(str, Enum):
    transfer = "Transfer"
    update = "Update"
    closure = "Closure"
