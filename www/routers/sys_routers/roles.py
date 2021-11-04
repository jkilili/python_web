
import re, json, asyncio
from common.coroweb import get, post,put, delete
from common.apis import APIResp, APIError,APIValueError,APIPermissionError
from models.sys import SysRoles

from services import RoleServices as services
from log import Log

@get('/')
async def index(request):
    users = await SysUsers.findAll()
    return {
        '__template__': 'sys/users/index.html',
        'users': users
    }

@get('/api/role')
async def role_page(request, *, page ='1', pagesize= 20):
    jsonstr = dict(request.query)
    if jsonstr is None:
        raise APIError('请求失败', '请求参数', '请求参数不能为空')
    if jsonstr.get('name','') and not jsonstr['name'].strip():
        raise APIValueError('角色名称','不能为空')
    page = jsonstr.get('page',1)
    pagesize = jsonstr.get('pagesize',20)
    result = await services().get_page(page=page, pagesize= pagesize, name = jsonstr.get('name'))
    return  APIResp(result)

@post('/api/role/list')
async def role_list(request):
    jsonstr = await request.json();
    #if jsonstr is None:
        #raise APIError('请求失败', '请求参数', '请求参数不能为空')
    result = await services().get_list(name = jsonstr['name'])
    return  APIResp(result)

@post('/api/role')
async def role_add(request, *, name):
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty')
    result = await services().add(name)
    return  APIResp(result)

@put('/api/role/{id}')
async def role_edit(id, request):
    jsonstr = await request.json();
    if not jsonstr['name'] or not jsonstr['name'].strip():
        raise APIValueError('name', 'name cannot be empty')
    result = await services().edit(id, name= jsonstr['name'])
    return  APIResp(result)

@get('/api/role/{id}')
async def role_detail(id):
    result = await services().get_detail(id)
    return  APIResp(result)

@delete('/api/role/{id}')
async def role_delete(id, request):
    result = await services().delete(id)
    return  APIResp(result)

@post('/api/role/delete')
async def role_delete_batch(request):
    ids = await request.text();
    result = await services().delete_batch(ids)
    return  APIResp(result)
