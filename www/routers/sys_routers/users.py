
import re, json, logging, asyncio
from common.coroweb import get, post,put, delete
from common.apis import APIResp, APIError,APIValueError,APIPermissionError
from models.sys import SysUsers

from services import UserServices as services

@get('/')
async def index(request):
    users = await SysUsers.findAll()
    return {
        '__template__': 'sys/users/index.html',
        'users': users
    }

@post('/login')
async def login(request):
    req = await request.json()
    if req is None or len(req) == 0:
        raise APIError('请求失败', '请求错误', '必填项不能为空')
    result = await services().dologin(req = request, name = req.get('user_name'), pwd = req.get('password'))
    return  APIResp(result)

@post('/logout')
async def logout(request):
    #删除seesion
    services().dologout()
    return  APIResp()

@get('/api/user')
async def user_page(request, *, page ='1', pagesize= 20):
    jsonstr = dict(request.query)
    if jsonstr is None:
        raise APIError('请求失败', '请求参数', '请求参数不能为空')
    user_name = jsonstr.get('user_name')
    if user_name and not user_name.strip():
        raise APIValueError('用户名','不能为空')

    page = jsonstr.get('page',1)
    pagesize = jsonstr.get('pagesize',20)
    
    jsonstr.pop('page')
    jsonstr.pop('pagesize')
    result = await services().get_page(page=page, pagesize= pagesize, ** jsonstr)
    return  APIResp(result)

@post('/api/user/list')
async def user_list(request):
    jsonstr = await request.json();
    if jsonstr is None or len(jsonstr) == 0:
        raise APIError('请求失败', '请求参数', '请求参数不能为空')
    result = await services().get_list(jsonstr)
    return  APIResp(result)

@post('/api/user')
async def user_add(request, *, user_name, password, re_password):
    req = await request.json()
    if req is None:
        raise APIError('请求失败', '请求参数', '请求参数不能为空')

    if not user_name or not user_name.strip():
        raise APIValueError('username', 'username cannot be empty')
    if password and not password.strip():
        raise APIValueError('密码','不能为空')
    if len(password) <= 6:
        raise APIValueError('密码','密码长度在6位以上')
    if re_password and not re_password.strip():
        raise APIValueError('确认密码','不能为空')
    if str(re_password) != str(password):
        raise APIValueError('确认密码','确认密码和密码不一致')
    if hasattr(req, 're_password'):
        req.pop('re_password')
    result = await services().add(**req)
    return  APIResp(result)

@put('/api/user/{id}')
async def user_edit(id, request):
    req = await request.json();
    if not req['user_name'] or not req['user_name'].strip():
        raise APIValueError('name', 'name cannot be empty')
    if hasattr(req, 'password'):
        req.pop('password')
    result = await services().edit(id, req)
    return  APIResp(result)

@get('/api/user/{id}')
async def user_detail(id):
    result = await services().get_detail(id)
    return  APIResp(result)

@delete('/api/user/{id}')
async def user_delete(id, request):
    result = await services().delete(id)
    return  APIResp(result)

@post('/api/user/delete')
async def user_delete_batch(request):
    ids = await request.text();
    result = await services().delete_batch(ids)
    return  APIResp(result)
