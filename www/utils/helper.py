#helper.py

import json, datetime, hashlib

def bytes_to_str(s, encoding='utf-8'):
    """Returns a str if a bytes object is given."""
    if isinstance(s, bytes):
        return s.decode(encoding)
    return s

def gettime():
    return datetime.datetime.today()
    
def gettimestr():
    return (datetime.datetime.today()).strftime('%Y-%m-%d %H:%M:%S')

class sha1Util():
    def __init__(self, id, pwd):
        self.id = id
        self.pwd = pwd

    def encrypt(self):
        sha1_passwd = '%s:%s'%(self.id, self.pwd)
        sha1 = hashlib.sha1()
        sha1.update(self.id.encode('utf-8'))
        sha1.update(b':')
        sha1.update(self.pwd.encode('utf-8'))
        return sha1.hexdigest();



def check_json(myjson):
    try:
        jobj = json.loads(myjson)
    except :
        return False
    return True

class jsonConverter(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, bool):
            return str(obj).lower()
        elif isinstance(obj, (list, tuple)):
            return [convert(item) for item in obj]
        elif isinstance(obj, dict):
            return {convert(key):convert(value) for key, value in obj.items()}
        return json.JSONEncoder.default(self, obj)
