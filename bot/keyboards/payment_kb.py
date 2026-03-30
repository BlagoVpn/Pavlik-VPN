from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_payment_keyboard(pay_url: str, transaction_id: str) -> InlineKeyboardMarkup:
    """
    Клавиатура оплаты (скриншот 3)
    """
    builder = InlineKeyboardBuilder()
    
    # Основная кнопка оплаты (открывается как Mini App)
    # Попробуем передать цвет, если поддерживается протоколом
    builder.row(InlineKeyboardButton(
        text="💳 Оплатить", 
        web_app=WebAppInfo(url=pay_url)
    ))
    
    # Кнопка подтверждения
    builder.row(InlineKeyboardButton(
        text="✅ Я оплатил", 
        callback_data=f"check_payment:{transaction_id}"
    ))
    
    # Кнопка назад
    builder.row(InlineKeyboardButton(
        text="◀️ Назад", 
        callback_data="buy_subscription"
    ))
    
    return builder.as_markup()
