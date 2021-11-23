
import re, json, asyncio
import aiohttp 
from common.coroweb import get, post,put, delete
from common.apis import APIResp, APIError,APIValueError,APIPermissionError
from common.apihttp import http_post
from models.sys import SysUsers

from services import UserServices as services
from log import Log
import config as conf


@post('/api/ali')
async def alicallback(request):
    try:
        resp = { "resp": "", "code": 1}
        req = await request.json()
        Log.info('阿里回调:%s'%req)
        if req is None or len(req) == 0:
            raise APIError('请求失败', '请求错误', '必填项不能为空')

        platforms = conf.configs['platforms'];
        if platforms is None:
            return;
        for platform in platforms:
            phone = platform.get('phone')
            url = platform.get('callback_url') 
            if url is not None:
                #根据路径转发信息
                resp = await http_post(url, req)
                Log.info('转发请求[%s]-[%s]-[%s]'%(phone,url,resp))
        
    except Exception as ex:
        Log.error('阿里回调失败:%s'%ex) 
    
    return resp;
        