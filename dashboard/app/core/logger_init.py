import sys
import time
from loguru import logger
from dashboard.app.core.config import settings
from dashboard.app.core.es_init import ElasticObj

es = ElasticObj(settings.INDEX_NAME, settings.INDEX_TYPE, settings.ES_IP, settings.ES_PORT)
#log和es
def init_logger():
    logger.remove(handler_id=None)
    if settings.LOG_ENABLED and settings.LOG_TO_CONSOLE:
        logger.add(sys.stderr, level=settings.LEVEL)
    if settings.LOG_ENABLED and settings.LOG_TO_FILE:
        logger.add(settings.LOG_PATH, rotation=settings.ROTATION, level=settings.LEVEL,
                   enqueue=True, compression=settings.COMPRESSION, retention=settings.RETENTION)
    if settings.LOG_ENABLED and settings.LOG_TO_ES:
        # 转成utc时间
        def to_utcTime(orginal_time):
            e_time = time.strptime(orginal_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
            time_stamp = time.mktime(e_time)
            utc_time_stamp = time_stamp - 8 * 60 * 60
            time_array = time.localtime(utc_time_stamp)
            utc_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
            return utc_time
        def my_sink(message):
            record = message.record
            utc_time = to_utcTime(record['time'])
            data = {
                    "module": record['file'].name,
                    "file_path": record['file'].path,
                    "function": record['function'],
                    "timestamp": utc_time,
                    "message": record['message'],
                    "level": record['level'].name,
                    "line": record['line'],
                    "detail": str(message)
            }
            es.create_index_data(data)
            return
        try:
            logger.add(my_sink)
        except Exception as e:
            logger.debug(e)
            logger.debug("es启动故障")
            pass
    return
