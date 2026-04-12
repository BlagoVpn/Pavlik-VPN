from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from apps.db.models.user import User

_LABELS = {
    "ru": {
        "buy": "Купить VPN",
        "trial": "Бесплатный пробный период на 3 дня",
        "profile": "Мой профиль",
        "referrals": "Рефералы",
        "instructions": "Инструкция по подключению",
        "support": "Поддержка",
        "channel": "Наш канал",
    },
    "en": {
        "buy": "Buy VPN",
        "trial": "Free 3-day trial period",
        "profile": "My Profile",
        "referrals": "Referrals",
        "instructions": "Connection Guide",
        "support": "Support",
        "channel": "Our Channel",
    },
}


def get_main_menu_keyboard(user: User, language: str = "ru") -> InlineKeyboardMarkup:
    lbl = _LABELS.get(language, _LABELS["ru"])
    builder = InlineKeyboardBuilder()

    # Ряд 0: Купить
    builder.row(
        InlineKeyboardButton(
            text=lbl["buy"],
            callback_data="buy_subscription",
            icon_custom_emoji_id="5258152182150077732",
            style="primary"
        )
    )

    # Ряд 1: Пробный период (если не использован)
    if not user.trial_used:
        builder.row(
            InlineKeyboardButton(
                text=lbl["trial"],
                callback_data="confirm_trial_request",
                icon_custom_emoji_id="5258185631355378853",
                style="success"
            )
        )

    # Ряд 2: Мой профиль и Рефералы
    builder.row(
        InlineKeyboardButton(
            text=lbl["profile"],
            callback_data="profile",
            icon_custom_emoji_id="5258011929993026890"
        ),
        InlineKeyboardButton(
            text=lbl["referrals"],
            callback_data="referrals",
            icon_custom_emoji_id="5258362837411045098"
        )
    )

    # Ряд 3: Инструкция
    builder.row(
        InlineKeyboardButton(
            text=lbl["instructions"],
            callback_data="instructions",
            icon_custom_emoji_id="5258328383183396223",
            style="primary"
        )
    )

    # Ряд 4: Поддержка | Канал
    builder.row(
        InlineKeyboardButton(
            text=lbl["support"],
            url="https://t.me/blago_vpn_manager",
            icon_custom_emoji_id="5258179403652801593"
        ),
        InlineKeyboardButton(
            text=lbl["channel"],
            url="https://t.me/blago_vpn_news",
            icon_custom_emoji_id="5260268501515377807"
        )
    )

    return builder.as_markup()
