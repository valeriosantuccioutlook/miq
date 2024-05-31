from redis import Redis

from app.settings import settings

# init Redis
redis: Redis = Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PSW
)
