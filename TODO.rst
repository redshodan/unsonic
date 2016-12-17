General
=======
* Proper server logging
* setup docker image for unsonic
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
* pathing for responses is weird, has a dash. missing .mp3 ending.
* Fit guest account concept into the subsonic API. Make it play well with
  sharing urls
* Figure out the differences between path/id3 results. Maybe union them? Prolly
  just return thing for the right kind of call
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
- getStarred2: id3 version
- search3:
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

- getGenres: No genre table to query against, maybe was part of mishmash before?
  <subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.10.2">
    <genres>
      <genre songCount="28" albumCount="6">Electronic</genre>
      <genre songCount="6" albumCount="2">Hard Rock</genre>
      <genre songCount="8" albumCount="2">R&B</genre>
      <genre songCount="22" albumCount="2">Blues</genre>
      <genre songCount="2" albumCount="2">Podcast</genre>
      <genre songCount="11" albumCount="1">Brit Pop</genre>
      <genre songCount="14" albumCount="1">Live</genre>
    </genres>
  </subsonic-response>

- getArtists:
  params: musicFolderId
  resp:
  - missing ignoredArticles.
    <artists ignoredArticles="The El La Los Las Le Les">
  - missing covertArt

- getAlbumList:
  params: type is missing byYear, byGenre
          fromYear
          toYear
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
