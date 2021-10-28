#sys_api.py
import json,logging,sys,datetime
from models.sys import SysRoles, next_id
from common.apis import Page, APIValueError, APIResourceNotFoundError,get_page_index
from log import ErrorLog, InfoLog
from utils.helper import gettime 

class RoleServices():
    @classmethod
    async def get_page(self, page, pagesize,**query):
        try:
            #InfoLog(self.getname(self)).log()
            #参数拼接
            #批量拼接查询语句
            #q = ' and '.join(map(lambda f:'`%s`=?'%f, query))
            q=''
            name = query.get('name')
            if name and str(name).strip():
                query['name'] = '%s%%'%(name)
                q +=  ' `name` like ? '

            #参数对应值
            arg = list(map(lambda f: '%s'%query.get(f), query))  
            total = await SysRoles.count(where=q, args= arg)  
            page_index = get_page_index(page)
            p = Page(total, page_index)
            data = await SysRoles.find_all(where=q, args= arg, orderBy='create_time desc', limit=(p.offset, p.limit))
            return dict(page=page, pageSize = pagesize, total= total, rows= data)
        except Exception as ex:
            logging.info('get_page is error:%s'%ex)
            return dict(page=page, pageSize = pagesize, total= 0, rows= [])

    @classmethod
    async def get_detail(self, id):
        result = await SysRoles.get(id)  
        return result
    
    @classmethod
    async def get_list(self, **query):
        #参数拼接
        q = ' and '.join(map(lambda f:'`%s`=?'%f, query))
        #参数对应值
        arg = list(map(lambda f: '%s'%query.get(f), query))  
        result = await SysRoles.find_all(where=q, args=arg, orderBy='create_time desc')
        return result

    @classmethod
    async def add(self, **kw):
        data = SysRoles(id=next_id(),name=name, is_deleted = 0, creator='sys', create_name ='sys')
        
        for k, v in kw.items():
            if not hasattr(data, k):
                setattr(data, k, v)
            if hasattr(data, k):
                data[k] = getattr(data, k)

        await data.insert()
        return data

        
    @classmethod
    async def edit(self, id, **kw):
        data = await SysRoles.get(id)
        if data is None:
            raise APIValueError('id', 'id is not exists')
            
        for k, v in kw:
            if not hasattr(data, k):
                setattr(data, k, v)
            if hasattr(data, k):
                data[k] = getattr(data, k)

        await data.update()
        return data
        
    @classmethod
    async def delete(self, id):
        role = await SysRoles.get(id)
        if role is None:
            raise APIValueError('id', 'id is not exists')
        await role.remove()
        return role

    @classmethod
    async def delete_batch(self, ids):
        idarr = [ids]
        if ids.find(',') > 0:
            idarr = str(ids).split(',')

        rows = await SysRoles.removelist(args=idarr)
        return rows