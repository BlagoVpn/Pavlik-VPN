import logging
from aiohttp import web
from sqlalchemy import select
from apps.db.database import async_session
from apps.db.models.transaction import Transaction
from apps.db.repositories.transaction import update_transaction_status

logger = logging.getLogger(__name__)


async def platega_webhook(request: web.Request) -> web.Response:
    """
    Принимает POST-уведомления от Platega об изменении статуса транзакции.
    Должен вернуть 200 OK иначе Platega будет повторять попытки.
    """
    try:
        data = await request.json()
    except Exception:
        logger.warning("Platega webhook: не удалось распарсить JSON")
        return web.Response(status=400)

    logger.info(f"Platega webhook received: {data}")

    transaction_id = data.get("transactionId") or data.get("id")
    status = data.get("status", "").upper()

    if not transaction_id or not status:
        logger.warning(f"Platega webhook: отсутствует transactionId или status: {data}")
        return web.Response(status=200)

    try:
        async with async_session() as session:
            result = await session.execute(
                select(Transaction).where(Transaction.external_id == str(transaction_id))
            )
            tx = result.scalar_one_or_none()

            if not tx:
                logger.warning(f"Platega webhook: транзакция не найдена external_id={transaction_id}")
                return web.Response(status=200)

            if status == "CONFIRMED" and tx.status != "CONFIRMED":
                from bot.handlers.menu import _activate_subscription_after_payment
                await _activate_subscription_after_payment(session, tx.id)
                logger.info(f"Platega webhook: подписка активирована tx={tx.id}")
            elif status in ("CANCELED", "FAILED", "EXPIRED") and tx.status == "PENDING":
                await update_transaction_status(session, tx.id, status)
                logger.info(f"Platega webhook: транзакция tx={tx.id} → {status}")

    except Exception as e:
        logger.error(f"Platega webhook: ошибка обработки: {e}", exc_info=True)

    return web.Response(status=200)


def create_webhook_app() -> web.Application:
    app = web.Application()
    app.router.add_post("/platega-webhook", platega_webhook)
    return app
