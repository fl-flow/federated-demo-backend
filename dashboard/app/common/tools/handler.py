import requests


class RequestHandler:
    def __init__(self):
        self.session = requests.session()

    def request(self, method, url, params=None, data=None, json=None, headers=None, **kwargs):
        try:
            return self.session.request(method,url, params=params, data=data, json=json, headers=headers,**kwargs)
        except:
            pass
        finally:
            self.close_session()

    def close_session(self):
        """关闭session"""
        self.session.close()
