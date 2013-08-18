define(['knockout', 'postbox', 'mapping', 'global', 'utils', 'model', 'player'], function (ko, postbox, mapping, global, utils, model, player) {
    return function () {
        var self = this;
        self.artist = new ko.observableArray([]);
        self.album = new ko.observableArray([]);
        self.song = new ko.observableArray([]);

        self.settings = global.settings;

        self.queue = new ko.observableArray([]).syncWith("queue");
        self.selectedArtist = ko.observable();
        self.selectedAlbum = ko.observable();
        self.selectedSongs = new ko.observableArray([]);
        self.selectSong = function (data, event) {
            if (self.selectedSongs.indexOf(this) >= 0) {
                self.selectedSongs.remove(this);
                this.selected(false);
            } else {
                self.selectedSongs.push(this);
                this.selected(true);
            }
        }
        self.addSongsToQueue = function (data, event) {
            ko.utils.arrayForEach(self.selectedSongs(), function (item) {
                self.queue.push(item);
                item.selected(false);
            });
            utils.updateMessage(self.selectedSongs().length + ' Song(s) Added to Queue', true);
        }

        self.archiveUrl = 'https://archive.org/';
        self.protocol = 'jsonp';

        self.AllCollections = global.archiveCollections;
        self.selectedCollectionChange = function (data, event) {
            var val = event.currentTarget.value;
            if (self.settings.SavedCollections()) {
                self.settings.SavedCollections(self.settings.SavedCollections() + ', ' + val)
            } else {
                self.settings.SavedCollections(val);
            }
            self.artist.push(new model.Artist('', val));
        };
        self.getArtists = function (data) {
            var map = {
                create: function (options) {
                    return new model.Artist('', options.data);
                }
            };
            mapping.fromJS(self.settings.SavedCollections().split(","), map, self.artist);
        };
        self.openLink = function (data, event) {
            return true;
        }
        self.selectedArchiveAlbumSort = ko.observable("date desc");
        self.ArchiveAlbumSort = new ko.observableArray([
        'addeddate desc',
        'addeddate asc',
        'avg_rating desc',
        'avg_rating asc',
        'createdate desc',
        'createdate asc',
        'date desc',
        'date asc',
        'downloads desc',
        'downloads asc',
        'num_reviews desc',
        'num_reviews asc',
        'publicdate desc',
        'publicdate asc',
        'stars desc',
        'stars asc'
        ]),
    self.selectedArchiveAlbumSort.subscribe(function (newValue) {
        if (utils.getValue('AlbumSort') != newValue) {
            if (typeof newValue != 'undefined') {
                utils.setValue('AlbumSort', newValue, true);
            } else {
                utils.setValue('AlbumSort', null, true);
            }
            //alert(newValue);
            self.getAlbums('');
        }
    });
        self.getAlbums = function (from) {
            var id, name;
            if (from == 'collection') {
                self.selectedArtist(this);
                id = this.id();
                name = this.name();
            } else {
                id = self.selectedArtist().id();
                name = self.selectedArtist().name();
            }
            var map = {
                create: function (options) {
                    var song = options.data;
                    var coverart, starred;
                    var url = self.archiveUrl + 'details/' + song.identifier;
                    coverart = 'images/albumdefault_50.jpg';
                    if (parseInt(song.avg_rating) == 5) { starred = true; } else { starred = false; }
                    //var description = '<b>Details</b><br />';
                    var description = '<b>Source</b>: ' + song.source + '<br />';
                    description += '<b>Date</b>: ' + song.date + '<br />';
                    description += typeof song.publisher != 'undefined' ? '<b>Transferer</b>: ' + song.publisher + '<br />' : '';
                    description += typeof song.avg_rating != 'undefined' ? '<b>Rating</b>: ' + song.avg_rating + '<br />' : '';
                    description += '<b>Downloads</b>: ' + song.downloads + '<br />';
                    //description += typeof song.description == 'undefined' ? '' : song.description.replace("\n", "<br />");
                    return new model.Album(song.identifier, null, song.title, null, coverart, null, starred, description, url);
                }
            }
            //var url = self.settings.BaseURL() + 'advancedsearch.php?q=collection%3A%28GreenskyBluegrass%29%20AND%20format%3A%28mp3%29&fl%5B%5D=avg_rating&fl%5B%5D=collection&fl%5B%5D=date&fl%5B%5D=description&fl%5B%5D=downloads&fl%5B%5D=headerImage&fl%5B%5D=identifier&fl%5B%5D=publicdate&fl%5B%5D=source&fl%5B%5D=subject&fl%5B%5D=title&format=mp3&sort%5B%5D=addeddate+desc&rows=50&page=1&output=json';
            var url = self.archiveUrl + 'advancedsearch.php?q=collection:(' + name + ') AND format:(MP3)';
            if (self.selectedSource()) {
                url += ' AND source:(' + self.selectedSource() + ')';
            }
            if (self.selectedYear()) {
                if (parseInt(self.selectedYear())) {
                    url += ' AND year:(' + self.selectedYear() + ')';
                }
            }
            if (self.selectedDescription()) {
                url += ' AND description:(' + self.selectedDescription() + ')';
            }
            url += '&fl[]=avg_rating,collection,date,description,downloads,headerImage,identifier,publisher,publicdate,source,subject,title,year';
            if (self.selectedArchiveAlbumSort()) {
                url += '&sort[]=' + self.selectedArchiveAlbumSort()
            }
            url += '&rows=50&page=1&output=json';
            $.ajax({
                url: url,
                method: 'GET',
                dataType: self.protocol,
                timeout: 10000,
                success: function (data) {
                    var items = [];
                    if (data["response"].docs.length > 0) {
                        items = data["response"].docs;
                        //alert(JSON.stringify(data["response"]));
                        mapping.fromJS(items, map, self.album);
                    } else {
                        utils.updateMessage("0 records returned", true);
                    }
                },
                error: function () {
                    alert('Archive.org service down :(');
                }
            });
        };
        self.selectedYear = ko.observable();
        self.getYears = function (startYear) {
            var currentYear = new Date().getFullYear(), years = [];
            startYear = startYear || 1950;

            while (startYear <= currentYear) {
                years.push(startYear++);
            }

            return years;
        }
        self.Years = new ko.observableArray(self.getYears()),
        self.selectedYear.subscribe(function (newValue) {
            if (typeof newValue != 'undefined') {
                self.getAlbums('');
            }
        });
        self.selectedSource = ko.observable();
        self.selectedSource.subscribe(function (newValue) {
            if (typeof newValue != 'undefined' && newValue != '') {
                self.getAlbums('');
            }
        });
        self.selectedDescription = ko.observable();
        self.selectedDescription.subscribe(function (newValue) {
            if (typeof newValue != 'undefined' && newValue != '') {
                self.getAlbums('');
            }
        });
        self.getSongs = function (id, action) {
            self.selectedAlbum(this);
            var url = self.archiveUrl + 'details/' + id + '?output=json';
            $.ajax({
                url: url,
                method: 'GET',
                dataType: self.protocol,
                timeout: 10000,
                success: function (data) {
                    var songs = [];
                    var url, time, track, title, rating, starred, contenttype, suffix;
                    var specs = '', coverartthumb = '', coverartfull = '';
                    var server = data.server;
                    var dir = data.dir;
                    if (typeof data.misc.image != 'undefined') {
                        //coverartthumb = self.settings.BaseURL() + data.misc.image;
                        coverartthumb = data.misc.image;
                        coverartfull = coverartthumb;
                    }
                    $.each(data.files, function (key, song) {
                        if (song.format == 'VBR MP3') {
                            url = 'http://' + server + dir + key;
                            specs = song.bitrate + 'kbps, ' + song.format.toLowerCase();
                            if (typeof song.track == 'undefined') { track = '&nbsp;'; } else { track = song.track; }
                            if (typeof song.title == 'undefined') { title = '&nbsp;'; } else { title = song.title; }
                            if (typeof song.length == 'undefined') { time = '&nbsp;'; } else { time = utils.timeToSeconds(song.length); }
                            songs.push(new model.Song(song.id, song.album, song.track, title, song.creator, '', song.album, '', coverartthumb, coverartfull, time, '', '', 'mp3', specs, url, 0, ''));
                        }
                    });
                    if (action == 'add') {
                        ko.utils.arrayForEach(songs, function (item) {
                            self.queue.push(item);
                        });
                        utils.updateMessage(self.queue().length + ' Song(s) Added to Queue', true);
                    } else if (action == 'play') {
                        self.queue(songs);
                        var next = self.queue()[0];
                        player.playSong(false, next);
                        utils.updateMessage(self.queue().length + ' Song(s) Added to Queue', true);
                    } else {
                        self.song(songs);
                    }
                }
            });
        };
        self.selectAll = function (data, event) {
            ko.utils.arrayForEach(self.song(), function (item) {
                self.selectedSongs.push(item);
                item.selected(true);
            });
        }
        self.selectNone = function (data, event) {
            ko.utils.arrayForEach(self.song(), function (item) {
                self.selectedSongs([]);
                item.selected(false);
            });
        }

        // Init
        self.getArtists();

        return {
            artist: self.artist,
            album: self.album,
            song: self.song,
            selectedArtist: self.selectedArtist,
            selectedAlbum: self.selectedAlbum,
            selectedSongs: self.selectedSongs,
            selectSong: self.selectSong,
            addSongsToQueue: self.addSongsToQueue,
            getArtists: self.getArtists,
            getAlbums: self.getAlbums,
            getSongs: self.getSongs,
            AllCollections: self.AllCollections,
            selectedCollectionChange: self.selectedCollectionChange,
            openLink: self.openLink,
            ArchiveAlbumSort: self.ArchiveAlbumSort,
            selectedArchiveAlbumSort: self.selectedArchiveAlbumSort,
            selectedYear: self.selectedYear,
            Years: self.Years,
            selectedSource: self.selectedSource,
            selectedDescription: self.selectedDescription,
            selectAll: self.selectAll,
            selectNone: self.selectNone
        };
    }
});