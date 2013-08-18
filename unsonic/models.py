from __future__ import print_function

import transaction, datetime, argparse
from argparse import Namespace

import sqlalchemy
from sqlalchemy import (engine_from_config, Column, Integer, Text, ForeignKey,
                        event)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relation
from sqlalchemy.orm.exc import NoResultFound
from zope.sqlalchemy import ZopeTransactionExtension

import mishmash.orm
from mishmash.orm import OrmObject, Artist, Album, Meta, Label, Track
from mishmash.orm import TYPES as MASH_TYPES

from .moduleref import ModuleRef


DBSession = ModuleRef()
Base = mishmash.orm.Base


@sqlalchemy.event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in DBSession.get_bind().driver:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


### DB models
class User(Base, OrmObject):
    __tablename__ = 'un_users'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    password = Column(Text)
    roles = relation("Role", cascade="all, delete-orphan",
                      passive_deletes=True)
    playlists = relation("PlayList", cascade="all, delete-orphan",
                         passive_deletes=True)

    def export(self):
        ret = argparse.Namespace()
        ret.id = self.id
        ret.name = self.name
        ret.password = self.password
        ret.roles = []
        for role in self.roles:
            ret.roles.append(role.name)
        def isAdmin():
            return Roles.ADMIN in ret.roles
        ret.isAdmin = isAdmin
        def isUser():
            return Roles.USERS in ret.roles
        ret.isUser = isUser
        def isRest():
            return Roles.REST in ret.roles
        ret.isRest = isRest
        return ret


class Roles(object):
    ADMIN = "admin"
    USERS = "users"
    REST = "rest"

class Role(Base, OrmObject):
    __tablename__ = 'un_roles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("un_users.id", ondelete='CASCADE'),
                     nullable=False)
    name = Column(Text)
    user = relation("User")


class PlayList(Base, OrmObject):
    __tablename__ = 'un_playlists'
        
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("un_users.id", ondelete='CASCADE'),
                      nullable=False)
    name = Column(Text)
    comment = Column(Text)
    public = Column(Integer, default=0)
    created = sqlalchemy.Column(sqlalchemy.DateTime(), nullable=False,
                         default=datetime.datetime.now)
    users = relation("PlayListUser", cascade="all, delete-orphan",
                     passive_deletes=True)
    tracks = relation("PlayListTrack", cascade="all, delete-orphan",
                      passive_deletes=True)
    owner = relation("User")


class PlayListUser(Base, OrmObject):
    __tablename__ = 'un_playlistusers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("un_users.id"), nullable=False)
    playlist_id = Column(Integer, ForeignKey("un_playlists.id",
                                             ondelete='CASCADE'),
                         nullable=False)
    playlist = relation("PlayList")
    user = relation("User")


class PlayListTrack(Base, OrmObject):
    __tablename__ = 'un_playlisttracks'

    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    playlist_id = Column(Integer, ForeignKey("un_playlists.id",
                                             ondelete='CASCADE'),
                         nullable=False)
    track = relation("Track")
    playlist = relation("PlayList")


# Modify the Track to include a relation to PlayListTrack
Track.playlist = relation("PlayListTrack")
    

### Utility functions
def init(settings, webapp):
    engine = engine_from_config(settings, 'sqlalchemy.')
    # Prevent fighting over the transaction model
    # FIXME maybe make transaction control optional in mishmash?
    if webapp:
        DBSession.__setobj__(scoped_session(sessionmaker(
            extension=ZopeTransactionExtension())))
    else:
        DBSession.__setobj__(scoped_session(sessionmaker(autocommit=True,
                                                         autoflush=False)))
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

def initDB(settings):
    from . import mash
    Base.metadata.create_all()
    with DBSession.begin():
        for table in MASH_TYPES:
            table.initTable(DBSession)
    addUser("admin", None, [Roles.REST, Roles.USERS, Roles.ADMIN])

def addUser(username, password, roles):
    try:
        with DBSession.begin():
            user = User(name=username, password=password)
            DBSession.add(user)
            DBSession.flush()
            for name in roles:
                role = Role(name=name, user_id=user.id)
                DBSession.add(role)
    except IntegrityError:
        return "Failed to add user. User already exists."
    return True

def delUser(username):
    DBSession.query(User).filter(User.name == username).delete()

def getUserByName(username):
    try:
        return DBSession.query(User).filter(User.name == username).one()
    except NoResultFound:
        return None

def getUserByID(id):
    try:
        return DBSession.query(User).filter(User.id == id).one()
    except NoResultFound:
        return None
