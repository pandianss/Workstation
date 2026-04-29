def validate_operation(data):
    if not data["branch"]:
        return {"valid": False, "message": "Branch is required"}

    if not data["account"]:
        return {"valid": False, "message": "Primary account number is required"}

    operation_type = data["type"]

    if operation_type == "Transfer":
        if data["amount"] <= 0:
            return {"valid": False, "message": "Transfer amount must be greater than zero"}
        if not data.get("destination_account"):
            return {"valid": False, "message": "Destination account is required for transfer"}
        if data["destination_account"] == data["account"]:
            return {"valid": False, "message": "Source and destination accounts must be different"}

    if operation_type == "Update":
        if not data.get("update_field"):
            return {"valid": False, "message": "Select a field to update"}
        if not data.get("update_value"):
            return {"valid": False, "message": "Enter the new value for the selected field"}

    if operation_type == "Closure" and data["amount"] < 0:
        return {"valid": False, "message": "Closure amount cannot be negative"}

    return {"valid": True}
