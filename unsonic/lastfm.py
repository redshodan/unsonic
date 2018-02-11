import pylast


# LastFM application creds
API_KEY = "83ccc11811b8e46234b0a5b8c0ed3e16"
API_SECRET = "c1ca75977d0930d80b314e2c1bb76435"


def makeUserLastFM():
    try:
        lastfm = lastFm(os.environ["LASTFM_USERNAME"],
                        os.environ["LASTFM_PASSWD"])
    except KeyError:
        log.debug("Skipping last.fm scrobbler, "
                  " LASTFM_USERNAME/LASTFM_PASSWD not set")
        lastfm = None


def lastfm(user, password):
    return pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                                username=user,
                                password_hash=pylast.md5(password))
