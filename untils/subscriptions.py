import os
from datetime import datetime, timedelta, timezone

FREE_REMINDER_LIMIT = int(os.getenv("FREE_REMINDER_LIMIT", 3))
SUBSCRIPTION_DURATION_DAYS = int(os.getenv("SUBSCRIPTION_DURATION_DAYS", 30))
SUBSCRIPTION_PRICE_STARS = int(os.getenv("SUBSCRIPTION_PRICE_STARS", 50))

SUBSCRIPTION_PAYLOAD = "premium_stars_subscription"
SUBSCRIPTION_TITLE = os.getenv("SUBSCRIPTION_TITLE", "ReminderBot Premium")
SUBSCRIPTION_DESCRIPTION = os.getenv(
    "SUBSCRIPTION_DESCRIPTION",
    "Unlimited reminders for 30 days. Paid with Telegram Stars.",
)


def is_premium_active(user) -> bool:
    expires = getattr(user, "premium_until", None)
    if not expires:
        return False

    if isinstance(expires, str):
        try:
            expires = datetime.fromisoformat(expires)
        except ValueError:
            return False

    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)

    return expires > datetime.now(timezone.utc)


def extend_subscription(user):
    now = datetime.now(timezone.utc)
    base = user.premium_until

    if isinstance(base, str):
        try:
            base = datetime.fromisoformat(base)
        except ValueError:
            base = None

    if base:
        if base.tzinfo is None:
            base = base.replace(tzinfo=timezone.utc)
        if base < now:
            base = now
    else:
        base = now

    new_until = base + timedelta(days=SUBSCRIPTION_DURATION_DAYS)
    user.premium_until = new_until
    return new_until
