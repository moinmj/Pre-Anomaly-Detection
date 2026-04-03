from collections import defaultdict

# 🔥 Store transactions per account
account_history = defaultdict(list)


def update_account(account_id, transaction):
    account_history[account_id].append(transaction)

    # Keep last 10 transactions
    if len(account_history[account_id]) > 10:
        account_history[account_id].pop(0)


def detect_mule_account(account_id):
    history = account_history[account_id]

    # Need minimum activity
    if len(history) < 3:
        return False

    high_velocity = sum(
        1 for t in history if t.get("velocity_6h", 0) > 10
    )

    foreign = sum(
        1 for t in history if t.get("foreign_request", 0) == 1
    )

    # 🚨 Mule pattern detection
    if high_velocity >= 3 and foreign >= 2:
        return True

    return False