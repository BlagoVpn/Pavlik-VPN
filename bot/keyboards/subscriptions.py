from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_subscriptions_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора тарифа (скриншот 2)
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(text="🥉 1 месяц — 149₽ / 500 GB", callback_data="buy:month_1:149"))
    builder.row(InlineKeyboardButton(text="🥈 3 месяца — 449₽ / 500 GB", callback_data="buy:month_3:449"))
    builder.row(InlineKeyboardButton(text="🥇 6 месяцев — 899₽ / 500 GB", callback_data="buy:month_6:899"))
    builder.row(InlineKeyboardButton(text="💎 12 месяцев — 1499₽ / 500 GB", callback_data="buy:month_12:1499"))
    
    # Кнопка назад
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
    
    return builder.as_markup()
