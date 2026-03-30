import aiohttp
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class PlategaService:
    """
    Бэкенд-сервис для работы с платежной системой Platega.io
    """
    def __init__(self, merchant_id: str, secret_key: str):
        self.merchant_id = merchant_id
        self.secret_key = secret_key
        self.base_url = "https://app.platega.io"
        
        # Заголовки для авторизации (из документации Platega)
        self.headers = {
            "X-MerchantId": self.merchant_id,
            "X-Secret": self.secret_key,
            "Content-Type": "application/json"
        }

    async def create_transaction(
        self, 
        amount: float, 
        description: str, 
        order_id: str,
        currency: str = "RUB",
        payment_method: int = 2  # 2 - СБП по умолчанию
    ) -> Optional[Dict[str, Any]]:
        """
        Создает транзакцию и возвращает ссылку на оплату
        """
        endpoint = f"{self.base_url}/transaction/process"
        
        payload = {
            "paymentMethod": payment_method,
            "paymentDetails": {
                "amount": amount,
                "currency": currency
            },
            "description": description,
            "payload": order_id # Передаем ID заказа, чтобы отследить его в коллбэке
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(endpoint, json=payload, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    
                    error_text = await response.text()
                    logger.error(f"Platega error: {response.status} - {error_text}")
                    return None
            except Exception as e:
                logger.error(f"Platega connection error: {e}")
                return None

    async def check_status(self, transaction_id: str) -> Optional[str]:
        """
        Проверяет статус транзакции по её ID
        Возвращает: 'CONFIRMED', 'PENDING', 'CANCELED' и др.
        """
        endpoint = f"{self.base_url}/transaction/{transaction_id}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(endpoint, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("status")
                    return None
            except Exception as e:
                logger.error(f"Platega status check error: {e}")
                return None
