import asyncio
import logging,datetime

import aiomysql

def log(sql, args=()):
    logging.info('SQL: %s' % sql)

async def create_pool(loop, **kw):

    logging.info('create database connection pool ...')
    global __pool
    __pool = await aiomysql.create_pool(host = kw.get('host','localhost'),
        port = kw.get('port', 3306),
        user = kw['user'],
        password=kw['password'],
        db = kw['db'],
        charset = kw.get('charset', 'utf8'),
        autocommit = kw.get('autocommit', True),
        maxsize = kw.get('maxsize',10),
        minsize = kw.get('minsize',1),
        loop = loop)

async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    async with __pool.get() as conn:
        try:
            cur = await conn.cursor(aiomysql.DictCursor)
            if sql.find('?') > 0:
                sql = sql.replace('?', '%s')
                await cur.execute(sql, args or ())
            else:
                await cur.execute(sql)
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
            logging.info('rows returned:%s' % len(rs))
        except BaseException as e:
            raise
        finally:
            conn.close()
        logging.info('rows returned: %s' % len(rs))
        return rs

async def execute(sql, args, autocommit=True):
    log(sql)
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        finally:
            conn.close()
        return affected

def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)

def resultConverter(ret, kw):
    try:
        if isinstance(kw, list):
            for k in kw:
                if isinstance( k.__mappings__, dict):
                     for r,v in k.__mappings__.items():
                         if isinstance(v, BooleanField) and not str(k[r]).isdigit():
                             k[r] = ord(k[r])
                         if isinstance(v,datetime.datetime ):
                             kw[r] = (kw[r]).replace('T','')
        if isinstance(kw, Model):
                if isinstance( kw.__mappings__, dict):
                     for r,v in kw.__mappings__.items():
                         if isinstance(v, BooleanField) and not str(kw[r]).isdigit():
                             kw[r] = ord(kw[r])
                         if isinstance(v,datetime.datetime ):
                             kw[r] = (kw[r]).replace('T','')
    except Exception as ex:
        logging.info('resultConverter error:%s'%ex)
    return kw
            
def _gen_sql(table_name, mappings):
    """
    类 ==> 表时 生成创建表的sql
    """
    pk = None
    sql = ['-- generating SQL for %s:' % table_name, 'create table `%s` (' % table_name]
    for f in sorted(mappings.values(), lambda x, y: cmp(x._order, y._order)):
        if not hasattr(f, 'ddl'):
            raise StandardError('no ddl in field "%s".' % f)
        ddl = f.ddl
        nullable = f.nullable
        if f.primary_key:
            pk = f.name
        #sql.append(nullable and '  `%s` %s,' % (f.name, ddl) or '  `%s` %s not null,' % (f.name, ddl))
        sql.append('  `%s` %s,' % (f.name, ddl) if nullable else '  `%s` %s not null,' % (f.name, ddl))
    sql.append('  primary key(`%s`)' % pk)
    sql.append(');')
    return '\n'.join(sql)

class Field(object):
    
    _count = 0

    def __init__(self, **kw):
        self.name = kw.get('name', None)
        self._default = kw.get('default', None)
        self.primary_key = kw.get('primary_key', False)
        self.nullable = kw.get('nullable', False)
        self.updatable = kw.get('updatable', True)
        self.insertable = kw.get('insertable', True)
        self.ddl = kw.get('ddl', '')
        self._order = Field._count
        Field._count += 1

    def __str__(self):
        #return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)
        s = ['<%s:%s,%s,default(%s),' % (self.__class__.__name__, self.name, self.ddl, self._default)]
        self.nullable and s.append('N')
        self.updatable and s.append('U')
        self.insertable and s.append('I')
        s.append('>')
        return ''.join(s)

class StringField(Field):
    """
    保存String类型字段的属性
    """
    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = ''
        if 'ddl' not in kw:
            kw['ddl'] = 'varchar(255)'
        super(StringField, self).__init__(**kw)

class IntegerField(Field):
    """
    保存Integer类型字段的属性
    """
    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = 0
        if 'ddl' not in kw:
            kw['ddl'] = 'bigint'
        super(IntegerField, self).__init__(**kw)

class FloatField(Field):
    """
    保存Float类型字段的属性
    """
    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = 0.0
        if 'ddl' not in kw:
            kw['ddl'] = 'real'
        super(FloatField, self).__init__(**kw)

class BooleanField(Field):
    """
    保存BooleanField类型字段的属性
    """
    def __init__(self, **kw):
        if not 'default' in kw:
            kw['default'] = False
        if not 'ddl' in kw:
            kw['ddl'] = 'bool'
        super(BooleanField, self).__init__(**kw)

class TextField(Field):
    """
    保存Text类型字段的属性
    """
    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = ''
        if 'ddl' not in kw:
            kw['ddl'] = 'text'
        super(TextField, self).__init__(**kw)


class BlobField(Field):
    """
    保存Blob类型字段的属性
    """
    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = ''
        if 'ddl' not in kw:
            kw['ddl'] = 'blob'
        super(BlobField, self).__init__(**kw)


class VersionField(Field):
    """
    保存Version类型字段的属性
    """
    def __init__(self, name=None):
        super(VersionField, self).__init__(name=name, default=0, ddl='bigint')


