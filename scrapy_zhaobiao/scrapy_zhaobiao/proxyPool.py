import redis
import requests
import time

class proxyPool():
    #链接Redis
    def __init__(self):
        self.redis_conn = redis.StrictRedis(
            host='localhost',
            port=6379,
            # password=''
            decode_responses=True,
        )
        print('成功链接Redis代理IP池')
    
    #将代理IP加入Redis
    def set_proxy(self):
        proxy_odd = None
        proxy_api = str(input('请输入代理池api：'))
        #更新代理IP地址
        while True:
            proxy_new = requests.get(proxy_api).decode('utf-8').strip().split(' ')
            if proxy_odd != proxy_new:
                proxy_odd = proxy_new
                self.redis_conn.delete('proxy')
                self.redis_conn.sadd('proxy',*proxy_new)
                print('change proxy:',proxy_new)
            else:
                time.sleep(1)
    
    #从Redis中获得代理IP
    def get_proxy(self):
        proxy_s = self.redis_conn.srandmember('proxy',1)
        #避免多线程代理IP取用出错
        if proxy_s:
            return proxy_s[0]
        else:
            time.sleep(0.1)
            return self.get_proxy()

if __name__ == "__main__":
    proxyPool().set_proxy()