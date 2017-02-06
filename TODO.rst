For Initial Release
===================
* mishmash Command take a subparser description.
* add argparse.parse_known_args() option to mishmash for pass-through args to pserve
* musicFolderId's

* Get alembic rocking for schema versioning or some other schema up/down-grade
  path. Check with Travis on mishmash supporting the same.
* Proper server logging
* setup docker image for unsonic
* Get unsonic into pypi (registered, work out dist package contents)


General
=======
* federation of unsonics. for showing playing now and other stuff
* EC2/S3 support. Remote file storage for media files. Run in AWS. Pass back S3 URL for untranscoded stream.


For dsub
========
* getPodcasts.view -- At least fake it up with empty data
* getChatMessages -- At least fake it up with empty data


unsonic-db
==========
* cache auth.User objects with db refresh checks. Update cache on deleteUser call.
* Add an export-playlists command


jamstash
========
* Implement json
* Remove user/pass
* Use templating to set url


Tests
=====
* run every API test without required args. automate it from the
  class.param_defs array.


API
===
Exceptions
----------
* No LDAP auth
* No simple hex encoded passwords
* 'search' is deprecated, not going to implement
* addChatMessage/getChatMessage not stubbed out cause its silly and a very poor API
* changePassword:
  * You can change your own password without being an admin, as long as you're not
    a guest.
  * username param is not required, will default to your own username if not supplied.
* savePlayQueue: id is not required, means delete the playqueue and don't create
  one in its place


General
-------
* Fit guest account concept into the subsonic API. Make it play well with
  sharing urls
* Older calls were never updated for newer param frameworks.


Missing
-------
- getVideo
- getVideoInfo
- getArtistInfo: musicbrainz id, lastfm artist info. Add on a <html> for client display of generic content. http://www.subsonic.org/pages/inc/api/examples/artistInfo_example_1.xml
- getArtistInfo2: id3 version of getArtistInfo
- getAlbumInfo: musicbrainz id, lastfm artist info
- getAlbumInfo2: id3 version of getAlbumInfo
- getSimilarSongs: lastfm similar matching
- getSimilarSongs2: id3 version of getSimilarSongs
- getTopSongs: Returns top songs for the given artist, using data from last.fm.
- getSongsByGenre:
- getNowPlaying:
- hls:
- getCaptions:
- getLyrics:
- getShares:
- createShares:
- updateShare:
- deleteShare:
- getPodcasts:
- getNewestPodcasts:
- refreshPodcasts:
- createPodcastChannel:
- deletePodcastChannel:
- deletePodcastEpisode:
- downloadPodcastEpisode:
- jukeboxControl:
- getInternetRadioStations:
- getBookmarks:
- createBookmark:
- deleteBookmark:


Partial
-------
- getIndexes:
  params: both params
  resp:
  - missing ignoredArticles.
    <indexes ignoredArticles="The El La Los Las Le Les">
  - shortcuts
    <shortcut id="11" name="Audio books"/>
    <shortcut id="10" name="Podcasts"/>

- getArtists:
  params: musicFolderId
  resp:
  - missing ignoredArticles.
    <artists ignoredArticles="The El La Los Las Le Les">
  - missing covertArt

- getArtist:
  resp:
  - handle playCount for album
    
- getAlbumList:
  params: type is missing byGenre
          genre
          musicFolderId
  resp:
  - missing averageRating for album

- getRandomSongs:
  params: unimplemented params
          genre
          musicFolderId

- search2:
  params: musicFolderId

- search3:
  params: musicFolderId

- stream:
  params: missing converted, for videos
          all params other than id are ignored

- getCoverArt:
  params: missing size to convert image to

- getUser:
  resp: Needs folders

- getUsers:
  resp: Needs folders

- createUser:
  resp: Needs folders

- getStarred:
  resp: Needs musicFolderId
