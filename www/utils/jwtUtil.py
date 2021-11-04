#jwtUtil.py
import time
import jwt
from jwt import exceptions
from log import Log

def create_token(id, name):
    global SECRET_KEY
    token = jwtUtil.encode(id, name)
    return token

def validate_token(token):
    global SECRET_KEY
    result = jwtUtil.decode(token)
    return result

class jwtUtil():
    _key = '1da4ega2s25FS5yY2s3lbc'

    # headers
    _headers = {
        'alg': "HS256",  # 声明所使用的算法
        'type': "JWT"
    }

    """headers 中一些固定参数名称的意义"""
    # jku: 发送JWK的地址；最好用HTTPS来传输
    # jwk: 就是之前说的JWK
    # kid: jwk的ID编号
    # x5u: 指向一组X509公共证书的URL
    # x5c: X509证书链
    # x5t：X509证书的SHA-1指纹
    # x5t#S256: X509证书的SHA-256指纹
    # typ: 在原本未加密的JWT的基础上增加了 JOSE 和 JOSE+
    # JSON。JOSE序列化后文会说及。适用于JOSE标头的对象与此JWT混合的情况。
    # crit: 字符串数组，包含声明的名称，用作实现定义的扩展，必须由 this->JWT的解析器处理。不常见。
    
    """payload 中一些固定参数名称的意义, 同时可以在payload中自定义参数"""
    # iss 【issuer】发布者的url地址
    # sub 【subject】该JWT所面向的用户，用于处理特定应用，不是常用的字段
    # aud 【audience】接受者的url地址
    # exp 【expiration】 该jwt销毁的时间；unix时间戳
    # nbf 【not before】 该jwt的使用时间不能早于该时间；unix时间戳
    # iat 【issued at】 该jwt的发布时间；unix 时间戳
    # jti 【JWT ID】 该jwt的唯一ID编号
    # 调用jwt库,生成json web token

    @classmethod
    def encode(cls, id, name):
        try:
            token_dict = {
                'iat': time.time(),
                'exp': int(time.time() + 600),
                'data':{
                    'id' : id,
                    'name': name
                    }
                }

            jwt_token = jwt.encode(token_dict,  # payload, 有效载体
                                   cls._key,  # 进行加密签名的密钥
                               algorithm="HS256",  # 指明签名算法方式, 默认也是HS256
                               headers= cls._headers  # json web token 数据结构包含两部分, payload(有效载体), headers(标头)
                               )  # python3 编码后得到 bytes, 再进行解码(指明解码的格式), 得到一个str

            de_token = cls.decode(jwt_token)
            print(jwt_token)
            return jwt_token
        except Exception as e:
            Log.error('jwt encode error， %s ...' % e)

    @classmethod
    def decode(cls, jt):
        try:
            token = jwt.decode(jt, cls._key, algorithms = ['HS256'])
            return (1,token)
        except exceptions.ExpiredSignatureError as esx:
            Log.error('token已失效')
            return (2, 'token已失效')
        except jwt.DecodeError as dx:
            Log.error('token认证失败')
            return (2, 'token认证失败')
        except jwt.InvalidTokenError as tr: 
            Log.error('非法的token')
            return (2, '非法的token')

