import logging
import os

import redis
from dotenv import load_dotenv

load_dotenv()
_redis_client = None
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = 0


def init_redis():
    global _redis_client
    _redis_client = redis.Redis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        db=REDIS_DB,
        decode_responses=True,
    )
    _redis_client.ping()
    logging.info("Redis connected")


def close_redis():
    global _redis_client
    if _redis_client:
        _redis_client.close()
        logging.warning("Redis disconnected")


def get_redis():
    global _redis_client
    if _redis_client is None:
        init_redis()
    return _redis_client
