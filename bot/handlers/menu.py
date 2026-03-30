from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession
from apps.db.repositories.user import get_user_by_id
from bot.keyboards.main_menu import get_main_menu_keyboard
from bot.keyboards.subscriptions import get_subscriptions_keyboard
from bot.keyboards.common import get_back_keyboard

menu_router = Router()

@menu_router.callback_query(F.data == "profile")
async def show_profile(callback: types.CallbackQuery, session: AsyncSession):
    """
    Показ профиля пользователя из БД
    """
    # Берем юзера из базы
    user = await get_user_by_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("Ошибка: Профиль не найден. Нажмите /start")
        return

    status = "Активна ✅" if user.is_active else "Не активна ❌"
    end_date = user.subscription_end.strftime("%d.%m.%Y") if user.subscription_end else "—"

    await callback.message.edit_text(
        f"👤 **Мой профиль**\n\n"
        f"🆔 Ваш ID: `{user.user_id}`\n"
        f"📅 Статус подписки: **{status}**\n"
        f"⌛️ Истекает: `{end_date}`\n\n"
        "Вы можете продлить подписку в меню ниже! 👇",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

from bot.keyboards.payment_kb import get_payment_keyboard
from apps.services.payment.platega_service import PlategaService
from apps.db.repositories.transaction import create_transaction, get_transaction, update_transaction_id, update_transaction_status
from config import config

# Инициализируем сервис платежей
platega = PlategaService(config.PLATEGA_MERCHANT_ID, config.PLATEGA_SECRET)

@menu_router.callback_query(F.data == "buy_subscription")
async def select_subscription(callback: types.CallbackQuery):
    """
    Выбор тарифа (Скриншот 2)
    """
    await callback.message.edit_text(
        "📦 **Выбери тариф:**\n\n"
        "• Безлимит устройств\n"
        "• Без логов\n"
        "• Поддержка 24/7",
        reply_markup=get_subscriptions_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

import asyncio

async def auto_check_payment(message: types.Message, tx_id: int, platega_id: str, session_maker):
    """
    Фоновая задача для автоматического подтверждения оплаты (Auto-confirm)
    Теория: Опрашиваем API раз в 20 секунд в течение 10 минут.
    """
    for _ in range(30): # Проверяем в течение 10 минут (30 * 20 сек)
        await asyncio.sleep(20)
        
        status = await platega.check_status(platega_id)
        if status == "CONFIRMED":
            async with session_maker() as session:
                await update_transaction_status(session, tx_id, "CONFIRMED")
            
            await message.edit_text(
                "✅ **Оплата подтверждена автоматически!**\n\n"
                "Ваша подписка активирована. Ожидайте данные для подключения! 🚀",
                reply_markup=get_back_keyboard(),
                parse_mode="Markdown"
            )
            return
        
        if status in ["CANCELED", "FAILED"]:
            return

@menu_router.callback_query(F.data.startswith("buy:"))
async def process_buy_tariff(callback: types.CallbackQuery, session: AsyncSession):
    """
    Процесс покупки тарифа и запуск авто-проверки
    """
    _, tariff_key, amount = callback.data.split(":")
    amount = float(amount)

    await callback.message.edit_text("⏳ **Загрузка платежа...**", parse_mode="Markdown")

    tx = await create_transaction(session, callback.from_user.id, amount, tariff_key)
    description = f"Оплата VPN: {tariff_key}"
    payment_data = await platega.create_transaction(amount, description, str(tx.id))

    if not payment_data or "redirect" not in payment_data:
        await callback.message.edit_text(
            "❌ **Ошибка при создании счета.**",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
        return

    await update_transaction_id(session, tx.id, payment_data["transactionId"])
    
    # Запускаем фоновую задачу авто-проверки (не ждем её завершения - .create_task)
    from apps.db.database import async_session
    asyncio.create_task(
        auto_check_payment(
            callback.message, 
            tx.id, 
            payment_data["transactionId"],
            async_session
        )
    )

    tariff_name = {"month_1": "1 месяц", "month_3": "3 месяца", "month_6": "6 месяцев", "month_12": "12 месяцев"}.get(tariff_key, tariff_key)

    await callback.message.edit_text(
        f"🥉 **Тариф: {tariff_name}**\n\n"
        f"💰 Сумма: **{amount}₽**\n"
        f"📦 Трафик: **500 GB**\n\n"
        "🟢 Нажми кнопку ниже для оплаты.\n"
        "После оплаты бот **автоматически** увидит платеж в течение минуты! ✅",
        reply_markup=get_payment_keyboard(payment_data["redirect"], str(tx.id)),
        parse_mode="Markdown"
    )
    await callback.answer()

@menu_router.callback_query(F.data.startswith("check_payment:"))
async def check_payment_status(callback: types.CallbackQuery, session: AsyncSession):
    """
    Проверка статуса платежа по кнопке
    """
    tx_id = int(callback.data.split(":")[1])
    tx = await get_transaction(session, tx_id)

    if not tx or not tx.platega_id:
        await callback.answer("Ошибка: Транзакция не найдена.", show_alert=True)
        return

    # Запрашиваем актуальный статус у Platega
    status = await platega.check_status(tx.platega_id)
    
    if status == "CONFIRMED":
        await update_transaction_status(session, tx_id, "CONFIRMED")
        await callback.message.edit_text(
            "✅ **Оплата прошла успешно!**\n\n"
            "Ваша подписка активирована. В ближайшее время мы пришлем вам данные для подключения.",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
    elif status == "PENDING":
        await callback.answer("⏳ Платеж еще обрабатывается. Попробуйте через минуту.", show_alert=True)
    else:
        await callback.answer(f"❌ Статус платежа: {status}", show_alert=True)

@menu_router.callback_query(F.data == "instructions")
async def show_instructions(callback: types.CallbackQuery):
    """
    Инструкция (Помощь)
    """
    await callback.message.edit_text(
        "❓ **Помощь и инструкции**\n\n"
        "Здесь будет ваша инструкция по подключению через строку vless...",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@menu_router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    """
    Возврат в главное меню
    """
    await callback.message.edit_text(
        f"Привет, {callback.from_user.first_name}! 🚀\n\n"
        "Добро пожаловать в **Павлик VPN**. Я помогу тебе получить быстрый и безопасный доступ "
        "в интернет из любой точки мира. 🌍\n\n"
        "Выбери нужное действие ниже: 👇",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()
