from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_payment_keyboard(pay_url: str, transaction_id: str) -> InlineKeyboardMarkup:
    """
    Клавиатура оплаты (используем обычный URL вместо WebApp для работы диплинков банков)
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка оплаты – используем стандартный url
    builder.row(InlineKeyboardButton(
        text="Оплатить", 
        url=pay_url,
        icon_custom_emoji_id="5445353829304387411",
        style="success"
    ))
    
    # Кнопка подтверждения
    builder.row(InlineKeyboardButton(
        text="Я оплатил", 
        callback_data=f"check_payment:{transaction_id}",
        icon_custom_emoji_id="5206607081334906820"
    ))
    
    # Кнопка назад
    builder.row(InlineKeyboardButton(
        text="Назад к тарифам", 
        callback_data="buy_subscription",
        icon_custom_emoji_id="5258236805890710909"
    ))
    
    return builder.as_markup()
