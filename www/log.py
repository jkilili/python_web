
import json,logging,sys,datetime

class BaseLog():
    def __init__(self, name, message, user, *args, **kwargs):
        self.name = name
        self.user = user
        self.message = message
    def getmessage(self):
        self.message = '[%s]-[%s]-%s'%(datetime.datetime.now(), self.name, self.message)

    def log(self):
        logging.log(1, self.message)

class ErrorLog(BaseLog):
    def __init__(self, name,  message=None, user=None, *args, **kwargs):
        return super().__init__(name,  message, user, *args, **kwargs)
    def log(self):
        logging.error(self.__str__)

class InfoLog(BaseLog):
    def __init__(self, name, message=None, user=None, *args, **kwargs):
        return super().__init__(name, message, user, *args, **kwargs)
    def log(self):
        logging.info(self.message)
