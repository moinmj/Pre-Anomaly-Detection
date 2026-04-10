from collections import defaultdict

# 🔥 Store account data
account_data = defaultdict(lambda: {
    "transactions": [],
    "fraud_count": 0,
    "approval_count": 0,
    "status": "ACTIVE"
})


# 🔹 Update account with new transaction
def update_account(account_id, transaction):
    account_data[account_id]["transactions"].append(transaction)

    # Keep only last 10 transactions
    if len(account_data[account_id]["transactions"]) > 10:
        account_data[account_id]["transactions"].pop(0)


# 🔹 Increment fraud count
def increment_fraud(account_id):
    account_data[account_id]["fraud_count"] += 1

    # 🔥 Auto-block if threshold reached
    if account_data[account_id]["fraud_count"] >= 3:
        account_data[account_id]["status"] = "BLOCKED"
        print(f"🚫 ACCOUNT BLOCKED: {account_id}")


# 🔹 Detect mule account (behavior-based)
def detect_mule_account(account_id):
    history = account_data[account_id]["transactions"]

    if len(history) < 3:
        return False

    high_velocity = sum(
        1 for t in history if t.get("velocity_6h", 0) > 10
    )

    foreign = sum(
        1 for t in history if t.get("foreign_request", 0) == 1
    )

    # 🚨 Mule pattern
    if high_velocity >= 3 and foreign >= 2:
        return True

    return False


# 🔹 Check if account is blocked
def is_account_blocked(account_id):
    return account_data[account_id]["status"] == "BLOCKED"


# 🔹 Get account summary (useful for dashboard)
def get_account_summary(account_id):
    return account_data[account_id]

def increment_approval(account_id):
    account_data[account_id]["approval_count"] += 1

def get_approval_count(account_id):
    return account_data[account_id]["approval_count"]