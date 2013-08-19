from __future__ import print_function

import transaction, datetime, argparse
from argparse import Namespace

import sqlalchemy
from sqlalchemy import (engine_from_config, Column, Integer, Text, ForeignKey,
                        String, DateTime, event)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relation
from sqlalchemy.orm.exc import NoResultFound
from zope.sqlalchemy import ZopeTransactionExtension

import mishmash.orm
from mishmash.orm import (Artist, Album, Meta, Label, Track, artist_labels,
                          album_labels, track_labels)
from mishmash.orm import TYPES as MASH_TYPES

from .moduleref import ModuleRef
from .version import DB_VERSION


DBSession = ModuleRef()
Base = mishmash.orm.Base
dbinfo = argparse.Namespace()


@sqlalchemy.event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in DBSession.get_bind().driver:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


### DB models
class OrmObject(mishmash.orm.OrmObject):
    @staticmethod
    def loadTable(session):
        pass


class DBInfo(Base, OrmObject):
    __tablename__ = 'un_dbinfo'

    version = Column(String(32), nullable=False, primary_key=True)
    last_sync = Column(DateTime)

    @staticmethod
    def initTable(session):
        session.add(DBInfo(version=DB_VERSION))

    @staticmethod
    def loadTable(session):
        dbinfo.version = None
        dbinfo.old_versions = []
        for dbi in session.query(DBInfo).order_by(DBInfo.version).all():
            if dbinfo.version is None:
                dbinfo.version = dbi.version
            else:
                dbinfo.old_versions.append(dbi.version)


class User(Base, OrmObject):
    __tablename__ = 'un_users'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    password = Column(Text)
    roles = relation("Role", cascade="all, delete-orphan",
                      passive_deletes=True)
    playlists = relation("PlayList", cascade="all, delete-orphan",
                         passive_deletes=True)

    @staticmethod
    def initTable(session):
        addUser("admin", None, [Roles.REST, Roles.USERS, Roles.ADMIN])
    
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


class ArtistRating(Base, OrmObject):
    __tablename__ = "un_artistratings"

    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False,
                       primary_key=True)
    user_id = Column(Integer, ForeignKey("un_users.id"), nullable=False,
                     primary_key=True)
    rating = Column(Integer, default=None, nullable=True)
    starred = Column(DateTime, default=None, nullable=True)
    artist = relation("Artist")
    user = relation("User")

    @staticmethod
    def get(artist_id, user_id):
        try:
            return DBSession.query(ArtistRating).\
              filter(ArtistRating.artist_id == artist_id,
                     ArtistRating.user_id == user_id).one()
        except NoResultFound:
            return None

Artist.rating = relation("ArtistRating")
    

class AlbumRating(Base, OrmObject):
    __tablename__ = "un_albumratings"
        
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False,
                      primary_key=True)
    user_id = Column(Integer, ForeignKey("un_users.id"), nullable=False,
                     primary_key=True)
    rating = Column(Integer, default=None, nullable=True)
    starred = Column(DateTime, default=None, nullable=True)
    album = relation("Album")
    user = relation("User")

    @staticmethod
    def get(album_id, user_id):
        try:
            return DBSession.query(AlbumRating).\
              filter(AlbumRating.album_id == album_id,
                     AlbumRating.user_id == user_id).one()
        except NoResultFound:
            return None

Album.rating = relation("AlbumRating")


class TrackRating(Base, OrmObject):
    __tablename__ = "un_trackratings"
    
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False,
                      primary_key=True)
    user_id = Column(Integer, ForeignKey("un_users.id"), nullable=False,
                     primary_key=True)
    rating = Column(Integer, default=None, nullable=True)
    starred = Column(DateTime, default=None, nullable=True)
    track = relation("Track")
    user = relation("User")

    @staticmethod
    def get(track_id, user_id):
        try:
            return DBSession.query(TrackRating).\
              filter(TrackRating.track_id == track_id,
                     TrackRating.user_id == user_id).one()
        except NoResultFound:
            return None

Track.rating = relation("TrackRating")


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

def load():
    with transaction.manager:
        for table in UN_TYPES:
            table.loadTable(DBSession)

def initDB(settings):
    from . import mash
    Base.metadata.create_all()
    with transaction.manager:
        for table in MASH_TYPES:
            table.initTable(DBSession)
        for table in UN_TYPES:
            table.initTable(DBSession)

def addUser(username, password, roles):
    try:
        user = User(name=username, password=password)
        DBSession.add(user)
        DBSession.flush()
        for name in roles:
            role = Role(name=name, user_id=user.id)
            DBSession.add(role)
        DBSession.flush()
    except IntegrityError:
        return "Failed to add user. User already exists."
    return True

def delUser(username):
    DBSession.query(User).filter(User.name == username).delete()
    DBSession.flush()

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

def rateItem(user_id, item_id, rating=None, starred=None):
    num = int(item_id[3:])
    if item_id.startswith("ar-"):
        try:
            row = DBSession.query(ArtistRating). \
              filter(ArtistRating.user_id == user_id,
                     ArtistRating.artist_id == num).one()
        except NoResultFound:
            row = ArtistRating(user_id=user_id, artist_id=num)
            DBSession.add(row)
    elif item_id.startswith("al-"):
        try:
            row = DBSession.query(AlbumRating). \
              filter(AlbumRating.user_id == user_id,
                     AlbumRating.album_id == num).one()
        except NoResultFound:
            row = AlbumRating(user_id=user_id, album_id=num)
            DBSession.add(row)
    elif item_id.startswith("tr-"):
        try:
            row = DBSession.query(TrackRating). \
              filter(TrackRating.user_id == user_id,
                     TrackRating.track_id == num).one()
        except NoResultFound:
            row = TrackRating(user_id=user_id, track_id=num)
            DBSession.add(row)
    if rating is not None:
        row.rating = rating
    if isinstance(starred, datetime.datetime):
        row.starred = starred
    elif starred is True:
        row.starred = None
    DBSession.flush()


UN_TYPES = [DBInfo, User, Role, PlayList, PlayListUser, PlayListTrack,
            ArtistRating, AlbumRating, TrackRating]
