from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from redis import Redis, ConnectionPool
from dashboard.app.core.config import settings



SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
        settings.MYSQL_USER, settings.MYSQL_PWD, settings.MYSQL_HOST, settings.MYSQL_PORT, settings.MYSQL_DB)
engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, pool_size=150, max_overflow=50, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# db
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_local():
    return scoped_session(SessionLocal)


#redis连接
class Cache:

    _client = None

    @classmethod
    def client(cls):
        """
        单例模式获取连接
        """
        if cls._client:
            return cls._client
        else:
            pool = ConnectionPool(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT,
                                  db=settings.REDIS_DB)
            cls._client = Redis(connection_pool=pool, decode_responses=True)
        return cls._client


class HCache:

    _client = None

    @classmethod
    def client(cls):
        """
        单例模式获取连接
        """
        if cls._client:
            return cls._client
        else:
            pool = ConnectionPool(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT,
                                  db=15,
                                  decode_responses=True)

            cls._client = Redis(connection_pool=pool)
        return cls._client



hcache = HCache().client()

cache = Cache().client()
# 设置默认时间
# cache.expire(cache_key, time(单位秒))
# cache.set(cache_key, value, time(时间秒))


