import yookassa
from yookassa import Payment
import uuid
from config_data.config import Config, load_config

config: Config = load_config()
yookassa.Configuration.account_id = config.tg_bot.yookassa_id
yookassa.Configuration.secret_key = config.tg_bot.yookassa_key


def create_payment(amount: str, chat_id: int, content: str):
    id_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "capture": True,
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/meetuprus_bot"
        },
        "description": 'Стоимость выполнения заявки...',
        "meta_data": {
            "order_id": str(chat_id)
        },
        "receipt": {
            "customer": {
                "email": "email@yandex.ru"
            },
            "items": [
                {
                    "description": content,
                    "quantity": 1,
                    "amount": {
                        "value": amount,
                        "currency": "RUB"
                    },
                    "vat_code": 1
                },
            ]
        },
    }, id_key)
    return payment.confirmation.confirmation_url, payment.id


def check_payment(payment_id: str):
    payment = yookassa.Payment.find_one(payment_id)
    return payment.status
