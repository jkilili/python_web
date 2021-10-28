import redis
import logging, json
from utils.helper import bytes_to_str,jsonConverter
import config as conf

class RedisManage(object):
    def __init__(self, **kwargs):
        redis_conf = conf.configs['redis']
        self._redis = redis.from_url(url=redis_conf['url'])

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance'):
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def get_ping(self):
        try:
           return self._redis.ping()
        except TimeoutError as ex:
            logging.error('redis connection timeout')

    #获取长度
    def get_len(self, args):
            len_dict = dict()
            val = None
            if not isinstance(args, str):
                for key in args:
                    kind = self.get_kind(key)
                    if kind == 'hash':
                        val = self.redis.hlen(key)
                    elif kind == 'zset':
                        val = self.redis.zcard(key)
                    elif kind == 'list':
                        val = self.redis.llen(key)
                    elif kind == 'set':
                        val = self.redis.scard(key)
                    len_dict[key] = val
                return len_dict
            else:
                dict_len = self.get_len([args])
                return dict_len[args]

    def set_str(self,key,value):
            logging.info('redis string set str %s:%s'%(key,value))
            try:
                value = json.dumps(value, ensure_ascii=False, default=None, cls = jsonConverter).encode('utf-8')
                ss= self._redis.set(key,value )
                return ss
            except Exception as e:
                logging.error('redis string set str %s:%s error, reason:%s'%(key,value, e))

    def set_strx(key,value, time):
            logging.info('redis string set str %s:%s'%(key,value))
            try:
                value = json.dumps(value, ensure_ascii=False, default=None, cls = jsonConverter).encode('utf-8')
                return self._redis.setex(key, time, value)
            except Exception as e:
                logging.error('redis string set str %s:%s error, reason:%s'%(key,value, e))
                
    def get_str(self,key):
            logging.info('redis string get str %s'%(key))     
            try:
                return self._redis.get(key) if self._redis.exists(key) else ''
            except Exception as e:
                logging.error('redis string get str %s error, reason:%s'%(key, e))

    def  exists_str(self,key):
        logging.info('redis string exists str %s:%s'%(key))     
        try:
            return True if self._redis.exists(key) else False
        except Exception as e:
            logging.error('redis string exists str %s error, reason:%s'%(key, e))

     # 加list头部元素
    def set_lpush(self,key, value):
            logging.info('redis list set lpush %s:%s'%(key,value))
            try:
                value = json.dumps(value, ensure_ascii=False, default=None, cls = jsonConverter).encode('utf-8')
                self._redis.lpush(key,  value)
            except Exception as e:
                logging.error('redis list set lpush %s:%s error, reason:%s'%(key,value, e))

     # 加list尾部元素
    def set_rpush(self,key, value):
            logging.info('redis list set lpush %s:%s'%(key,value))
            try:
                value = json.dumps(value, ensure_ascii=False, default=None, cls = jsonConverter).encode('utf-8')
                self._redis.rpush(key,  value)
            except Exception as e:
                logging.error('redis list set lpush %s:%s error, reason:%s'%(key,value, e))

    # 删除list第一个元素              
    def remove_lpop(self,key):
            logging.info('redis list set lpop %s'%(key))
            try:
                self._redis.lpop(key)
            except Exception as e:
                logging.error('redis list set lpop %s error, reason:%s'%(key, e))


    # 删除list最后一个元素            
    def remove_rpop(self, key):
            logging.info('redis list get lrange value:%s'%(key))       
            try:
                return self._redis.rpop(key)
            except Exception as e:
                logging.error('redis list get lrange value:%s error, reason:%s'%(key,e))

    #返回集合key所有元素
    def get_zset(self, key):
            logging.info('redis zset get smembers value:%s'%(key))     
            try:
                return self._redis.smembers(key, start, end)
            except Exception as e:
                logging.error('redis zset get smembers value:%s error, reason:%s'%(key,e))

    def set_zset(self, key, value):
            logging.info('redis zset get sadd %s:%s'%(key))     
            try:
                value = json.dumps(value, ensure_ascii=False, default=None, cls = jsonConverter).encode('utf-8')
                return self._redis.sadd(key, value)
            except Exception as e:
                logging.error('redis zset get sadd %s:%s error, reason:%s'%(key,value, e))

    #返回集合key删除数据个数
    def remove_zset(self, key,):
            logging.info('redis zset get srem  %s'%(key))     
            try:
                return self._redis.srem(key)
            except Exception as e:
                logging.error('redis zset get srem %s error, reason:%s'%(key, e))

                
    #添加hash key
    def set_hash(self, key, id, value):
            logging.info('redis hash get hset %s:%s:%'%(key,id,value))     
            try:
                value = json.dumps(value, ensure_ascii=False, default=None, cls = jsonConverter).encode('utf-8')
                return self._redis.hset(key, id, value)
            except Exception as e:
                logging.error('redis hash get hset %s:%s:%s error, reason:%s'%(key,id,value, e))
    
    def get_hash(self, key, id):
            logging.info('redis hash get hget %s:%s'%(key, id))     
            try:
                return self._redis.hget(key, id)
            except Exception as e:
                logging.error('redis hash get hget %s:%s error, reason:%s'%(key,id, e))

    def set_hmset(self, key, **h):
            logging.info('redis hash get hmset %s:%s'%(key, h))     
            try:
                h = json.dumps(h, ensure_ascii=False, default=None, cls = jsonConverter).encode('utf-8')
                return self._redis.hmset(key, h)
            except Exception as e:
                logging.error('redis hash get hmset %s:%s error, reason:%s'%(key,h, e))

    def set_hexists(self, key, id):
            logging.info('redis hash get hexists %s:%s'%(key))     
            try:
                return self._redis.hexists(key, id)
            except Exception as e:
                logging.error('redis hash get hexists %s:%s error, reason:%s'%(key,id, e))
    #
    def remove_hash(self, key, id):
            logging.info('redis hash get hdel %s:%s'%(key, id))     
            try:
                return self._redis.hdel(key, id)
            except Exception as e:
                logging.error('redis hash get hdel %s:%s error, reason:%s'%(key,id, e))