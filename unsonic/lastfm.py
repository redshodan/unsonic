import pylast

import logging
log = logging.getLogger(__name__)


# LastFM application creds
API_KEY = "83ccc11811b8e46234b0a5b8c0ed3e16"
API_SECRET = "c1ca75977d0930d80b314e2c1bb76435"


def hashPassword(password):
    return pylast.md5(password)


def makeUserClient(user, password):
    log.debug(f"Creating LastFM client for {user}")
    return pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                                username=user, password_hash=password)
