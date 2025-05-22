import asyncio
import random
import bcrypt

import smtplib
from email.mime.text import MIMEText
import logging

from src.core.celery_config import celery
from src.core.config import load_config
from src.core.redis_initializer import get_redis

logger = logging.getLogger(__name__)
config = load_config()


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password_to_check: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password_to_check.encode('utf-8'), password_hash.encode('utf-8'))


def create_verification_code() -> int:
    """
    simple verification code creator
    :return:
    """
    return random.randint(100_000, 999_999)


@celery.task
def send_verification_code(
        email: str,
) -> int:
    """
    creating code, save it to redis, call smtp sender function
    :param email: validated user email
    :return: verification code
    """
    redis = get_redis()
    code_to_user = create_verification_code()
    # imitate sms
    try:
        redis.setex(
            name=email,
            time=config.verification_code_time_expiration,
            value=code_to_user
        )
        send_verification_code_by_smtp(
            email=email,
            auth_code=code_to_user
        )
        logger.info(f"Successfully sent verification code {code_to_user} to {email}")
        return code_to_user
    except Exception:
        logger.exception("Failed to send verification code")


def send_verification_code_by_smtp(email: str, auth_code: int) -> None:
    """
    отправляет код по email

    :param auth_code: 6-digits code
    :param email: user validated email
    :return:
    """
    # Создаем email-сообщение
    msg = MIMEText(f"Ваш код подтверждения: {auth_code}")
    msg["Subject"] = "Код подтверждения"
    msg["From"] = config.smtp.SMTP_USER
    msg["To"] = email
    logger.info("Я начал отправку по email!")
    # Отправляем email
    try:
        with smtplib.SMTP(
                config.smtp.SMTP_SERVER,
                config.smtp.SMTP_PORT
        ) as server:
            server.starttls()
            server.login(config.smtp.SMTP_USER, config.smtp.SMTP_PASSWORD)
            server.sendmail(config.smtp.SMTP_USER, email, msg.as_string())
        logger.info("Отправил код по email")
    except Exception:
        logger.exception("Error while sending verification code")
