from functools import lru_cache
from dashboard.app.core.logger_init import init_logger
from dashboard.app.core.es_init import ElasticObj
from dashboard.app.core.config import settings

def init_log():
    init_logger()
init_log()

try:
    if settings.LOG_TO_ES:
        def es_log():
            es = ElasticObj(settings.INDEX_NAME, settings.INDEX_TYPE, settings.ES_IP, settings.ES_PORT)
            es.create_index()
        es_log()
except Exception as e:
    print("es启动故障")
