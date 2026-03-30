from sqlalchemy import BigInteger, String, Boolean, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from apps.db.models.base import Base
from datetime import datetime
from typing import Optional

class User(Base):
    """
    Модель пользователя бота
    """
    __tablename__ = "users"

    # Telegram ID делаем основным ключом (PK)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    
    # Данные из телеграма
    username: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    
    # Поля VPN-сервиса
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Ссылка на VLESS (будем хранить её здесь после создания в панели)
    vless_link: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    # Реферальная система
    referred_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Использовал ли пробный период
    trial_used: Mapped[bool] = mapped_column(Boolean, default=False)

    # Реферальный доход (по умолчанию 0.0)
    referral_balance: Mapped[float] = mapped_column(Float, default=0.0)
    total_earned: Mapped[float] = mapped_column(Float, default=0.0)

    def __repr__(self) -> str:
        return f"<User user_id={self.user_id} full_name='{self.full_name}'>"
