from sqlalchemy.ext.asyncio import AsyncSession
from apps.db.models.transaction import Transaction

async def create_transaction(
    session: AsyncSession, 
    user_id: int, 
    amount: float, 
    tariff_key: str
) -> Transaction:
    """
    Создает запись о транзакции в базе
    """
    transaction = Transaction(
        user_id=user_id,
        amount=amount,
        tariff_key=tariff_key
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction

async def update_transaction_id(
    session: AsyncSession, 
    transaction_id: int, 
    platega_id: str
):
    """
    Обновляет ID транзакции от Platega
    """
    transaction = await session.get(Transaction, transaction_id)
    if transaction:
        transaction.platega_id = platega_id
        await session.commit()

from apps.db.models.user import User

async def update_transaction_status(
    session: AsyncSession, 
    transaction_id: int, 
    status: str
):
    """
    Обновляет статус транзакции и начисляет бонусы реферерам при успехе
    """
    transaction = await session.get(Transaction, transaction_id)
    if not transaction:
        return

    old_status = transaction.status
    transaction.status = status
    
    # Реферальные отчисления только при ПЕРВОМ переходе в CONFIRMED
    if status == "CONFIRMED" and old_status != "CONFIRMED":
        user = await session.get(User, transaction.user_id)
        if user and user.referred_by:
            # Один уровень: 20% от суммы
            ref1 = await session.get(User, user.referred_by)
            if ref1:
                commission1 = transaction.amount * 0.20
                ref1.referral_balance = (ref1.referral_balance or 0.0) + commission1
                ref1.total_earned = (ref1.total_earned or 0.0) + commission1

    await session.commit()

async def get_transaction(session: AsyncSession, transaction_id: int) -> Transaction:
    return await session.get(Transaction, transaction_id)
