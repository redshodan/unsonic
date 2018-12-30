Release 0.1
===========
* func tests run full passes with json and jsonp
* fix db slowness


Release 0.2
===========
* Scrobbling
* Add an export-playlists command
* Add playlist manipulation commands

Config
======
* Minimize ini config. Store as much as possible in the db through the config
  command. Allow for ini file to override built in defaults for everything. Have
  an installed default ini file to read in, then user's if found else
  /etc/unsonic. All commands look for the same ini's to find the db url to
  startup, or cmdline arg for db url.

General
=======
* federation of unsonics. for showing playing now and other stuff
* EC2/S3 support. Remote file storage for media files. Run in AWS. Pass back S3 URL for untranscoded stream.


database
==========
* cache auth.User objects with db refresh checks. Update cache on deleteUser
  call.
* Cache Tag table


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
* getLyrics: added optional id param which is a track id that can be looked up
* Stubbed out, wont implement:
  - hls
  - getVideo
  - getVideoInfo
  - getCaptions:


General
-------
* Fit guest account concept into the subsonic API. Make it play well with
  sharing urls
* Older calls were never updated for newer param frameworks.


Missing
-------
- jukeboxControl:

- getPodcasts:
- getNewestPodcasts:
- refreshPodcasts:
- createPodcastChannel:
- deletePodcastChannel:
- deletePodcastEpisode:
- downloadPodcastEpisode:


Partial
-------
- getIndexes:
  resp:
  - shortcuts
    <shortcut id="11" name="Audio books"/>
    <shortcut id="10" name="Podcasts"/>

- getAlbumList:
  resp:
  - missing averageRating for album

- stream:
  params: missing converted, for videos
          all params other than id are ignored

- getCoverArt:
  params: missing size to convert image to
