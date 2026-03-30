from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from apps.db.models.user import User

def get_main_menu_keyboard(user: User) -> InlineKeyboardMarkup:
    """
    Главное меню с премиум-стилями кнопок
    """
    builder = InlineKeyboardBuilder()
    
    # Ряд 0: Купить (Просто убираем стиль, чтобы она была стандартной серой)
    builder.row(
        InlineKeyboardButton(
            text="Купить VPN", 
            callback_data="buy_subscription",
            icon_custom_emoji_id="5258152182150077732"
        )
    )

    # Ряд 1: Пробный период
    if not user.trial_used:
        builder.row(
            InlineKeyboardButton(
                text="Бесплатный пробный период на 3 дня",
                callback_data="confirm_trial_request",
                icon_custom_emoji_id="5258185631355378853",
                style="success"
            )
        )
    
    # Ряд 2: Мой профиль и Рефералы
    builder.row(
        InlineKeyboardButton(
            text="Мой профиль", 
            callback_data="profile",
            icon_custom_emoji_id="5258011929993026890"
        ),
        InlineKeyboardButton(
            text="Рефералы", 
            callback_data="referrals",
            icon_custom_emoji_id="5258362837411045098"
        )
    )
    
    # Ряд 3: Поддержка и Канал
    builder.row(
        InlineKeyboardButton(
            text="Поддержка", 
            url="https://t.me/pavlik_manager",
            icon_custom_emoji_id="5258179403652801593"
        ),
        InlineKeyboardButton(
            text="Наш канал", 
            url="https://t.me/your_channel",
            icon_custom_emoji_id="5260268501515377807"
        )
    )
    
    return builder.as_markup()
