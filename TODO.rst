For dsub
========

* getPodcasts.view -- At least fake it up with empty data
* getChatMessages -- At least fake it up with empty data


unsonic-db
==========

* cache auth.User objects with db refresh checks
* Add an export-playlists command


jamstash
========

* Implement json
* Remove user/pass
* Use templating to set url


API
===
Exceptions
----------
* No LDAP auth
* No simple hex encoded passwords

General
-------
* pathing for responses is weird, has a dash. missing .mp3 ending.

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
- getStarred:
- getStarred2: id3 version
X search: deprecated, not going to impl
- search3:
- updatePlaylist:
- deletePlaylist:
* download:
- hls:
- getCaptions:
- getLyrics:
- getAvatar:
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
- getChatMessages:
- addChatMessage:
- updateUser:
- deleteUser:
- changePassword:
- getBookmarks:
- createBookmark:
- deleteBookmark:
- getPlayQueue:
- savePlayQueue:


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
          fromYear
          toYear
          genre
          musicFolderId

- search2:
  params: musicFolderId

- getPlayLists:
  resp: missing allowedUser

- getPlayList:
  resp: missing allowedUser

- createPlaylist:
  resp: Since 1.14.0 the newly created/updated playlist is returned. In earlier versions an empty <subsonic-response> element is returned.

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
