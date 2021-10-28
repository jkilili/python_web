import datetime, uuid
from common.orm import Model, Field, StringField, BooleanField, FloatField, TextField,IntegerField,DatetimeField
from utils.helper import gettime

def next_id():
    return '%s'%(uuid.uuid4())

class SysResource(Model):
    __table__ = "sys_resource"
    id = StringField(name="resourceid", primary_key=True, default=next_id(), ddl='varchar(36)')
    applicationId = StringField( name="applicationid", ddl='varchar(36)') 
    uri = StringField( name="resourceid", ddl='varchar(256)') 
    name  = IntegerField(name="name", default = 1) 
    type  = StringField(name="type",ddl='varchar(512)') 
    parentid  = StringField(name="parentid",ddl='varchar(36)')
    path  = StringField(name="path",ddl='varchar(1024)') 
    Level = IntegerField(name="Level",default=0) 
    sort_num = IntegerField(name="sort_num",default=0) 
    extend  = StringField(name="extend",ddl='varchar(512)') 
    remark  = StringField(name="remark",ddl='varchar(512)') 
    is_deleted = IntegerField(name="is_deleted",default=0)
    creator = StringField(name="creator",updatable=False,ddl='varchar(36)')
    create_name  = StringField(name="create_name",updatable=False,ddl='varchar(64)') 
    create_time = DatetimeField(name="create_time",updatable=False,default=gettime())

class SysPermission(Model):
    __table__ = "sys_permission"
    id = StringField(name="permissionid", primary_key=True, default=next_id(), ddl='varchar(36)')
    roleId = StringField( name="roleId", ddl='varchar(36)') 
    resourceId = StringField( name="resourceid", ddl='varchar(36)') 
    isdeny  = IntegerField(name="is_deny", default = 1) 
    extend  = StringField(name="extend",ddl='varchar(512)') 
    remark  = StringField(name="remark",ddl='varchar(512)') 
    is_deleted = IntegerField(name="is_deleted",default=0)
    creator = StringField(name="creator",updatable=False,ddl='varchar(36)')
    create_name  = StringField(name="create_name",updatable=False,ddl='varchar(64)') 
    create_time = DatetimeField(name="create_time",updatable=False,default=gettime())

class SysApplication(Model):
    __table__ = "sys_application"
    id = StringField(name="applicationid", primary_key=True, default=next_id(), ddl='varchar(36)')
    code = StringField( name="code", ddl='varchar(64)') 
    name = StringField( name="name", ddl='varchar(256)') 
    register_enabled  = IntegerField(name="register_enabled", default = 1) 
    extend  = StringField(name="extend",ddl='varchar(512)') 
    is_deleted = IntegerField(name="is_deleted",default=0)
    remark  = StringField(name="remark",ddl='varchar(512)') 
    creator = StringField(name="creator",updatable=False,ddl='varchar(36)')
    create_name  = StringField(name="create_name",updatable=False,ddl='varchar(64)') 
    create_time = DatetimeField(name="create_time",updatable=False,default=gettime())
    #version = BytesField(name="version", dll='bytes')

class SysMenu(Model):
    __table__ = "sys_menu"
    id = StringField(name="id", primary_key=True, default=next_id(), ddl='varchar(36)')
    name = StringField( name="name", ddl='varchar(36)') 
    title  = StringField(name="title",ddl='varchar(128)') 
    group_name  = StringField(name="group_name",ddl='varchar(128)') 
    parent_id  = StringField(name="parent_id",ddl='varchar(128)')
    url  = StringField(name="url",ddl='varchar(128)')
    icon  = StringField(name="icon",ddl='varchar(128)')
    level = IntegerField(name="level", default = 1) 
    sort_num  = IntegerField(name="sort_num",default=0)
    is_deleted = IntegerField(name="is_deleted",default=0)
    remark  = StringField(name="remark",ddl='varchar(512)') 
    creator = StringField(name="creator",updatable=False,ddl='varchar(36)')
    create_name  = StringField(name="create_name",updatable=False,ddl='varchar(64)') 
    create_time = DatetimeField(name="create_time",updatable=False,default=gettime())

class SysUsers(Model):
    __table__ = "sys_users"
    id = StringField(name="id", primary_key=True, default=next_id(), ddl='varchar(36)')
    user_name = StringField(updatable = False, name="user_name", ddl='varchar(36)') 
    password  = StringField(name="password",ddl='varchar(128)') 
    email = StringField(name="email",ddl='varchar(50)') 
    usertype  = IntegerField(name="usertype",default=0)
    is_deleted = IntegerField(name="is_deleted",default=0)
    remark  = StringField(name="remark",ddl='varchar(512)') 
    creator = StringField(name="creator",updatable=False,ddl='varchar(36)')
    create_name  = StringField(name="create_name",updatable=False,ddl='varchar(64)') 
    create_time = DatetimeField(name="create_time",updatable=False,default=gettime())
    #version = BytesField(name="version", dll='bytes')

class SysRoles(Model):
    __table__ = "sys_roles"
    id = StringField(name="id", primary_key=True, default=next_id(), ddl='varchar(36)')
    name = StringField(name="name", ddl='varchar(36)') 
    is_deleted = IntegerField(name="is_deleted", default=0)
    remark  = StringField(name="remark", ddl='varchar(512)') 
    creator = StringField(name="creator", updatable=False,ddl='varchar(36)')
    create_name  = StringField(name="create_name", updatable=False,ddl='varchar(64)') 
    create_time = DatetimeField(name="create_time", updatable=False,default=gettime())
