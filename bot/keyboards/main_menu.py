from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Создает главное меню бота (скриншот 1)
    """
    builder = InlineKeyboardBuilder()
    
    # Ряд 1: 🛒 Купить VPN | 👤 Профиль
    builder.row(
        InlineKeyboardButton(text="🛒 Купить VPN", callback_data="buy_subscription"),
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile")
    )
    
    # Ряд 2: 💎 Пробный период
    builder.row(
        InlineKeyboardButton(text="💎 Пробный период", callback_data="trial")
    )
    
    # Ряд 3: ❓ Помощь | ⚙️ Настройки
    builder.row(
        InlineKeyboardButton(text="❓ Помощь", callback_data="instructions"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
    )
    
    return builder.as_markup()
