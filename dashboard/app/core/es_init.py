from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from dashboard.app.core.config import settings

class ElasticObj:
    def __init__(self, index_name, index_type, ip=settings.ES_IP, port=9200):
        '''
        :param index_name: 索引名称
        :param index_type: 索引类型
        '''
        self.index_name = index_name
        self.index_type = index_type
        # 无用户名密码状态
        self.es = Elasticsearch([ip], port=port)
        # self.es.cluster.health(wait_for_status='yellow', request_timeout=1)
        #用户名密码状态
        # self.es = Elasticsearch([ip],http_auth=('elastic', 'password'),port=9200)

    def create_index(self, name=None):
        '''
        创建索引
        '''
        #创建映射
        _index_mappings = {
            "mappings": {
                # self.index_type: {
                    "properties": {
                        # "id": {
                        #     "type": "long",
                        #     "index": True,
                        # },
                        "function": {
                            "type": "text",
                            "index": True,
                        },
                        #文件名
                        "module": {
                            "type": "text",
                            "index": True,
                        },
                        "timestamp": {
                            "type": "date",
                            "index": True,
                            "format": "yyyy-MM-dd HH:mm:ss || yyyy-MM-dd || yyyy/MM/dd HH:mm:ss|| yyyy/MM/dd ||epoch_millis"
                        },
                        #信息
                        "message": {
                            "type": "text",
                            "index": True,
                        },
                        #详细信息
                        "detail": {
                            "type": "text",
                            "index": True,
                        },
                        #等级
                        "level": {
                            "type": "text",
                            "index": True,
                        },
                        #行数
                        "line": {
                            "type": "text",
                        },
                        #文件地址
                        "file_path": {
                            "type": "text",
                            "index": True,
                        }
                    }
                # }

            }
        }
        if not name:
            name = self.index_name+"_"+datetime.now().strftime("%Y-%m")
        if self.es.indices.exists(index=name) is not True:
            print(name,'name')
            res = self.es.indices.create(index=name, body=_index_mappings, request_timeout=50)
            return res['acknowledged']


    def create_index_data(self, message):
        '''
        数据存储到es
        :return:
        '''
        data_index_name = self.index_name+'_'+datetime.now().strftime("%Y-%m")
        now_date = datetime.now().strftime("%Y-%m")
        index_name = self.index_name + "_" + now_date
        if self.es.indices.exists(index=index_name) is not True:
            create_index = self.create_index(index_name)
            data_index_name = index_name
        if isinstance(message, dict):
            res = self.es.index(index=data_index_name, doc_type='_doc', body=message)
            return res['_shards']['successful']
        return False

    def search_all_data(self):
        body = {"query": {"match_all": {}}}
        hits_a = self.es.search(index = self.index_name, body = body)
        print(hits_a['hits']['hits'])
        return hits_a

    def bulk_index_data(self):
        '''
        用bulk将批量数据存储到es
        :return:
        '''
        list = [
            {"date": "2021-09-13",
             "source": "肯德基",
             "link": "www.baidu.com",
             "path": "快餐",
             "title": "肯德基很坑"
             },
            {"date": "2021-09-14",
             "source": "麦当劳",
             "link": "www.baidu.com",
             "path": "汉堡",
             "title": "麦当劳很贵"
             },
            {"date": "2021-09-15",
             "source": "汉堡王",
             "link": "www.baidu.com",
             "path": "披萨",
             "title": "汉堡王拉肚子"
             },
            {"date": "2021-09-116",
             "source": "德克士",
             "link": "www.baidu.com",
             "path": "烧烤",
             "title": "德克士没人吃"
             }
        ]
        ACTIONS = []
        i = 1
        for line in list:
            action = {
                "_index": self.index_name,
                "_type": self.index_type,
                "_id": i, #_id 也可以默认生成，不赋值
                "_source": {
                    "date": line['date'],
                    "source": line['source'].decode('utf8'),
                    "link": line['link'],
                    "path": line['path'].decode('utf8'),
                    "title": line['title'].decode('utf8')}
            }
            i += 1
            ACTIONS.append(action)
            # 批量处理
        success, _ = bulk(self.es, ACTIONS, index=self.index_name, raise_on_error=True)
        print('Performed %d actions' % success)

    def delete_index_data(self, id):
        '''
        删除索引中的一条
        :param id:
        :return:
        '''
        res = self.es.delete(index=self.index_name, doc_type=self.index_type, id=id)
        print(res)

    def get_data_id(self,id):

        res = self.es.get(index=self.index_name, doc_type=self.index_type,id=id)
        print(res['_source'])

        print('------------------------------------------------------------------')
        #
        # # 输出查询到的结果
        for hit in res['hits']['hits']:
            # print hit['_source']
            print(hit['_source']['date'],hit['_source']['source'],hit['_source']['link'],hit['_source']['keyword'],hit['_source']['title'])

    def get_data_by_body(self):
        # doc = {'query': {'match_all': {}}}
        doc = {
            "query": {
                "match": {
                    "keyword": "电视"
                }
            }
        }
        _searched = self.es.search(index=self.index_name, doc_type=self.index_type, body=doc)

        for hit in _searched['hits']['hits']:
            # print hit['_source']
            print(hit['_source']['date'], hit['_source']['source'], hit['_source']['link'], hit['_source']['keyword'], \
            hit['_source']['title'])
