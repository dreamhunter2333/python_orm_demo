import sqlite3

from typing import Any,
from collections import OrderedDict


db = sqlite3.connect('db.sqlite')


class Field(object):
    column_type = None
    format_type = '%s'
    format_str = '"{}"'

    def __init__(self, name, ) -> None:
        self.name = name

    def convert_to_param(self, record) -> Any:
        return record[self.name]


class Char(Field):
    column_type = 'varchar(100)'


class Int(Field):
    format_str = '{}'
    column_type = 'bigint'


class IdField(Field):
    column_type = 'integer primary key autoincrement'

    def __init__(self):
        super().__init__('id')


class MetaModel(type):

    def __new__(cls, name, bases, attrs):
        _all_fields = OrderedDict()
        for key, value in attrs.items():
            if isinstance(value, Field):
                _all_fields[key] = value
        attrs['_all_fields'] = _all_fields
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=MetaModel):
    _table = None

    id = IdField()

    def __getattr__(self, name: str) -> Any:
        if name in self._all_fields:
            return self[name]
        return super().__getattr__(name)

    def __init__(self, **kwargs) -> None:
        return super().__init__(**kwargs)

    @classmethod
    def init_table(cls):
        try:
            sql = 'DROP TABLE {}'.format(cls._table)
            db.execute(sql)
        except:
            pass

        sql = 'CREATE TABLE {} ({}) '.format(
            cls._table,
            ','.join([
                ' '.join([f.name, f.column_type])
                for f in cls._all_fields.values()
            ])
        )
        db.execute(sql)

    def save(self):
        sql = "insert into {} ({}) values ({})"
        all_fields = [f for f in self._all_fields.values() if f.name != 'id']
        sql = "insert into {} ({}) values ({})".format(
            self._table,
            ','.join([f.name for f in all_fields]),
            ','.join([f.format_str.format(self[f.name]) for f in all_fields]),
        )
        db.execute(sql)


class User(Model):

    _table = 'user'

    name = Char('name')
    number = Int('number')



User.init_table()
User(name="1", number=22).save()
db.commit()
db.close()
