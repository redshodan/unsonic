define(['knockout', 'postbox', 'mapping', 'global', 'utils', 'model'], function (ko, postbox, mapping, global, utils, model) {
        var self = this;
        self.album = new ko.observableArray([]);
        self.song = new ko.observableArray([]).syncWith("song"); ;
        self.templateToUse = ko.observable();

        self.settings = global.settings;
        self.queue = new ko.observableArray([]).syncWith("queue");
        self.selectedArtist = ko.observable();
        self.selectedAlbum = ko.observable();
        self.selectedSongs = new ko.observableArray([]);
        
        self.getRandomSongs = function (action, genre, folder) {
            if (self.settings.Debug()) { console.log('action:' + action + ', genre:' + genre + ', folder:' + folder); }
            var size = self.settings.AutoPlaylistSize();
            var genreParams = '';
            if (genre != '' && genre != 'Random') {
                genreParams = '&genre=' + genre;
            }
            folderParams = '';
            if (typeof folder == 'number' && folder == 0 && folder != 'all') {
                folderParams = '&musicFolderId=' + folder;
            } else if (folder != '' && folder != 'all') {
                folderParams = '&musicFolderId=' + folder;
            }
            $.ajax({
                url: self.settings.BaseURL() + '/getRandomSongs.view?' + self.settings.BaseParams() + '&size=' + size + genreParams + folderParams,
                method: 'GET',
                dataType: self.settings.Protocol(),
                timeout: 10000,
                success: function (data) {
                    if (typeof data["subsonic-response"].randomSongs.song != 'undefined') {
                        var items = [];
                        if (data["subsonic-response"].randomSongs.song.length > 0) {
                            items = data["subsonic-response"].randomSongs.song;
                        } else {
                            items[0] = data["subsonic-response"].randomSongs.song;
                        }
                        if (action == 'add') {
                            var songs = mapping.fromJS(items, self.songMapping);
                            self.queue.push.apply(self.queue, songs());
                            utils.updateMessage(songs().length + ' Song(s) Added to Queue', true);
                        } else if (action == 'play') {
                            var songs = mapping.fromJS(items, self.songMapping);
                            self.queue.push.apply(self.queue, songs());
                            require("player").nextTrack();
                            utils.updateMessage(self.queue().length + ' Song(s) Added to Queue', true);
                        } else {
                            mapping.fromJS(items, self.songMapping, self.song);
                        }
                    }
                }
            });
        }
        self.updateFavorite = function (data, event) {
            var url;
            var id = data.id();
            if (typeof id !== 'undefined') {
                if (data.starred()) {
                    data.starred(false);
                    url = self.settings.BaseURL() + '/unstar.view?' + self.settings.BaseParams() + '&id=' + id;
                } else {
                    data.starred(true);
                    url = self.settings.BaseURL() + '/star.view?' + self.settings.BaseParams() + '&id=' + id;
                }
                $.ajax({
                    url: url,
                    method: 'GET',
                    dataType: self.settings.Protocol(),
                    timeout: 10000,
                    success: function () {
                        utils.updateMessage('Favorite Updated!', true);
                    }
                });
            }
        }
        

        return {
            getRandomSongs: self.getRandomSongs,
            updateFavorite: self.updateFavorite
        };
});