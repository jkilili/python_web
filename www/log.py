
import json,sys,datetime
from storage import globalVal
from os import path
import sys
import logging
import logging.config
from utils import helper
import config as conf
import configparser

log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logger.conf')

#DebugLog = {}
#InfoLog = {}
#WarnLog = {}
#ErrorLog = {}
#SqlLog = {}

DebugLog = logging.getLogger('debug')
InfoLog = logging.getLogger('info')
WarnLog = logging.getLogger('warn')
ErrorLog = logging.getLogger('error')
SqlLog = logging.getLogger('sql')

""" 创建日志服务 """
def create_logger():
    logConf = conf.configs.get('log');
    basePath = './logs'
    fileConfigs = configparser.ConfigParser()
    fileConfigs.read(log_file_path, encoding='GB18030')

    if logConf:
        level = ['info','debug', 'error','warn','sql']
        base_path = logConf.get('base')
        for level_name in level:
            cur_path = logConf.get(level_name)
            if cur_path:
                cur_path = '%s/%s'%(basePath, cur_path) 
                helper.createFile(cur_path)
                _class = fileConfigs.get('handler_%sHanlder'%level_name,'class')
                if _class.find('File') > 0:
                    args = fileConfigs.get('handler_%sHanlder'%level_name,'args')
                    if args:
                        _args = fileConfigs.get('handler_%sHanlder'%level_name,'args')
                        #print('args', '', _args)
                        tupleArgs = list(eval(_args))
                        tupleArgs[0] = '%s/%s.log'%(cur_path, level_name)
                        strArg = str(tuple(tupleArgs))
                        fileConfigs.set('handler_%sHanlder'%level_name,'args', strArg)

    o = open(log_file_path, 'w')
    fileConfigs.write(o)
    o.close()
    logging.config.fileConfig(log_file_path)
    DebugLog = logging.getLogger('debug')
    InfoLog = logging.getLogger('info')
    WarnLog = logging.getLogger('warn')
    ErrorLog = logging.getLogger('error')
    SqlLog = logging.getLogger('sql')


class BaseLog():

    def __init__(self,  message=None, ex=None, *args, **kwargs):
        self.userName = ""
        self.userId =""
        if globalVal.global_user:
            self.userName = globalVal.global_user.get('user_name')
            self.userId = globalVal.global_user.get('id')
        self.message = message
        self.ex = ex

    def log(self, level, massage, code=None, ex=None):
        user_name = ""
        user_id = ""
        if globalVal.global_user:
            user_name = globalVal.global_user['user_name']
            user_id = globalVal.global_user['id']
        if level == "info" and InfoLog:
            InfoLog.info('%s %s'%(user_name, massage))
        if level == "error" and ErrorLog:
            ErrorLog.error('%s %s'%(user_name, massage))
        if level == "warn" and WarnLog:
            WarnLog.warning('%s %s'%(user_name, massage))
        if level == "debug" and DebugLog:
            DebugLog.debug('%s %s'%(user_name, massage))
        if level == "sql" and SqlLog:
            SqlLog.info('%s  %s'%(user_name, massage))
        if level == "db_info":
            #入库 
            #logging.error(self.getmessage(level))
            pass
        if level == "db_error":
            #入库 
            #logging.error(self.getmessage(level))
            pass


class Log(BaseLog):
    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)

    @classmethod
    def info(cls, message):
        cls.log(cls, 'info', message)

    @classmethod
    def error(cls, message):
        cls.log(cls, 'error', message)

    @classmethod
    def debug(cls, message):
        cls.log(cls, 'debug', message)
        
    @classmethod
    def warn(cls, message):
        cls.log(cls, 'warn', message)

    @classmethod
    def sql(cls, message):
        cls.log(cls, 'sql', message)

