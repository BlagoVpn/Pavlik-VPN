from sqlalchemy import BigInteger, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from apps.db.models.base import Base
from datetime import datetime

class Transaction(Base):
    """
    Модель транзакции (платежа)
    Теория: Мы храним транзакции отдельно от юзеров для ведения логов
    и предотвращения дублирования платежей (идемпотентность).
    """
    __tablename__ = "transactions"

    # У каждой транзакции свой уникальный ID (автоинкремент)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Ссылаемся на пользователя через Telegram ID (Foreign Key)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    
    # Данные платежа
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="RUB")
    
    # Данные от Platega
    platega_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    
    # Какой тариф был выбран (например, 'month_1')
    tariff_key: Mapped[str] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f"<Transaction id={self.id} user_id={self.user_id} amount={self.amount}>"
