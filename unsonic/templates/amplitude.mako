<!DOCTYPE html>
<html>
    <head>
        <title>Unsonic Music Player</title>
        <!-- Include Resource Stylesheets -->
        <link rel="stylesheet" type="text/css" href="../static/amplitude/css/foundation.min.css"/>

        <!-- Include Resource Javascript -->
        <script type="text/javascript" src="../static/amplitude/js/jquery.js"></script>
        <script type="text/javascript" src="../static/amplitude/js/foundation.min.js"></script>

        <!-- Include Amplitude JS -->
        <script type="text/javascript" src="../static/amplitude/js/amplitude.js"></script>

        <!-- Include UX functions JS -->
        <script type="text/javascript" src="../static/amplitude/js/functions.js"></script>

        <!-- Include Style Sheet -->
        <link rel="stylesheet" type="text/css" href="../static/amplitude/css/app.css"/>
    </head>
    <body>
        <div class="grid-x" id="blue-playlist-container">
            <div class="large-10 medium-12 small-11 large-centered medium-centered small-centered cell" id="amplitude-player">
                <div class="grid-x">
                    <div class="large-6 medium-6 small-12 cell" id="amplitude-left">
                        <div align="center">
                            <img amplitude-song-info="cover_art_url" amplitude-main-song-info="true"/>
                        </div>
                        <div id="player-left-bottom">
                            <div id="time-container">
                                <span class="current-time">
                                    <span class="amplitude-current-minutes" amplitude-main-current-minutes="true"></span>:<span class="amplitude-current-seconds" amplitude-main-current-seconds="true"></span>
                                </span>
                                <div id="progress-container">
                                    <input type="range" class="amplitude-song-slider" amplitude-main-song-slider="true"/>
                                    <progress id="song-played-progress" class="amplitude-song-played-progress" amplitude-main-song-played-progress="true"></progress>
                                    <progress id="song-buffered-progress" class="amplitude-buffered-progress" value="0"></progress>
                                </div>
                                <span class="duration">
                                    <span class="amplitude-duration-minutes" amplitude-main-duration-minutes="true"></span>:<span class="amplitude-duration-seconds" amplitude-main-duration-seconds="true"></span>
                                </span>
                            </div>

                            <div id="control-container">
                                <div id="repeat-container">
                                    <div class="amplitude-repeat" id="repeat"></div>
                                    <div class="amplitude-shuffle amplitude-shuffle-off" id="shuffle"></div>
                                </div>

                                <div id="central-control-container">
                                    <div id="central-controls">
                                        <div class="amplitude-prev" id="previous"></div>
                                        <div class="amplitude-play-pause" amplitude-main-play-pause="true" id="play-pause"></div>
                                        <div class="amplitude-next" id="next"></div>
                                    </div>
                                </div>

                                <div id="volume-container">
                                    <div class="volume-controls">
                                        <div class="amplitude-mute amplitude-not-muted"></div>
                                        <input type="range" class="amplitude-volume-slider"/>
                                        <div class="ms-range-fix"></div>
                                    </div>
                                    <div class="amplitude-shuffle amplitude-shuffle-off" id="shuffle-right"></div>
                                </div>
                            </div>

                            <div id="meta-container">
                                <span amplitude-song-info="name" amplitude-main-song-info="true" class="song-name"></span>

                                <div class="song-artist-album">
                                    <span amplitude-song-info="artist" amplitude-main-song-info="true"></span>
                                    <span amplitude-song-info="album" amplitude-main-song-info="true"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="large-6 medium-6 small-12 cell" id="amplitude-right">

                        <%def name="makeAmpTrack(track, url, index)">
                            <div class="song amplitude-song-container
                                        amplitude-play-pause"
                                 amplitude-song-index="${index}">
                                <div class="song-now-playing-icon-container">
                                    <div class="play-button-container">
                                    </div>
                                    <img class="now-playing" src="../static/amplitude/img/now-playing.svg"/>
                                </div>
                                <div class="song-meta-data">
                                    <span class="song-title">${track.title}</span>
                                    <span class="song-artist">${track.artist.name}</span>
                                </div>
                                <a href="https://switchstancerecordings.bandcamp.com/..." class="bandcamp-link" target="_blank">
                                    <img class="bandcamp-grey" src="../static/amplitude/img/bandcamp-grey.svg"/>
                                    <img class="bandcamp-white" src="../static/amplitude/img/bandcamp-white.svg"/>
                                </a>
                                <%
                                    attrs['duration'] = "%02d:%02d" % (track.time_secs / 60, track.time_secs % 60)
                                    if track.time_secs / 3600 > 1:
                                        attrs['duration'] = "%02d:%s" % (track.time_secs / 3600, attrs['duration'])
                                %>
                                <span class="song-duration">${attrs['duration']}</span>
                            </div>
                        </%def>

                        % for track, url, coverart_url in tracks:
                            ${makeAmpTrack(track, url, loop.index)}
                        % endfor
                    </div>
                </div>
            </div>
        </div>
    </body>
    <script type="text/javascript">
        <%def name="makeTrack(track, url, coverart_url, first)">
        % if not first:
        ,
        % endif
        {
        "name": "${track.title}",
        "artist": "${track.artist.name}",
        "album": "${track.album.title}",
        "url": "${url}",
        "cover_art_url": "${coverart_url}"
        }
        </%def>
        Amplitude.init({
        "songs": [
            % for track, url, coverart_url in tracks:
                ${makeTrack(track, url, coverart_url, loop.first)}
            % endfor
        ]
        });
    </script>
</html>
