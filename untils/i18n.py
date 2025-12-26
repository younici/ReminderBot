from pathlib import Path

from aiogram.utils.i18n import I18n
from aiogram.utils.i18n.middleware import FSMI18nMiddleware

LOCALES_PATH = Path(__file__).resolve().parent.parent / "locales"

i18n = I18n(path=str(LOCALES_PATH), default_locale="en", domain="messages")
i18n_middleware = FSMI18nMiddleware(i18n)

_ = i18n.gettext


def normalize_locale(value: str | None) -> str:
    if not value:
        return "en"
    cleaned = value.lower().replace("_", "-")
    base = cleaned.split("-")[0]
    return base or "en"
