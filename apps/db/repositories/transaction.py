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

async def update_transaction_status(
    session: AsyncSession, 
    transaction_id: int, 
    status: str
):
    """
    Обновляет статус транзакции
    """
    transaction = await session.get(Transaction, transaction_id)
    if transaction:
        transaction.status = status
        await session.commit()

async def get_transaction(session: AsyncSession, transaction_id: int) -> Transaction:
    return await session.get(Transaction, transaction_id)
