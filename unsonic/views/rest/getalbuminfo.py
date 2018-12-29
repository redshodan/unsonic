import xml.etree.ElementTree as ET
import pylast

from . import Command, NotFound, MissingParam, registerCmd, playable_id_t
from ... import lastfm
from ...models import Artist, Album, getPlayable
from ...log import log


@registerCmd
class GetAlbumInfo(Command):
    name = "getAlbumInfo.view"
    param_defs = {
        "id": {"required": True, "type": playable_id_t},
    }
    dbsess = True

    def handleReq(self, session):
        album = getPlayable(session, self.params["id"])
        if not album:
            raise NotFound("Item not found")
        if isinstance(album, Artist):
            raise MissingParam("id must be an album or song")
        if not isinstance(album, Album):
            album = session.query(Album).filter(
                Album.id == album.album_id).one_or_none()
        if not album:
            raise NotFound("Item not found")

        try:
            lang = lastfm.getDomain(self.req.authed_user.lastfm_lang)
            lf_client = self.req.authed_user.lastfm
            lf_album = lf_client.get_album(album.artist.name, album.title)

            ainfo = ET.Element("albumInfo")
            notes = ET.Element("notes")
            notes.text = lf_album.get_wiki_summary()
            ainfo.append(notes)
            mbid = ET.Element("musicBrainzId")
            mbid.text = lf_album.get_mbid()
            ainfo.append(mbid)
            url = ET.Element("lastFmUrl")
            url.text = lf_album.get_url(lang)
            ainfo.append(url)
            url = ET.Element("smallImageUrl")
            url.text = lf_album.get_cover_image(pylast.SIZE_SMALL)
            ainfo.append(url)
            url = ET.Element("mediumImageUrl")
            url.text = lf_album.get_cover_image(pylast.SIZE_MEDIUM)
            ainfo.append(url)
            url = ET.Element("largeImageUrl")
            url.text = lf_album.get_cover_image(pylast.SIZE_EXTRA_LARGE)
            ainfo.append(url)
        except pylast.WSError as e:
            log.error("Error talking to LastFM: %s / %s", str(e), e.get_id())
            # wtf is this a string and an int?
            if e.get_id() == str(pylast.STATUS_INVALID_PARAMS):
                return self.makeResp(status=404)
            else:
                return self.makeResp(status=504)
        except Exception as e:
            log.error("Error talking to LastFM: " + str(e))
            return self.makeResp(status=504)

        return self.makeResp(child=ainfo)
