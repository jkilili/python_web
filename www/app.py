
#import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time, base64
from datetime import datetime

from aiohttp import web

from jinja2 import Environment, FileSystemLoader
from log import Log,create_logger
 
import config as conf
import common.orm as orm
from common.webmiddlewares import logger_factory, data_factory,response_factory,auth_factory
from common.coroweb import add_routes, add_static
from cryptography import fernet

def init_jinja2(app, **kw):
    Log.info('init jinja2...')
    options = dict(
        autoescape = kw.get('autoescape', True),
        block_start_string = kw.get('block_start_string', '{%'),
        block_end_string = kw.get('block_end_string', '%}'),
        variable_start_string = kw.get('variable_start_string', '{{'),
        variable_end_string = kw.get('variable_end_string', '}}'),
        auto_reload = kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    Log.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env

def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)

def index(request):
    return web.Response(body=b'<h1>Hello</h1>',headers={'content-type':'text/html'})

@asyncio.coroutine
async def init(loop):
    try:
        create_logger()

        Log.info("server init...")
        db = conf.configs['db'];
        
        Log.info("init configs...")
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)

        await orm.create_pool(loop=loop, host=db['host'], port=db['port'], user=db['user'], password=db['password'], db= db['database'])
        app = web.Application(loop=loop, middlewares=[
            logger_factory, 
            data_factory,
            auth_factory, 
            response_factory, 
        ])
        init_jinja2(app, filters=dict(datetime=datetime_filter))
        add_routes(app, 'routers')
        add_static(app)
    
        url = 'localhost'
        port = 8050
        srv = await loop.create_server(app.make_handler(),url, port)
        Log.info("server started at http://"+url+":"+ str(port))
        return srv
    except Exception as ex:
            print('服务启动失败')
            print(ex) 

    #app = web.Application(loop=loop)
    #app.router.add_route('GET', '/', index)
    #srv = yield from loop.create_server(app.make_handler(), url, port)
    #logging.info("server started at http://"+url+":"+ str(port))
    #return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
