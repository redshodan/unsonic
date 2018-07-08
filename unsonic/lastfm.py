import pylast
import requests

import logging
log = logging.getLogger(__name__)


# LastFM application creds
API_KEY = "83ccc11811b8e46234b0a5b8c0ed3e16"
API_SECRET = "c1ca75977d0930d80b314e2c1bb76435"

LANGUAGES = ["english", "german", "spanish", "french", "italian", "polish",
             "portuguese", "swedish", "turkish", "russian", "japanese",
             "chinese"]

LANG_TO_DOMAIN = {
    "english": pylast.DOMAIN_ENGLISH,
    "german": pylast.DOMAIN_GERMAN,
    "spanish": pylast.DOMAIN_SPANISH,
    "french": pylast.DOMAIN_FRENCH,
    "italian": pylast.DOMAIN_ITALIAN,
    "polish": pylast.DOMAIN_POLISH,
    "portuguese": pylast.DOMAIN_PORTUGUESE,
    "swedish": pylast.DOMAIN_SWEDISH,
    "turkish": pylast.DOMAIN_TURKISH,
    "russian": pylast.DOMAIN_RUSSIAN,
    "japanese": pylast.DOMAIN_JAPANESE,
    "chinese": pylast.DOMAIN_CHINESE
}

system_client = None


def getDomain(lang):
    return LANG_TO_DOMAIN[lang]


def hashPassword(password):
    return pylast.md5(password)


def getSystemClient():
    global system_client
    if not system_client:
        system_client = makeClient()
    return system_client


def makeClient(user=None, password=None):
    log.debug(f"Creating LastFM client for {user}")
    client = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                                  username=user, password_hash=password)
    # FIXME: more proper cache file name? ~/.cache?
    # self._lastfm.enable_caching("/tmp/unsonic-lastfm.cache")
    client.enable_caching()
    if user and password:
        client.is_user = True
    else:
        client.is_user = False
    return client


def getImage(client, url):
    shelf = client._get_cache_backend().shelf

    if url in shelf:
        return shelf[url]

    resp = requests.get(url)
    if resp:
        ret = (resp.content, resp.headers["Content-Type"])
        shelf[url] = ret
        return ret

    return None
