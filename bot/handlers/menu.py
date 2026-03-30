from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from apps.db.models.user import User
from apps.db.models.transaction import Transaction
from bot.keyboards.main_menu import get_main_menu_keyboard
from bot.keyboards.subscriptions import get_subscriptions_keyboard
from bot.keyboards.common import get_back_keyboard
from bot.keyboards.profile_kb import get_profile_keyboard
from bot.keyboards.trial_kb import get_trial_confirmation_keyboard

menu_router = Router()

@menu_router.callback_query(F.data == "profile")
async def show_profile(callback: types.CallbackQuery, session: AsyncSession):
    """
    Личный кабинет (Главная)
    """
    user_id = callback.from_user.id
    user = await session.get(User, user_id)
    
    if not user:
        await callback.answer("Ошибка: Пользователь не найден.")
        return

    await callback.message.edit_text(
        f"<tg-emoji emoji-id=\"5258262708838472996\">👤</tg-emoji> <b>Привет, {user.full_name}!</b>\n\n"
        f"<tg-emoji emoji-id=\"5258011929993026890\">🆔</tg-emoji> ID: <code>{user_id}</code>\n",
        reply_markup=get_profile_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@menu_router.callback_query(F.data == "history_tx")
async def show_history_tx(callback: types.CallbackQuery, session: AsyncSession):
    """
    История транзакций (последние 10)
    """
    user_id = callback.from_user.id
    
    # Получаем историю (последние 10 подтвержденных)
    stmt = select(Transaction).where(
        Transaction.user_id == user_id, 
        Transaction.status == "CONFIRMED"
    ).order_by(Transaction.id.desc()).limit(10)
    
    result = await session.execute(stmt)
    transactions = result.scalars().all()

    history_text = "\n".join([
        f"• {tx.tariff_key}: {tx.amount}₽ ({tx.created_at.strftime('%d.%m.%Y')})" 
        for tx in transactions
    ]) or "• История пока пуста"

    await callback.message.edit_text(
        f"<tg-emoji emoji-id=\"\">📜</tg-emoji> <b>История ваших транзакций</b>\n\n"
        f"{history_text}\n\n",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@menu_router.callback_query(F.data == "my_subs")
async def show_my_subs(callback: types.CallbackQuery, session: AsyncSession):
    """
    Текущие подписки юзера
    """
    user_id = callback.from_user.id
    user = await session.get(User, user_id)

    sub_status = "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> Не активна"
    if user.subscription_end:
        if user.subscription_end > datetime.now():
            sub_status = f"<tg-emoji emoji-id=\"5260341314095947411\">✅</tg-emoji> Активна (до {user.subscription_end.strftime('%d.%m.%Y %H:%M')})"
        else:
            sub_status = "<tg-emoji emoji-id=\"5258474669769497337\">⚠️</tg-emoji> Истекла"

    await callback.message.edit_text(
        f"<tg-emoji emoji-id=\"5255813559572508065\">💎</tg-emoji> <b>Ваши подписки</b>\n\n"
        f"<tg-emoji emoji-id=\"5258330865674494479\">🆔</tg-emoji> Статус основной подписки: <b>{sub_status}</b>\n\n"
        f"<i>(В будущем здесь будет отображен список всех ваших приватных ключей)</i>",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@menu_router.callback_query(F.data == "referrals")
async def show_referrals(callback: types.CallbackQuery):
    """
    Реферальная система (HTML + Premium Emoji)
    """
    ref_link = f"https://t.me/pavlik_vpn_bot?start={callback.from_user.id}"
    await callback.message.edit_text(
        f'<tg-emoji emoji-id=\"5258513401784573443\">👥</tg-emoji> <b>Реферальная система</b>\n\n'
        f"Приглашайте друзей и получайте бонусные дни к подписке!\n\n"
        f"<tg-emoji emoji-id=\"5260730055880876557\">🔗</tg-emoji> Ваша ссылка:\n<code>{ref_link}</code>\n\n"
        f"<i>(Система зачисления бонусов проходит финальную настройку...)</i>",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
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
    Выбор тарифа (HTML + Premium Emoji)
    """
    await callback.message.edit_text(
        f'<tg-emoji emoji-id=\"5258389041006518073\">📦</tg-emoji> <b>Выберите тариф:</b>\n\n'
        f"• Безлимит устройств\n"
        f"• Без логов\n"
        f"• Поддержка 24/7",
        reply_markup=get_subscriptions_keyboard(),
        parse_mode="HTML"
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
                "<tg-emoji emoji-id=\"5260341314095947411\">✅</tg-emoji> **Оплата подтверждена автоматически!**\n\n"
                "Ваша подписка активирована. Ожидайте данные для подключения! <tg-emoji emoji-id=\"5260221883940347555\">🚀</tg-emoji>",
                reply_markup=get_back_keyboard(),
                parse_mode="Markdown"
            )
            return
        
        if status in ["CANCELED", "FAILED"]:
            async with session_maker() as session:
                await update_transaction_status(session, tx_id, status)
            
            await message.edit_text(
                f"<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> **Платеж был отклонен или отменен.**\nСтатус: {status}",
                reply_markup=get_back_keyboard(),
                parse_mode="Markdown"
            )
            return

@menu_router.callback_query(F.data.startswith("buy:"))
async def process_buy_tariff(callback: types.CallbackQuery, session: AsyncSession):
    """
    Процесс покупки тарифа и запуск авто-проверки
    """
    _, tariff_key, amount = callback.data.split(":")
    amount = float(amount)

    await callback.message.edit_text("<tg-emoji emoji-id=\"5199457120428249992\">⏳</tg-emoji> **Загрузка платежа...**", parse_mode="Markdown")

    tx = await create_transaction(session, callback.from_user.id, amount, tariff_key)
    description = f"Оплата VPN: {tariff_key}"
    payment_data = await platega.create_transaction(amount, description, str(tx.id))

    if not payment_data or "redirect" not in payment_data:
        await callback.message.edit_text(
            "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> **Ошибка при создании счета.**",
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
    days = {"month_1": "30", "month_3": "90", "month_6": "180", "month_12": "365"}.get(tariff_key, "30")

    await callback.message.edit_text(
        f"<tg-emoji emoji-id=\"5258204546391351475\">💳</tg-emoji> **Подтверждение покупки**\n\n"
        f"Срок: **{days} дней**\n"
        f"Устройств: **Безлимит**\n"
        f"Цена: **{amount}₽**\n\n"
        "Нажми кнопку ниже для оплаты.\n"
        "После оплаты бот **автоматически** увидит платеж в течение минуты! <tg-emoji emoji-id=\"5260221883940347555\">🚀</tg-emoji>",
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
            "<tg-emoji emoji-id=\"5260221883940347555\">✅</tg-emoji> **Оплата прошла успешно!**\n\n"
            "Ваша подписка активирована. В ближайшее время мы пришлем вам данные для подключения.",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
    elif status == "PENDING":
        await callback.answer("⏳ Платеж еще обрабатывается. Попробуйте через минуту.", show_alert=True)
    else:
        # Если статус изменился на какой-то другой (CANCELED, FAILED и т.д.)
        await update_transaction_status(session, tx_id, status)
        await callback.message.edit_text(
            f"<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> **Статус платежа изменился.**\n\n"
            f"Текущий статус: **{status}**\n"
            f"Если вы считаете, что это ошибка, обратитесь в поддержку.",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()

@menu_router.callback_query(F.data == "instructions")
async def show_instructions(callback: types.CallbackQuery):
    """
    Инструкция (Помощь)
    """
    await callback.message.edit_text(
        "<tg-emoji emoji-id=\"5307761176132720417\">❓</tg-emoji> **Помощь и инструкции**\n\n"
        "Здесь будет ваша инструкция по подключению через строку vless...",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@menu_router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, session: AsyncSession):
    """
    Возврат в главное меню
    """
    user = await session.get(User, callback.from_user.id)
    await callback.message.edit_text(
        f"<tg-emoji emoji-id=\"5258152182150077732\">⚡</tg-emoji> <b>Pavlik VPN — Ваш персональный ключ к свободе.</b>\n\n"
        f"Забудьте о границах в интернете. Мы обеспечиваем сверхбыстрое соединение, абсолютную анонимность и доступ к любому контенту в один клик.\n\n"
        f"<tg-emoji emoji-id=\"5260221883940347555\">🚀</tg-emoji> <b>Наши преимущества:</b>\n"
        f"  •  <b>Скорость:</b> До 1 Гбит/с без задержек.\n"
        f"  •  <b>Приватность:</b> Строгая политика No-Logs.\n"
        f"  •  <b>Простота:</b> Настройка за 30 секунд прямо в Telegram.\n\n"
        f"<i>Ваша безопасность — наша работа. Подключайтесь и летайте!</i>",
        reply_markup=get_main_menu_keyboard(user), # Передаем юзера
        parse_mode="HTML"
    )
    await callback.answer()

@menu_router.callback_query(F.data == "confirm_trial_request")
async def show_trial_confirmation(callback: types.CallbackQuery, session: AsyncSession):
    """
    Показывает окно подтверждения триала
    """
    user = await session.get(User, callback.from_user.id)
    if user.trial_used:
        await callback.answer("<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> Вы уже использовали пробный период!", show_alert=True)
        return

    # Рассчитываем дату окончания для текста
    end_date = (datetime.now() + timedelta(days=3)).strftime("%d.%m.%Y %H:%M")

    await callback.message.edit_text(
        f"🎁 <b>Активация пробного периода</b>\n\n"
        f"Вы собираетесь активировать бесплатный доступ на <b>3 дня</b>.\n"
        f"Он будет действовать до: <b>{end_date}</b>\n\n"
        f"⚠️ <b>Внимание:</b> Пробный период можно активировать только <b>один раз</b>.\n\n"
        f"💡 <i>После активации вы сможете следить за статусом в разделе:\n"
        f"Профиль -> Мои подписки</i>",
        reply_markup=get_trial_confirmation_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@menu_router.callback_query(F.data == "claim_trial")
async def claim_trial(callback: types.CallbackQuery, session: AsyncSession):
    """
    Финальная активация пробного периода
    """
    user = await session.get(User, callback.from_user.id)
    
    if user.trial_used:
        await callback.answer("<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> Вы уже использовали пробный период!", show_alert=True)
        return
        
    # Начисляем 3 дня
    now = datetime.now()
    if user.subscription_end and user.subscription_end > now:
        user.subscription_end += timedelta(days=3)
    else:
        user.subscription_end = now + timedelta(days=3)
        
    user.trial_used = True
    user.is_active = True
    await session.commit()
    
    await callback.message.edit_text(
        "<tg-emoji emoji-id=\"5260221883940347555\">✅</tg-emoji> <b>Пробный период успешно активирован!</b>\n\n"
        "Вам начислено <b>3 дня</b> бесплатного VPN.\n\n"
        "<tg-emoji emoji-id=\"5307761176132720417\">❓</tg-emoji> <i>Инструкция: теперь вы можете зайти в свой Профиль и увидеть "
        "актуальный срок действия подписки в подразделе «Мои подписки».</i>",
        reply_markup=get_main_menu_keyboard(user),
        parse_mode="HTML"
    )
    await callback.answer("<tg-emoji emoji-id=\"5260221883940347555\">✅</tg-emoji> Подписка активирована!", show_alert=True)
