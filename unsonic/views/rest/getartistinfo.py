import xml.etree.ElementTree as ET
import pylast

from . import Command, NotFound, registerCmd, int_t, playable_id_t, bool_t
from ... import lastfm
from ...models import Artist, Album, Track, getPlayable


@registerCmd
class GetArtistInfo(Command):
    name = "getArtistInfo.view"
    param_defs = {
        "id": {"required": True, "type": playable_id_t},
        "count": {"default": 20, "type": int_t},
        "includeNotPresent": {"type": bool_t, "default": False},
    }
    dbsess = True

    def __init__(self, route, req, session=None):
        super().__init__(route, req, session)
        self.setParams()

    def setParams(self, tag_name="artistInfo"):
        self.tag_name = tag_name

    def handleReq(self, session):
        artist = getPlayable(session, self.params["id"])
        if not artist:
            raise NotFound("Item not found")
        if not isinstance(artist, Artist):
            artist = session.query(Artist).filter(
                Artist.id == artist.artist_id).one_or_none()
        if not artist:
            raise NotFound("Item not found")

        lang = lastfm.getDomain(self.req.authed_user.lastfm_lang)
        lf_client = self.req.authed_user.lastfm
        lf_artist = lf_client.get_artist(artist.name)

        ainfo = ET.Element(self.tag_name)
        bio = ET.Element("biography")
        bio.text = lf_artist.get_bio_summary(language=lang)
        ainfo.append(bio)
        mbid = ET.Element("musicBrainzId")
        mbid.text = lf_artist.get_mbid()
        ainfo.append(mbid)
        url = ET.Element("lastFmUrl")
        url.text = lf_artist.get_url(lang)
        ainfo.append(url)
        url = ET.Element("smallImageUrl")
        url.text = lf_artist.get_cover_image(pylast.SIZE_SMALL)
        ainfo.append(url)
        url = ET.Element("mediumImageUrl")
        url.text = lf_artist.get_cover_image(pylast.SIZE_MEDIUM)
        ainfo.append(url)
        url = ET.Element("largeImageUrl")
        url.text = lf_artist.get_cover_image(pylast.SIZE_EXTRA_LARGE)
        ainfo.append(url)

        for sim in lf_artist.get_similar(limit=self.params["count"]):
            name = sim.item.get_name()
            row = session.query(Artist).filter(
                Artist.name == name).one_or_none()
            if not row:
                name2 = name.replace(" ", "").lower()
                row = session.query(Artist).filter(
                    Artist.name == name2).one_or_none()
            if not row:
                if not self.params["includeNotPresent"]:
                    continue
                else:
                    row_id = "-1"
            else:
                row_id = row.id
            sa = ET.Element("similarArtist")
            sa.set("name", name)
            sa.set("id", f"ar-{row_id}" if row_id else "")
            ainfo.append(sa)

        return self.makeResp(child=ainfo)
