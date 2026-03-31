from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton

class PrimaryButton(InlineKeyboardButton):
    """
    Хакинг Pydantic для поддержки стилей, если это поддерживается прослойкой API
    """
    style: str = "primary"

def get_referral_keyboard(ref_link: str) -> InlineKeyboardMarkup:
    """
    Клавиатура реферальной системы (Копирование в буфер + Стиль)
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            PrimaryButton(
                text="Скопировать реферальную ссылку", 
                copy_text=CopyTextButton(text=ref_link),
                icon_custom_emoji_id="5260687681733533075",
                style="primary"
            )
        ],
        [
            InlineKeyboardButton(
                text="Вернуться в меню", 
                callback_data="back_to_main",
                icon_custom_emoji_id="5258236805890710909"
            )
        ]
    ])
