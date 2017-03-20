import pylast


def lastfm(user, password):
    API_KEY = "83ccc11811b8e46234b0a5b8c0ed3e16"
    SHARED_SECRET = "c1ca75977d0930d80b314e2c1bb76435"
    return pylast.LastFMNetwork(api_key=API_KEY, api_secret=SHARED_SECRET,
                                username=user,
                                password_hash=pylast.md5(password))
