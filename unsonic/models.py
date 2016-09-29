import transaction, datetime, argparse
from argparse import Namespace
from contextlib import contextmanager

import sqlalchemy
from sqlalchemy import (engine_from_config, Column, Integer, Text, ForeignKey,
                        String, DateTime, event, Index, Boolean)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker, relation
from sqlalchemy.orm.exc import NoResultFound
from zope.sqlalchemy import ZopeTransactionExtension

import mishmash.orm
from mishmash.orm import (Base, Artist, Album, Meta, Track, Image,
                          artist_images, album_images)
from mishmash.orm import TYPES as MASH_TYPES
from mishmash.database import init as dbinit

from .moduleref import ModuleRef
from .version import DB_VERSION


db_url = None
db_engine = None
session_maker = None
dbinfo = Namespace()


@sqlalchemy.event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if db_url.startswith("sqlite://"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@contextmanager
def Session():
    """Provide a transactional scope around a series of operations."""
    session = session_maker()
    try:
        yield session
        if hasattr(session, "failed"):
            session.rollback()
        else:
            session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


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
    def initTable(session, config):
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
    def initTable(session, config):
        addUser(session, "admin", None, [Roles.REST, Roles.USERS, Roles.ADMIN])


    @staticmethod
    def loadTable(session):
        try:
            dbinfo.users = {}
            for user in session.query(User).all():
                u = Namespace()
                u.name = user.name
                u.listening = None
                dbinfo.users[u.name] = u
        finally:
            session.close()


    def export(self):
        ret = Namespace()
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

# playlist_images = sql.Table("playlist_images", Base.metadata,
#                             sql.Column("playlist_id", sql.Integer,
#                                        sql.ForeignKey("un_playlist.id")),
#                             sql.Column("img_id", sql.Integer,
#                                        sql.ForeignKey("images.id")))
# '''Pivot table 'album_images' for mapping an album ID to a value in the
# `images` table.'''

class PlayList(Base, OrmObject):
    __tablename__ = 'un_playlists'
        
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("un_users.id", ondelete='CASCADE'),
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
    # images = relation("Image", secondary=playlist_images, cascade="all")
    '''one-to-many playlist images.'''


class PlayListUser(Base, OrmObject):
    __tablename__ = 'un_playlistusers'

    id = Column(Integer, primary_key=True)
    playlist_id = Column(Integer, ForeignKey("un_playlists.id",
                                             ondelete='CASCADE'),
                         nullable=False)
    user_id = Column(Integer, ForeignKey("un_users.id"), nullable=False)
    playlist = relation("PlayList")
    user = relation("User")


class PlayListTrack(Base, OrmObject):
    __tablename__ = 'un_playlisttracks'

    id = Column(Integer, primary_key=True)
    playlist_id = Column(Integer, ForeignKey("un_playlists.id",
                                             ondelete='CASCADE'),
                         nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
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
    pseudo_rating = Column(Boolean, default=True, nullable=False)
    starred = Column(DateTime, default=None, nullable=True)
    pseudo_starred = Column(Boolean, default=True, nullable=False)
    artist = relation("Artist")
    user = relation("User")

    @staticmethod
    def get(session, artist_id, user_id):
        try:
            return session.query(ArtistRating).\
              filter(ArtistRating.artist_id == artist_id,
                     ArtistRating.user_id == user_id).one()
        except NoResultFound:
            return None
        finally:
            session.close()

Artist.rating = relation("ArtistRating")
    

class AlbumRating(Base, OrmObject):
    __tablename__ = "un_albumratings"
        
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False,
                      primary_key=True)
    user_id = Column(Integer, ForeignKey("un_users.id"), nullable=False,
                     primary_key=True)
    rating = Column(Integer, default=None, nullable=True)
    pseudo_rating = Column(Boolean, default=True, nullable=False)
    starred = Column(DateTime, default=None, nullable=True)
    pseudo_starred = Column(Boolean, default=True, nullable=False)
    album = relation("Album")
    user = relation("User")

    @staticmethod
    def get(session, album_id, user_id):
        try:
            return session.query(AlbumRating).\
              filter(AlbumRating.album_id == album_id,
                     AlbumRating.user_id == user_id).one()
        except NoResultFound:
            return None
        finally:
            session.close()

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
    def get(session, track_id, user_id):
        try:
            return session.query(TrackRating).\
              filter(TrackRating.track_id == track_id,
                     TrackRating.user_id == user_id).one()
        except NoResultFound:
            return None
        finally:
            session.close()

Track.rating = relation("TrackRating")


class PlayCount(Base, OrmObject):
    __tablename__ = "un_playcounts"

    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False,
                      primary_key=True)
    user_id = Column(Integer, ForeignKey("un_users.id"), nullable=False,
                     primary_key=True)
    count = Column(Integer, nullable=False)
    track = relation("Track")
    user = relation("User")
    
Track.play_count = relation("PlayCount")


class Scrobble(Base, OrmObject):
    __tablename__ = "un_scrobbles"
    
    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("un_users.id"), nullable=False)
    tstamp = Column(DateTime, default=None, nullable=False)
    track = relation("Track")
    user = relation("User")

    @declared_attr
    def __table_args__(cls):
        return (Index("scrobble_user_index", "user_id"), )

Track.scrobbles = relation("Scrobble")


