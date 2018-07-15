from unsonic.models import InternetRadio
from unsonic.views.rest.createinternetradiostation import \
    CreateInternetRadioStation
from unsonic.views.rest.deleteinternetradiostation import \
    DeleteInternetRadioStation
from unsonic.views.rest.getinternetradiostations import \
    GetInternetRadioStations
from unsonic.views.rest.updateinternetradiostation import \
    UpdateInternetRadioStation
from . import buildCmd, checkResp


def testCreateIRadio(session):
    name = "Foo iradio"
    stream_url = "http://foo.com/stream"
    homepage_url = "http://foo.com/home"
    cmd = buildCmd(session, CreateInternetRadioStation,
                   {"name": name, "streamUrl": stream_url,
                    "homepageUrl": homepage_url})
    checkResp(cmd.req, cmd())
    row = session.query(InternetRadio).\
        filter(InternetRadio.name == name).one_or_none()
    assert row is not None
    assert row.stream_url == stream_url
    assert row.homepage_url == homepage_url
    assert row.user.name == "test"


def testUpdateIRadio(session):
    name = "Foo iradio"
    stream_url = "http://foo.com/stream"
    homepage_url = "http://foo.com/home"
    cmd = buildCmd(session, CreateInternetRadioStation,
                   {"name": name, "streamUrl": stream_url,
                    "homepageUrl": homepage_url})
    sub_resp = checkResp(cmd.req, cmd())
    irs = sub_resp.find("{http://subsonic.org/restapi}internetRadioStations")
    ir = irs.find("{http://subsonic.org/restapi}internetRadioStation")
    ir_id = ir.get("id")
    row = session.query(InternetRadio).\
        filter(InternetRadio.name == name).one_or_none()
    assert row is not None
    assert row.id == int(ir_id[3:])
    assert row.stream_url == stream_url
    assert row.homepage_url == homepage_url
    assert row.user.name == "test"

    nname = "Foo iradio_new"
    nstream_url = "http://foo.com/stream_new"
    nhomepage_url = "http://foo.com/home_new"
    cmd = buildCmd(session, UpdateInternetRadioStation,
                   {"id": ir_id, "name": nname, "streamUrl": nstream_url,
                    "homepageUrl": nhomepage_url})
    checkResp(cmd.req, cmd())
    row = session.query(InternetRadio).\
        filter(InternetRadio.name == nname).one_or_none()
    assert row is not None
    assert row.stream_url == nstream_url
    assert row.homepage_url == nhomepage_url
    assert row.user.name == "test"


def testGetIRadio(session):
    names = ["Foo iradio", "Foo iradio2"]
    stream_urls = ["http://foo.com/stream", "http://foo.com/stream2"]
    homepage_urls = ["http://foo.com/home", "http://foo.com/home2"]
    cmd = buildCmd(session, CreateInternetRadioStation,
                   {"name": names[0], "streamUrl": stream_urls[0],
                    "homepageUrl": homepage_urls[0]})
    checkResp(cmd.req, cmd())

    cmd = buildCmd(session, CreateInternetRadioStation,
                   {"name": names[1], "streamUrl": stream_urls[1],
                    "homepageUrl": homepage_urls[1]})
    checkResp(cmd.req, cmd())

    cmd = buildCmd(session, GetInternetRadioStations, {})
    sub_resp = checkResp(cmd.req, cmd())
    irs = sub_resp.find("{http://subsonic.org/restapi}internetRadioStations")
    ir = irs.find("{http://subsonic.org/restapi}internetRadioStation")
    for ir in ir:
        assert ir.get("id")
        assert ir.get("name") in names
        assert ir.get("streamUrl") in stream_urls
        assert ir.get("homepageUrl") in homepage_urls


def testDeleteIRadio(session):
    names = ["Foo iradio", "Foo iradio2"]
    stream_urls = ["http://foo.com/stream", "http://foo.com/stream2"]
    homepage_urls = ["http://foo.com/home", "http://foo.com/home2"]
    cmd = buildCmd(session, CreateInternetRadioStation,
                   {"name": names[0], "streamUrl": stream_urls[0],
                    "homepageUrl": homepage_urls[0]})
    checkResp(cmd.req, cmd())

    cmd = buildCmd(session, CreateInternetRadioStation,
                   {"name": names[1], "streamUrl": stream_urls[1],
                    "homepageUrl": homepage_urls[1]})
    sub_resp = checkResp(cmd.req, cmd())
    irs = sub_resp.find("{http://subsonic.org/restapi}internetRadioStations")
    ir = irs.find("{http://subsonic.org/restapi}internetRadioStation")
    ir_id = ir.get("id")

    cmd = buildCmd(session, GetInternetRadioStations, {})
    sub_resp = checkResp(cmd.req, cmd())

    cmd = buildCmd(session, DeleteInternetRadioStation, {"id": ir_id})
    checkResp(cmd.req, cmd())

    cmd = buildCmd(session, GetInternetRadioStations, {})
    sub_resp = checkResp(cmd.req, cmd())
    irs = sub_resp.find("{http://subsonic.org/restapi}internetRadioStations")
    ir = irs.find("{http://subsonic.org/restapi}internetRadioStation")
    assert ir.get("id")
    assert ir.get("name") == names[0]
    assert ir.get("streamUrl") == stream_urls[0]
    assert ir.get("homepageUrl") == homepage_urls[0]
