from unsonic import auth
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
    session.flush()

    res = session.query(User).filter(User.name == name)
    assert res.count() == 1

    res.delete()
    session.flush()

    res = session.query(User).filter(User.name == name)
    assert res.count() == 0


def testAddUserRoles(session):
    name = "testAddUserRoles"
    user = User(name=name, password="secretz")
    session.add(user)
    session.flush()

    uid = user.id
    for role_name in auth.Roles.def_user_roles:
        role = Role(name=role_name, user_id=uid)
        session.add(role)
    session.flush()

    res = session.query(Role).filter(Role.user_id == uid)
    assert res.count() == len(auth.Roles.def_user_roles)

    res = session.query(User).filter(User.name == name)
    assert res.count() == 1
    res.delete()
    session.flush()

    res = session.query(Role).filter(Role.user_id == uid)
    assert res.count() == 0
