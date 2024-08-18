import yookassa
from yookassa import Payment
import uuid
from config_data.config import Config, load_config

config: Config = load_config()
yookassa.Configuration.account_id = config.tg_bot.yookassa_id
yookassa.Configuration.secret_key = config.tg_bot.yookassa_key


def create_payment(amount: str, chat_id: int):
    id_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "paymnet_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/meetuprus_bot"
        },
        "capture": True,
        "meta_data": {
            "chat_id": chat_id
        },
        "description": 'Стоимость выполнения заявки...'
    }, id_key)
    return payment.confirmation.confirmation_url, payment.id


def check_payment(payment_id: str):
    payment = yookassa.Payment.find_one(payment_id)
    return payment.status