### Utility functions
def init(settings, webapp):
    from . import mash
    global db_url, db_engine, session_maker
    db_url = settings["sqlalchemy.url"]
    db_engine, session_maker = dbinit(mash.mashConfig(settings))


def load():
    with Session() as session:
        for table in UN_TYPES:
            table.loadTable(session)


def initDB(settings):
    from . import mash
    Base.metadata.create_all()
    with Session() as session:
        for table in UN_TYPES:
            table.initTable(session, mash.mashConfig(settings))


def addUser(session, username, password, roles):
    try:
        user = User(name=username, password=password)
        session.add(user)
        session.flush()
        for name in roles:
            role = Role(name=name, user_id=user.id)
            session.add(role)
        session.flush()
    except IntegrityError:
        session.failed = True
        return "Failed to add user. User already exists."
    return True


def delUser(session, username):
    session.query(User).filter(User.name == username).delete()
    session.flush()


def listUsers(session):
    users = []
    for user in session.query(User).all():
        users.append((user.name, [g.name for g in user.roles]))
    return users


def setUserPassword(session, uname, password):
    user = getUserByName(session, uname)
    if not user:
        return False
    user.password = password
    session.flush()


def getUserByName(session, username):
    try:
        return session.query(User).filter(User.name == username).one()
    except NoResultFound:
        return None


def getUserByID(session, id):
    try:
        return session.query(User).filter(User.id == id).one()
    except NoResultFound:
        return None


def rateItem(session, user_id, item_id, rating=None, starred=None):
    num = int(item_id[3:])
    artist_id = None
    album_id = None
    if item_id.startswith("ar-"):
        row = ArtistRating.get(num, user_id)
        if row is None:
            row = ArtistRating(artist_id=num, user_id=user_id)
            session.add(row)
    elif item_id.startswith("al-"):
        row = AlbumRating.get(num, user_id)
        if row is None:
            row = AlbumRating(album_id=num, user_id=user_id)
            session.add(row)
            session.flush()
        artist_id = row.album.artist_id
    elif item_id.startswith("tr-"):
        row = TrackRating.get(num, user_id)
        if row is None:
            row = TrackRating(track_id=num, user_id=user_id)
            session.add(row)
            session.flush()
        album_id = row.track.album_id
    if rating is not None:
        if rating == 0:
            row.rating = None
            row.pseudo_rating = True
        else:
            row.rating = rating
            row.pseudo_rating = False
    if isinstance(starred, datetime.datetime):
        row.starred = starred
        row.pseudo_starred = False
    elif starred is True:
        row.starred = None
        row.pseudo_starred = True
    session.flush()
    if artist_id or album_id:
        updatePseudoRatings(user_id=user_id, album_id=album_id,
                            artist_id=artist_id)


ALL = object()
def updatePseudoRatings(session, user_id=None, album_id=ALL, artist_id=ALL):
    # Update albums first
    albums = None
    if album_id is ALL:
        albums = session.query(Album).all()
    elif album_id is not None:
        albums = session.query(Album).filter(Album.id == album_id).all()

    if albums:
        for album in albums:
            alrating = AlbumRating.get(album.id, user_id)
            if alrating is None:
                alrating = AlbumRating(album_id=album.id, user_id=user_id)
                session.add(alrating)
            tracks = session.query(Track). \
                         filter(Track.album_id == album.id).all()
            pseudo = 0
            count = 0
            starred = None
            for track in tracks:
                trating = TrackRating.get(track.id, user_id)
                if trating:
                    if trating.rating is not None:
                        pseudo += trating.rating
                    if trating.starred is not None:
                        if starred is None or starred > trating.starred:
                            # Extract the oldest starred date
                            starred = trating.starred
                # Down rank for unrated tracks
                count += 1
            if count and alrating.pseudo_rating:
                pseudo = round(float(pseudo) / float(count))
                alrating.rating = pseudo
                alrating.pseudo_rating = True
            if starred and alrating.pseudo_starred:
                alrating.starred = starred
                alrating.pseudo_starred = True

    # Update artists last
    artists = None
    if artist_id is ALL:
        artists = session.query(Artist).all()
    elif artist_id is not None:
        artists = session.query(Artist).filter(Artist.id == artist_id).all()

    if artists:
        for artist in artists:
            arrating = ArtistRating.get(artist.id, user_id)
            if arrating is None:
                arrating = ArtistRating(user_id=user_id, artist_id=artist.id)
                session.add(arrating)
            if arrating.rating is None or not arrating.pseudo_rating:
                print("skipping hand set rating", arrating, artist)
                continue
            albums = session.query(Album). \
                         filter(Album.artist_id == artist.id).all()
            pseudo = 0
            count = 0
            starred = None
            for album in albums:
                alrating = AlbumRating.get(album.id, user_id)
                if alrating:
                    if alrating.rating is not None:
                        pseudo += alrating.rating
                    if alrating.starred is not None:
                        if starred is None or starred > alrating.starred:
                            # Extract the oldest starred date
                            starred = alrating.starred
                    
                # Down rank for unrated albums
                count += 1
            if count:
                pseudo = round(float(pseudo) / float(count))
                arrating.rating = pseudo
                arrating.pseudo_rating = True
            if starred and arrating.pseudo_starred:
                arrating.starred = starred
                arrating.pseudo_starred = True


UN_TYPES = [DBInfo, User, Role, PlayList, PlayListUser, PlayListTrack,
            ArtistRating, AlbumRating, TrackRating, PlayCount, Scrobble]
