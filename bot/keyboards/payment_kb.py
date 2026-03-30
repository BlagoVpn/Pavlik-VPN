from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

class SuccessButton(InlineKeyboardButton):
    """
    Бэкенд-хак: расширяем кнопку, чтобы она «проглотила» параметр style.
    Это позволит отправить 'success' напрямую в Telegram API.
    """
    style: str = "success"

def get_payment_keyboard(pay_url: str, transaction_id: str) -> InlineKeyboardMarkup:
    """
    Клавиатура оплаты (скриншот 3)
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка оплаты – форсируем стиль 'success' (зеленый)
    builder.row(SuccessButton(
        text="💳 Оплатить", 
        web_app=WebAppInfo(url=pay_url),
        style="success"
    ))
    
    # Кнопка подтверждения
    builder.row(InlineKeyboardButton(
        text="✅ Я оплатил", 
        callback_data=f"check_payment:{transaction_id}"
    ))
    
    # Кнопка назад
    builder.row(InlineKeyboardButton(
        text="Назад", 
        callback_data="buy_subscription",
        icon_custom_emoji_id="5258236805890710909"
    ))
    
    return builder.as_markup()
