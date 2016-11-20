define(['jquery', 'knockout', 'mapping', 'jplayer', 'global', 'utils', 'model', 'subsonic', 'jquery.scrollTo'], function ($, ko, mapping, jPlayer, global, utils, model, subsonic) {
var self = this;
var player1 = '#playdeck_1';
var player2 = '#playdeck_2';
var scrobbled = false;
var timerid = 0;
self.queue = new ko.observableArray([]).syncWith("queue");
self.playingSong = ko.observable().publishOn("playing");
var settings = global.settings;

defaultPlay = function (data, event) {
    if (typeof $(player1).data("jPlayer") == 'undefined') {
        nextTrack();
    }
}
nextTrack = function (data, event) {
    var next = getNextSong();
    if (next) {
        playSong(false, next);
    }
    //$(player1).jPlayer("stop");
    //$(player2).jPlayer("play");
}
getNextSong = function () {
    if (settings.Debug()) { console.log('Getting Next Song > ' + 'Queue length: ' + self.queue().length); }
    if (self.queue().length > 0) {
        var song = ko.utils.arrayFirst(self.queue(), function (item) {
            return item.playing() === true;
        });
        var index = self.queue.indexOf(song);
        var next = self.queue()[index + 1];
        if (typeof next != 'undefined') {
            return next;
        } else {
            return false;
        }
    } else {
        return false;
    }
}
saveTrackPosition = function () {
    //var audio = typeof $(player1).data("jPlayer") != 'undefined' ? true : false;
    var audio = $(player1).data("jPlayer");
    if (typeof audio != 'undefined') {
        if (audio.status.currentTime > 0 && audio.status.paused == false) {
            var song = ko.utils.arrayFirst(self.queue(), function (item) {
                return item.playing() === true;
            });
            if (song) {
                var position = $(player1).data("jPlayer").status.currentTime;
                if (position != null) {
                    $('#action_SaveProgress').fadeOut("slow").delay(500).fadeIn("slow").delay(500).fadeOut("slow").delay(500).fadeIn("slow");
                    song.position(position);
                    utils.setValue('CurrentSong', mapping.toJSON(song), false);
                    //if (settings.Debug()) { console.log('Saving Current Position: ' + JSON.stringify(song, null, 2)); }
                    // Save Play Queue
                    if (utils.browserStorageCheck()) {
                        var html = localStorage.getItem('CurrentPlaylist');
                        if (self.queue().length > 0) {
                            var current = mapping.toJSON(self.queue());
                            if (current != html) {
                                try {
                                    localStorage.setItem('CurrentPlaylist', current);
                                    if (settings.Debug()) { console.log('Saving Play Queue: ' + current.length + ' characters'); }
                                } catch (e) {
                                    if (e == QUOTA_EXCEEDED_ERR) {
                                        alert('Quota exceeded!');
                                    }
                                }
                            }
                        }
                    } else {
                        if (settings.Debug()) { console.log('HTML5::loadStorage not supported on your browser'); }
                    }
                }
            }
        }
    }
}
loadTrackPosition = function () {
    if (utils.getValue("CurrentSong") != false) {
        var song = mapping.fromJSON(utils.getValue("CurrentSong"));
        //var song = mapping.fromJSON(utils.getValue("CurrentSong"), global.songMapping);
        playSong(true, song);
        if (utils.browserStorageCheck()) {
            var data = localStorage.getItem('CurrentPlaylist');
            if (data != '' && data !== undefined && data !== null) {
                var map = {
                    create: function (options) {
                        return mapping.fromJS(options.data);
                    }
                }
                mapping.fromJSON(data, map, self.queue);
                if (settings.Debug()) { console.log('Play Queue Loaded From localStorage: ' + self.queue().length + ' song(s)'); }
            }
        } else {
            if (settings.Debug()) { console.log('HTML5::loadStorage not supported on your browser'); }
        }
    }
}
deleteCurrentPlaylist = function (data) {
    if (utils.browserStorageCheck()) {
        localStorage.removeItem('CurrentPlaylist');
        utils.setValue('CurrentSong', null, false);
        if (settings.Debug()) { console.log('Removing Play Queue'); }
    } else {
        if (settings.Debug()) { console.log('HTML5::loadStorage not supported on your browser, ' + html.length + ' characters'); }
    }
}
playSong = function (loadonly, data) {
    if (settings.Debug()) { console.log('Play: ' + JSON.stringify(ko.toJS(data), null, 2)); }
    self.playingSong(data);
    ko.utils.arrayForEach(self.queue(), function (item) {
        item.playing(false);        
    });
    data.playing(true);

    var id = data.id();
    var url = data.url();
    var position = data.position();
    var title = data.name();
    var album = data.album();
    var artist = data.artist();
    var suffix = data.suffix();
    var specs = data.specs();
    var coverartthumb = data.coverartthumb();
    var coverartfull = data.coverartfull();
    var starred = data.starred();
    $('#playermiddle').css('visibility', 'visible');
    $('#songdetails').css('visibility', 'visible');
    
    /*
    if (player != null) {
        //loadjPlayer('#playdeck_1', url, suffix, false, position);
        if (settings.Debug()) { console.log(currentPlayer + ' currently playing, switching player'); }
        if (currentPlayer == player1) {
            $(player1).jPlayer("stop");
            $(player1).jPlayer("destroy");
            $(player2).jPlayer("play", 0);
            currentPlayer = player2;
        } else {
            $(player2).jPlayer("stop");
            $(player2).jPlayer("destroy");
            $(player1).jPlayer("play", 0);
            currentPlayer = player1;
        }
    } else {
        player = loadjPlayer(player1, url, suffix, false, position);
        currentPlayer = player1;
    }
    // Preload
    var next = getNextSong();
    if (next) {
        if (settings.Debug()) { console.log('Starting preload of: ' + next.url()); }
        if (currentPlayer == player1) {
            loadjPlayer(player2, next.url(), next.suffix(), true, 0);  
        } else {
            loadjPlayer(player1, next.url(), next.suffix(), true, 0);  
        }
    }
    */
    loadjPlayer(player1, url, suffix, loadonly, position);
    $('#Queue').stop().scrollTo('#' + id, 400);
    if (utils.getValue('SaveTrackPosition')) {
        if (timerid != 0) {
            clearInterval(timerid);
        }
        timerid = window.setInterval(function () {
            if (utils.getValue('SaveTrackPosition')) {
                saveTrackPosition();
            }
        }, 30000);
    }
    var spechtml = '';
    var data = $(player1).data().jPlayer;
    for (i = 0; i < data.solutions.length; i++) {
        var solution = data.solutions[i];
        if (data[solution].used) {
            spechtml += "<strong class=\"codesyntax\">" + solution + "</strong> is";
            spechtml += " currently being used with<strong>";
            for (format in data[solution].support) {
                if (data[solution].support[format]) {
                    spechtml += " <strong class=\"codesyntax\">" + format + "</strong>";
                }
            }
            spechtml += "</strong> support";
        }
    }
    $('#SMStats').html(spechtml);
    scrobbleSong(false);
    scrobbled = false;

    if (settings.NotificationSong() && !loadonly) {
        utils.showNotification(coverartthumb, utils.toHTML.un(title), utils.toHTML.un(artist + ' - ' + album), 'text', '#NextTrack');
    }
    if (settings.ScrollTitle()) {
        var title = utils.toHTML.un(artist) + ' - ' + utils.toHTML.un(title);
        utils.scrollTitle(title);
    } else {
        utils.setTitle(utils.toHTML.un(artist) + ' - ' + utils.toHTML.un(title));
    }
};

function loadjPlayer(el, url, suffix, loadonly, position) {
    // jPlayer Setup
    var volume = 1;
    if (utils.getValue('Volume')) {
        volume = parseFloat(utils.getValue('Volume'));
    }
    var audioSolution = "html,flash";
    if (utils.getValue('ForceFlash')) {
        audioSolution = "flash,html";
    }
    //var salt = Math.floor(Math.random() * 100000);
    //url += '&salt=' + salt;
    $(el).jPlayer("destroy");
    $.jPlayer.timeFormat.showHour = true; 
    $(el).jPlayer({
        swfPath: "js/jplayer",
        wmode: "window",
        solution: audioSolution,
        supplied: suffix,
        volume: volume,
        errorAlerts: false,
        warningAlerts: false,
        cssSelectorAncestor: "#player",
        cssSelector: {
            play: "#PlayTrack",
            pause: "#PauseTrack",
            seekBar: "#audiocontainer .scrubber",
            playBar: "#audiocontainer .progress",
            mute: "#action_Mute",
            unmute: "#action_UnMute",
            volumeMax: "#action_VolumeMax",
            currentTime: "#played",
            duration: "#duration"
        },
        ready: function () {
            if (suffix == 'oga') {
                $(this).jPlayer("setMedia", {
                    oga: url,
                });
            } else if (suffix == 'mp3') {
                $(this).jPlayer("setMedia", {
                    mp3: url,
                });
            }
            if (!loadonly) { // Start playing
                $(this).jPlayer("play");
                /* Uncomment to enable Unity shim
                var playerState = {
                    playing: true,
                    title: title,
                    artist: artist,
                    favorite: false,
                    albumArt: coverartFullSrc
                }
                if (unity) {
                    unity.sendState(playerState);
                }
                */
            } else { // Loadonly
                //$('#' + songid).addClass('playing');
                $(this).jPlayer("pause", position);
            }
            if (settings.Debug()) {
                console.log('[jPlayer Version Info]');
                utils.logObjectProperties($(el).data("jPlayer").version);
                console.log('[HTML5 Debug Info]');
                utils.logObjectProperties($(el).data("jPlayer").html);
                console.log('[Flash Debug Info]');
                utils.logObjectProperties($(el).data("jPlayer").flash);
                console.log('[jPlayer Options Info]');
                utils.logObjectProperties($(el).data("jPlayer").options);
            }
		},
        timeupdate: function(event) {
            // Scrobble song once percentage is reached
            var p = event.jPlayer.status.currentPercentAbsolute;
            if (!scrobbled && p > 30) {
                if (settings.Debug()) { console.log('LAST.FM SCROBBLE - Percent Played: ' + p); }
                scrobbleSong(true);
            }
        },
        volumechange: function(event) {
            utils.setValue('Volume', event.jPlayer.options.volume, true);
        },
        ended: function(event) {
            if (settings.Repeat()) { // Repeat current track if enabled
                $(this).jPlayer("play");
            } else {
                if (!getNextSong()) { // Action if we are at the last song in queue
                    if (settings.LoopQueue()) { // Loop to first track in queue if enabled
                        var next = self.queue()[0];
                        playSong(false, next);                
                    } else if (settings.AutoPlay()) { // Load more tracks if enabled
                        subsonic.getRandomSongs('play', '', '');
                    }
                } else {
                    nextTrack();
                }
            }
        },
        error: function(event) {
            var time = $(player1).data("jPlayer").status.currentTime;
            $(player1).jPlayer("play", time);
            if (settings.Debug()) { 
                console.log("Error Type: " + event.jPlayer.error.type); 
                console.log("Error Context: " + event.jPlayer.error.context); 
                console.log("Error Message: " + event.jPlayer.error.message); 
                console.log("Stream interrupted, retrying from position: " + time);
            }
        }
    });
    return;
}

function playPauseSong() {
    if (typeof $(player1).data("jPlayer") != 'undefined') {
        if ($(player1).data("jPlayer").status.paused) {
            $(player1).jPlayer("play");
        } else {
            $(player1).jPlayer("pause");
        }
    } 
}

function playVideo(id, bitrate) {
    var w, h;
    bitrate = parseInt(bitrate);
    if (bitrate <= 600) { 
        w = 320; h = 240; 
    } else if (bitrate <= 1000) { 
        w = 480; h = 360; 
    } else { 
        w = 640; h = 480; 
    } 
    //$("#jPlayerSelector").jPlayer("option", "fullScreen", true);
    $("#videodeck").jPlayer({
		ready: function () {
            /*
            $.fancybox({
                autoSize: false,
                width: w + 10,
                height: h + 10,
                content: $('#videodeck')
            });
            */
			$(this).jPlayer("setMedia", {
				m4v: 'https://&id=' + id + '&salt=83132'
			}).jPlayer("play");
            $('#videooverlay').show();
		},
		swfPath: "js/jplayer",
		solution: "html, flash",
		supplied: "m4v"
	});
}
function scrobbleSong(submission) {
    var songid = $('#songdetails li.song').attr('id');
    if (typeof songid != 'undefined' && settings.Username != '' && settings.Server() != '') {
        if (settings.Debug()) { console.log('Scrobble Song: ' + songid); }
        $.ajax({
            url: settings.BaseURL() + '/scrobble.view?' + settings.BaseParams() + '&id=' + songid + "&submission=" + submission,
            method: 'GET',
            dataType: settings.Protocol(),
            timeout: 10000,
            success: function () {
                if (submission) {
                    scrobbled = true;
                }
            }
        });
    } else {
        if (submission) {
            scrobbled = true;
        }
    }
}
function rateSong(songid, rating) {
    $.ajax({
        url: baseURL + '/setRating.view?' + baseParams + '&id=' + songid + "&rating=" + rating,
        method: 'GET',
        dataType: protocol,
        timeout: 10000,
        success: function () {
            updateMessage('Rating Updated!', true);
        }
    });
}

    return {
        defaultPlay: defaultPlay,
        nextTrack: nextTrack,
        playSong: playSong,
        playPauseSong: playPauseSong,
        saveTrackPosition: saveTrackPosition,
        loadTrackPosition: loadTrackPosition,
        deleteCurrentPlaylist: deleteCurrentPlaylist
    };
});