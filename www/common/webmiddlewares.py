
import asyncio, os, json, logging
from aiohttp import web
from utils.helper import jsonConverter
from utils.jwtUtil import validate_token
from common.apis import Constant
from common.httphandler import _RESPONSE_STATUSES


@asyncio.coroutine
async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request: %s %s' % (request.method, request.path))
        # await asyncio.sleep(0.3)
        return (await handler(request))
    return logger

@asyncio.coroutine
async def data_factory(app, handler):
    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                logging.info('request json: %s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = await request.post()
                logging.info('request form: %s' % str(request.__data__))
        return (await handler(request))
    return parse_data

@asyncio.coroutine
async def auth_factory(app, handler):
    async def is_auth(request):
        try:
            """ 判断路由 验证登录 """
            login_router_list = ['/login']#跳过验证的路由
            if request.path in login_router_list:
                return await handler(request)
            else:
                token = request.headers.get('Authorization')
                if token and token.startswith('Bearer'):
                    token = token[7:]
                else:
                    token = request.rel_url.query.get('token')

                if not token:
                    token = request.headers.get('token')

                request.verified = False
                if token:
                    """ 验证Token """
                    payload = validate_token(token)
                    code = payload[0]   #状态
                    msg = payload[1]    #数据
                    if code == 1:
                        request.verified = True
                        request.__token__ = msg
                        """ 验证权限 """
                        # TODO

                    else:
                        r = dict(data=None, message= msg, status = code, code = _RESPONSE_STATUSES[401] )
                        resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=None, cls = jsonConverter).encode('utf-8'),)
                        resp.content_type = 'application/json;charset=utf-8'
                        return resp
                else:
                    payload = {}
                    raise web.HTTPUnauthorized()

            return await handler(request)
        except Exception as ex:
            logging.error('验证token失败%s'%ex)
            raise web.HTTPUnauthorized()

    return is_auth

@asyncio.coroutine
async def response_factory(app, handler):
    async def response(request):
        try:
            logging.info('Response handler...')
            r = await handler(request)
            if isinstance(r, web.StreamResponse):
                return r
            if isinstance(r, bytes):
                resp = web.Response(body=r)
                resp.content_type = 'application/octet-stream'
                return resp
            if isinstance(r, str):
                if r.startswith('redirect:'):
                    return web.HTTPFound(r[9:])
                resp = web.Response(body=r.encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
            if isinstance(r, dict):
                template = r.get('__template__')
                if template is None:
                    resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=None, cls = jsonConverter).encode('utf-8'),)
                    resp.content_type = 'application/json;charset=utf-8'
                    return resp
                else:
                    resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                    resp.content_type = 'text/html;charset=utf-8'
                    return resp
            if isinstance(r, int) and r >= 100 and r < 600:
                return web.Response(r)
            if isinstance(r, tuple) and len(r) == 2:
                t, m = r
                if isinstance(t, int) and t >= 100 and t < 600:
                    return web.Response(t, str(m))
            # default:
            resp = web.Response(body=str(r).encode('utf-8'))
            resp.content_type = 'text/plain;charset=utf-8'
            return resp
        except Exception as ex:
            logging.error('响应失败：'%( ex))
    return response
