#sys_api.py
import json,sys,datetime
from models.sys import SysUsers, next_id
from common.apis import Page, APIError, APIValueError, APIResourceNotFoundError,get_page_index
from utils.helper import gettime,sha1Util
from utils.jwtUtil import create_token, validate_token
from common.redis_manage import RedisManage
from storage import globalVal
from log import Log

class UserServices():

    @classmethod
    async def dologin(self, req, name, pwd):
        #q = ' and '.join(map(lambda f:'`%s`=?'%f, query))
        paswd = sha1Util(name, pwd).encrypt() 
        query = " where `is_deleted` = 0 and `user_name` = '%s' and  `password` = '%s' "%(name, paswd)
        data = await SysUsers.find_first(where=query)
        if data is None:
            raise APIError('登录失败','','用户名不存在')
        RedisManage().set_str(data['user_name'], data);
        globalVal.global_user = data;
        token = create_token(data['id'], data['user_name'])
        return token

    #@classmethod
    #def dologout(self, name):

    @classmethod
    async def get_page(self, page, pagesize, **query):
        #InfoLog(self.getname(self)).log()
        #参数拼接
        #批量拼接查询语句
        #q = ' and '.join(map(lambda f:'`%s`=?'%f, query))
        q=''
        name = query.get('user_name')
        if name and str(name).strip():
            q +=  ' `user_name` like ? '
            query['user_name'] = '%s%%'%(name)

        #参数对应值
        arg = list(map(lambda f: '%s'%query.get(f), query))  
        total = await SysUsers.count(where=q, args= arg)  
        page_index = get_page_index(page)
        p = Page(total, page_index)
        data = await SysUsers.find_all(where=q, args= arg, orderBy='create_time desc', limit=(p.offset, p.limit))
        return dict(page=page, pageSize = pagesize, total= total, rows= data)

    @classmethod
    async def get_detail(self, id):
        result = await SysUsers.get(id)  
        return result
    
    @classmethod
    async def get_list(self, **query):
        #参数拼接
        q = ' and '.join(map(lambda f:'`%s`=?'%f, query))
        #参数对应值
        arg = list(map(lambda f: '%s'%query.get(f), query))  
        result = await SysUsers.find_all(where=q, args=arg, orderBy='create_time desc')
        return result

    @classmethod
    async def add(self,**kw):
        user = await SysUsers.find_first(' where `user_name` = ? ',kw.get('user_name'))
        if user:
            raise APIError('注册用户失败', '', '用户名已经存在')

        data = SysUsers(id=next_id(), is_deleted = 0, creator='sys', create_name ='sys', password = sha1Util(kw.get('user_name'), kw.get('password')).encrypt() )
        if kw is None or len(kw) == 0:
            return None
        kw['password'] = data['password']
        await data.insert(**kw)
        data['password'] = '********'
        return data
            
    @classmethod
    async def edit(self, id,  **kw):
        data = await SysUsers.get(id)
        if data is None:
            raise APIValueError('id', 'id is not exists')
        await data.update(**kw)
        return data
        
    @classmethod
    async def delete(self, id):
        role = await SysUsers.get(id)
        if role is None:
            raise APIValueError('id', 'id is not exists')
        await role.remove()
        return role

    @classmethod
    async def delete_batch(self, ids):
        idarr = [ids]
        if ids.find(',') > 0:
            idarr = str(ids).split(',')

        rows = await SysUsers.removelist(args=idarr)
        return rows