class BytesField(Field):
    """
    保存BooleanField类型字段的属性
    """
    def __init__(self, **kw):
        if not 'default' in kw:
            kw['default'] = None
        if not 'ddl' in kw:
            kw['ddl'] = 'bytes'
        super(BytesField, self).__init__(**kw)

class DatetimeField(Field):
    """
    保存DateTime类型字段的属性
    """
    def __init__(self, name=None,updatable=None, default=None):
        super(DatetimeField, self).__init__(name=name, updatable = updatable, default = default, ddl='datetime')

class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, tableName))
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('  found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    # 找到主键:
                    if primaryKey:
                        raise StandardError('Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise StandardError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey # 主键属性名
        attrs['__fields__'] = fields # 除主键外的属性名
        #attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        #attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        #attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        #attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        #attrs['__delete__'] = 'delete from `%s` ' % (tableName)
        return type.__new__(cls, name, bases, attrs)

class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def get_self(self):
        return self

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value

    @classmethod
    async def get(cls, pk):
        """
        Get by primary key.
        """
        d = await select('select * from %s where %s=?' % (cls.__table__, cls.__primary_key__), [pk],1)
        return cls(**d[0]) if d else None

    @classmethod
    async def find_all(cls, where=None, args=None, **kw):
        ' find objects by where clause. '
        sql = ['select `%s`, %s from `%s`' % (cls.__primary_key__, ', '.join(['`%s`' % col for col in cls.__fields__] ), cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        ' find number by select and where. '
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    async def find_first(cls, where, args=None):
        """
        通过where语句进行条件查询，返回1个查询结果。如果有多个查询结果
        仅取第一个，如果没有结果，则返回None
        """
        d = await select('select * from %s %s' % (cls.__table__, where), args)
        return cls(**d[0]) if d else None

    @classmethod
    async def find_by(cls, where, *args):
        ' find object by primary key. '
        sql = ' select `%s` from `%s`  %s' % (','.join(['`%s`' % col for col in cls.__fields__]), cls.__table__, where)
        rs = await select( sql, args)
        if len(rs) == 0:
            return None
        return [cls(**r) for r in rs]

    @classmethod
    async def count_all(cls):
        """
        执行 select count(pk) from table语句，返回一个数值
        """
        rs = await select('select count(`%s`) _num_ from `%s`' % (cls.__primay_key__, cls.__table__), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    async def count(cls, where, args):
        """
        通过select count(pk) from table where ...语句进行查询， 返回一个数值
        """
        sql = ['select count(`%s`) _num_ from `%s` '% (cls.__primary_key__, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    async def insert(self, **kw):
        params = {}
        
        #赋值
        for k, v in kw.items():
            if not hasattr(self, k):
                setattr(self, k, v)
            if hasattr(self, k):
                self[k] = getattr(self, k)

        for k, v in self.__mappings__.items():
            if v.insertable:
                if not hasattr(self, k):
                    setattr(self, k, v._default)
                params[v.name] = getattr(self, k)
        await self._create(self.__table__, **params)
        return self
    
    async def _create(self, table, **kw):
        cols, args = zip(*kw.items())
        sql = 'insert into `%s` (%s) values (%s)' % (table, ','.join(['`%s`' % col for col in cols]), ','.join(['?' for i in range(len(cols))]))
        rows = await execute(sql, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)
        return rows

    async def update(self, **kw):
        #赋值
        for k, v in kw.items():
            if not hasattr(self, k):
                setattr(self, k, v)
            if hasattr(self, k):
                self[k] = getattr(self, k)

        L = []
        args = []
        for k, v in self.__mappings__.items():
            if v.updatable:
                if hasattr(self, k):
                    arg = getattr(self, k)
                else:
                    arg = v.default
                    setattr(self, k, arg)
                L.append('`%s`=?' % k)
                args.append(arg)
        pk = self.__primary_key__
        args.append(getattr(self, pk))
        rows = await execute('update `%s` set %s where %s=?' % (self.__table__, ','.join(L), pk), args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)
        return rows

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)

   #async def update(self):
   #    args = list(map(self.getValue, self.__fields__))
   #    args.append(self.getValue(self.__primary_key__))
   #    rows = await execute(self.__update__, args)
   #    if rows != 1:
   #        logging.warn('failed to update by primary key: affected rows: %s' % rows)
            
    async def remove(self):
        sql = ['delete from `%s` '%self.__table__]
        args = [self.getValue(self.__primary_key__)]
        sql.append('where')
        sql.append('`%s`=?' % (self.__primary_key__))
        rows = await execute(' '.join(sql), args)
        if rows != 1:
            logging.warn('failed to remove by primary key: affected rows: %s' % rows)

    @classmethod
    async def removelist(cls, where=None, args=None):
        sql = ['delete from `%s` '%cls.__table__]
        if where:
            sql.append('where')
            sql.append(where)
        else:
            s = []
            for num in range(len(args)):
                s.append('?')
                    
            if len(s) > 0:
                c = ','.join(s) 
                sql.append('where')
                sql.append('`%s` in (%s)'%(cls.__primary_key__,c))

        rows = await execute(' '.join(sql), args)
        if rows != 1:
            logging.warn('failed to remove by primary key: affected rows: %s' % rows)
        return rows