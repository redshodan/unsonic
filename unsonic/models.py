from __future__ import print_function

import transaction
from argparse import Namespace

import sqlalchemy
from sqlalchemy import (engine_from_config, Column, Integer, Text, ForeignKey,
                        event)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relation
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
users = {}


@sqlalchemy.event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in DBSession.get_bind().driver:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


### DB models

# Borrowed from mishmash
class OrmObject(object):
    @staticmethod
    def initTable(session):
        pass

    def __repr__(self):
        attrs = []
        for key in self.__dict__:
            if not key.startswith('_'):
                attrs.append((key, getattr(self, key)))
        return self.__class__.__name__ + '(' + ', '.join(x[0] + '=' +
                                            repr(x[1]) for x in attrs) + ')'

class MyModel(Base, OrmObject):
    __tablename__ = 'models'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    value = Column(Integer)


class User(Base, OrmObject):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    password = Column(Text)
    groups = relation("Group", cascade="all, delete-orphan",
                      passive_deletes=True)


class Group(Base, OrmObject):
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'),
                     nullable=False)
    user = relation("User")


### Utility functions
def init(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

def initModels():
    Base.metadata.create_all()
    with transaction.manager:
        ret = DBSession.query(MyModel).filter(MyModel.name == "one").all()
        if len(ret) == 0:
            model = MyModel(name='one', value=1)
            DBSession.add(model)

def loadData():
    for userdb in DBSession.query(User).all():
        groups = []
        for groupdb in userdb.groups:
            groups.append(groupdb.name)
        user = Namespace(name=userdb.name, password=userdb.password,
                         groups=groups)
        users[user.name] = user

def addUser(username, password, groups):
    with transaction.manager:
        try:
            user = User(name=username, password=password)
            DBSession.add(user)
            DBSession.flush()
            for name in groups:
                group = Group(name=name, user_id=user.id)
                DBSession.add(group)
        except IntegrityError:
            return "Failed to add user. User already exists."
        return True

def delUser(username):
    with transaction.manager:
        DBSession.query(User).filter(User.name == username).delete()
