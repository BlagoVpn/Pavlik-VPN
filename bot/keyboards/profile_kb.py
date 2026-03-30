from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_profile_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура внутри профиля пользователя
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопки истории и подписок
    builder.row(
        InlineKeyboardButton(text="История оплат", callback_data="history_tx", icon_custom_emoji_id="5258419835922030550")
    )
    builder.row(
        InlineKeyboardButton(text="Мои подписки", callback_data="my_subs", icon_custom_emoji_id="5258185631355378853")
    )
    
    # Кнопка назад
    builder.row(
        InlineKeyboardButton(text="Назад в меню", callback_data="back_to_main", icon_custom_emoji_id="5258236805890710909")
    )
    
    return builder.as_markup()
