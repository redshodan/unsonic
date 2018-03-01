import pylast

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


def getDomain(lang):
    return LANG_TO_DOMAIN[lang]


def hashPassword(password):
    return pylast.md5(password)


def makeClient(user=None, password=None):
    log.debug(f"Creating LastFM client for {user}")
    client = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                                  username=user, password_hash=password)
    if user and password:
        client.is_user = True
    else:
        client.is_user = False
    return client
