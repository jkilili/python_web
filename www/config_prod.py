# config_prod.py

configs = {
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': 'Sxsh_2020',
        'database': 'py_db',
        "charset": 'utf8',
        "autocommit": True,
        "maxsize": 10,
        "minsize":1
    },
    'session': {
        'secretkey': '1d5e2Hke310m',
    },
    'redis':{
        'url':'redis://@127.0.0.1:6379/0',
        'host': '127.0.0.1',
        'port':'6379',
        'password':''
        },
    'log': {
        'base':'./logs',
        'info':'Info',
        'warn':'Warn',
        'error': 'Error',
        'debug':'Debug',
        'sql':'Sql'
        }
}