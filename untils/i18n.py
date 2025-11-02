from aiogram.utils.i18n import I18n
from aiogram.utils.i18n.middleware import FSMI18nMiddleware

i18n = I18n(path="locales", default_locale="en", domain="messages")
i18n_middleware = FSMI18nMiddleware(i18n)

_ = i18n.gettext