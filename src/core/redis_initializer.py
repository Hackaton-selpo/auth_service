import redis.asyncio as redis
from dotenv import load_dotenv
import os
import logging

load_dotenv()
_redis_client = None
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = 0


async def init_redis():
    global _redis_client
    _redis_client = await redis.Redis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        db=REDIS_DB,
        decode_responses=True,
    )
    await _redis_client.ping()
    logging.info("Redis connected")


async def close_redis():
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        logging.warning("Redis disconnected")


async def get_redis():
    global _redis_client
    yield _redis_client
