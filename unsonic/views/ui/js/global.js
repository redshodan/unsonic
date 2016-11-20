define(['knockout', 'utils', 'model'], function (ko, utils, model) {
    var self = this;
    // 1. Default Values
    self.settings = {
        // Subsonic
        Username: ko.observable("%user%"),
        Server: ko.observable("%home%"),
        BaseURL: ko.observable("%rest%"),
        Protocol: ko.observable("jsonp"),
        Protocols: new ko.observableArray(["json", "jsonp"]),
        ApplicationName: ko.observable("Jamstash"),
        ApiVersion: ko.observable("1.6.0"),
        AutoPlaylists: ko.observable(""),
        AutoPlaylistSize: ko.observable(25),
        AutoAlbumSize: ko.observable(15),
        // General
        HideAZ: ko.observable(true),
        ScrollTitle: ko.observable(true),
        NotificationSong: ko.observable(false),
        NotificationNowPlaying: ko.observable(false),
        SaveTrackPosition: ko.observable(false),
        ForceFlash: ko.observable(false),
        Theme: ko.observable("Default"),
        Themes: new ko.observableArray(["Default", "Dark"]),
        AutoPlay: ko.observable(false),
        LoopQueue: ko.observable(false),
        Repeat: ko.observable(false),
        Debug: ko.observable(false)
    };
    /* For Basic Authentication
    settings.Auth = ko.computed(function () {
    return makeBaseAuth(settings.Username(), settings.Password().substring(4, settings.Password().length).hexDecode());
    });
    */
    self.settings.BaseParams = ko.computed(function () {
        return 'u=' + '&f=' + self.settings.Protocol() + '&v=' + self.settings.ApiVersion() + '&c=' + self.settings.ApplicationName();
    });

    // 2. Reads cookies and sets defaults, overwriting above initialization
    self.loadSettings = function () {
        var exclude = ["Auth", "BaseURL", "BaseParams"];
        $.each(self.settings, function (key, value) {
            if ($.inArray(key, exclude) == -1) {
                if (utils.getValue(key)) {
                    var v = utils.getValue(key);
                    if (v == 'false') { v = false; }
                    if (v == 'true') { v = true; }
                    self.settings[key](v);
                }
            }
        });
        if (self.settings.Debug()) { console.log('Settings: ' + JSON.stringify(ko.toJS(self.settings), null, 2)); }
    }
    self.loadSettings();

    // 3. Bind to value change AutoSave Form Values (Subscribe AFTER initial values are set/loaded)
    self.settings.Protocol.subscribe(function (newValue) { utils.setValue('Protocol', newValue, true); });
    self.settings.ApplicationName.subscribe(function (newValue) { utils.setValue('ApplicationName', newValue, true); });
    self.settings.AutoPlaylists.subscribe(function (newValue) { utils.setValue('AutoPlaylists', newValue, true); });
    self.settings.AutoPlaylistSize.subscribe(function (newValue) { utils.setValue('AutoPlaylistSize', newValue, true); });
    self.settings.AutoAlbumSize.subscribe(function (newValue) { utils.setValue('AutoAlbumSize', newValue, true); });
    self.settings.HideAZ.subscribe(function (newValue) {
        utils.setValue('HideAZ', newValue, true);
        if (newValue) {
            $('#BottomContainer').hide();
        } else {
            $('#BottomContainer').show();
        }
    });
    self.settings.ScrollTitle.subscribe(function (newValue) { utils.setValue('ScrollTitle', newValue, true); });
    self.settings.NotificationSong.subscribe(function (newValue) {
        utils.requestPermissionIfRequired();
        if (utils.hasNotificationPermission()) {
            utils.setValue('NotificationSong', newValue, true);
        } else {
            alert('HTML5 Notifications are not available for your current browser, Sorry :(');
            return false;
        }
    });
    self.settings.NotificationNowPlaying.subscribe(function (newValue) {
        utils.requestPermissionIfRequired();
        if (utils.hasNotificationPermission()) {
            utils.setValue('NotificationNowPlaying', newValue, true);
        } else {
            alert('HTML5 Notifications are not available for your current browser, Sorry :(');
            return false;
        }
    });
    self.settings.SaveTrackPosition.subscribe(function (newValue) {
        utils.setValue('SaveTrackPosition', newValue, true);
        if (newValue) {
            saveTrackPosition();
        } else {
            utils.setValue('CurrentSong', null, false);
            deleteCurrentPlaylist();
        }
    });
    self.settings.ForceFlash.subscribe(function (newValue) { utils.setValue('ForceFlash', newValue, true); });
    self.settings.AutoPlay.subscribe(function (newValue) { utils.setValue('AutoPlay', newValue, true); });
    self.settings.LoopQueue.subscribe(function (newValue) { utils.setValue('LoopQueue', newValue, true); });
    self.settings.Repeat.subscribe(function (newValue) { utils.setValue('Repeat', newValue, true); });
    self.settings.Theme.subscribe(function (newValue) {
        utils.switchTheme(newValue);
        utils.setValue('Theme', newValue, true);
    });
    self.settings.Debug.subscribe(function (newValue) { utils.setValue('Debug', newValue, true); });

    self.songMapping = {
        create: function (options) {
            var song = options.data;
            var url, track, rating, starred, contenttype, suffix, description;
            var specs = '', coverartthumb = '', coverartfull = '';
            if (typeof song.coverArt != 'undefined') {
                coverartthumb = self.settings.BaseURL() + '/getCoverArt.view?' + self.settings.BaseParams() + '&size=60&id=' + song.coverArt;
                coverartfull = self.settings.BaseURL() + '/getCoverArt.view?' + self.settings.BaseParams() + '&id=' + song.coverArt;
            }
            if (typeof song.description == 'undefined') { description = ''; } else { description = song.description; }
            if (typeof song.track == 'undefined') { track = '&nbsp;'; } else { track = song.track; }
            if (typeof song.starred !== 'undefined') { starred = true; } else { starred = false; }
            if (song.bitRate !== undefined) { specs += song.bitRate + ' Kbps'; }
            if (song.transcodedSuffix !== undefined) { specs += ', transcoding:' + song.suffix + ' > ' + song.transcodedSuffix; } else { specs += ', ' + song.suffix; }
            if (song.transcodedSuffix !== undefined) { suffix = song.transcodedSuffix; } else { suffix = song.suffix; }
            if (suffix == 'ogg') { suffix = 'oga'; }
            var salt = Math.floor(Math.random() * 100000);
            url = self.settings.BaseURL() + '/stream.view?' + self.settings.BaseParams() + '&id=' + song.id + '&salt=' + salt;
            return new model.Song(song.id, song.parent, track, song.title, song.artist, song.artistId, song.album, song.albumId, coverartthumb, coverartfull, song.duration, song.userRating, starred, suffix, specs, url, 0, description);
        }
    }
    // <a href=\"\" target=\"_blank\"></a>
    /*
    { date: "", version: "", changes: 
    [{ text: "- "}]
    },
    */
    self.changeLog = [
      { date: "TBD", version: "0.1", changes: [{ text: "0.1 Initial Release"}] }
    ]

    return {
        changeLog: self.changeLog,
        settings: self.settings,
        songMapping: self.songMapping
    };
});