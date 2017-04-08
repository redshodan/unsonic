import pytest

from unsonic.auth import Roles
from unsonic.models import (Config, User, Role, PlayQueue, PlayList,
                            PlayListUser, PlayListTrack, ArtistRating,
                            AlbumRating, TrackRating, PlayCount, Scrobble)


def testAddDelUser(session):
    name = "testAddUser"
    user = User(name=name, password="secretz")
    session.add(user)
    session.flush()

    res = session.query(User).filter(User.name == name)
    assert res.count() == 1
    res.delete()
    session.flush()

    res = session.query(User).filter(User.name == name)
    assert res.count() == 0


idxs = [1, 2, 3]


@pytest.mark.parametrize("klass,items,item_id",
                         [(Role, Roles.def_user_roles, "name"),
                          (PlayCount, idxs, "track_id"),
                          (Scrobble, idxs, "track_id"),
                          (PlayQueue, idxs, "track_id"),
                          (ArtistRating, idxs, "artist_id"),
                          (AlbumRating, idxs, "album_id"),
                          (TrackRating, idxs, "track_id")])
def testAddUserItems(session, klass, items, item_id):
    # Add user
    name = "testAddUserItems"
    user = User(name=name, password="secretz")
    session.add(user)
    session.flush()
    uid = user.id

    # Add items
    kwargs = {"user_id": uid}
    for item_val in items:
        kwargs[item_id] = item_val
        session.add(klass(**kwargs))
    session.flush()

    # Verify item count
    res = session.query(klass).filter(klass.user_id == uid)
    assert res.count() == len(items)

    # Delete user
    res = session.query(User).filter(User.id == uid)
    assert res.count() == 1
    res.delete()
    session.flush()

    # Verify user is gone
    res = session.query(User).filter(User.id == uid)
    assert res.count() == 0

    # Verify items are gone
    res = session.query(klass).filter(klass.user_id == uid)
    assert res.count() == 0


def testAddUserPlayList(session):
    # Add users
    name = "testAddUserPlayList"
    user = User(name=name, password="secretz")
    session.add(user)
    name2 = "testAddUserPlayList2"
    user2 = User(name=name2, password="secretz")
    session.add(user2)
    name3 = "testAddUserPlayList3"
    user3 = User(name=name3, password="secretz")
    session.add(user3)
    session.flush()
    uid = user.id
    uid2 = user2.id
    uid3 = user3.id

    # Add playlist
    plist = PlayList(user_id=uid, name="test", comment="testing")
    session.add(plist)
    session.flush()

    # Add users
    session.add(PlayListUser(playlist_id=plist.id, user_id=uid2))
    session.add(PlayListUser(playlist_id=plist.id, user_id=uid3))
    session.flush()

    # Add tracks
    session.add(PlayListTrack(playlist_id=plist.id, track_id=1))
    session.add(PlayListTrack(playlist_id=plist.id, track_id=2))
    session.add(PlayListTrack(playlist_id=plist.id, track_id=3))
    session.flush()

    # Verify counts
    res = session.query(PlayListUser).\
                    filter(PlayListUser.playlist_id == plist.id)
    assert res.count() == 2
    res = session.query(PlayListTrack).\
                    filter(PlayListTrack.playlist_id == plist.id)
    assert res.count() == 3

    # Delete user
    res = session.query(User).filter(User.id == uid)
    assert res.count() == 1
    res.delete()
    session.flush()

    # Verify user is gone
    res = session.query(User).filter(User.id == uid)
    assert res.count() == 0

    # Verify items are gone
    res = session.query(PlayList).filter(PlayList.id == plist.id)
    assert res.count() == 0
    res = session.query(PlayListUser).\
                    filter(PlayListUser.playlist_id == plist.id)
    assert res.count() == 0
    res = session.query(PlayListTrack).\
                    filter(PlayListTrack.playlist_id == plist.id)
    assert res.count() == 0


def testConfig(session):
    name = "testConfig"
    user = User(name=name, password="secretz")
    session.add(user)
    session.flush()

    cfg = Config(key="key1", value="value1")
    session.add(cfg)
    cfg = Config(key="key2", value="value2", user_id=user.id)
    session.add(cfg)
    session.flush()

    res = session.query(Config).filter(Config.key == "key1")
    assert res.count() == 1
    res = session.query(Config).filter(Config.key == "key2")
    assert res.count() == 1

    res = session.query(User).filter(User.id == user.id)
    assert res.count() == 1
    res.delete()
    session.flush()

    res = session.query(Config).filter(Config.key == "key1")
    assert res.count() == 1
    res = session.query(Config).filter(Config.key == "key2")
    assert res.count() == 0
