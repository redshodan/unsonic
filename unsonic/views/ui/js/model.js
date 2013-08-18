/// <reference path="../../js/plugins/knockout-2.2.1.debug.js" />
/// <reference path="../../js/plugins/knockout.mapping-latest.debug.js" />
define(['knockout', 'utils'], function (ko, utils) {
    var Index = function (name, artist) {
        this.name = ko.observable(name);
        this.artist = ko.observableArray(artist);
    }
    var Artist = function (id, name) {
        this.id = ko.observable(id);
        this.name = ko.observable(name);
    }
    var Album = function (id, parentid, name, artist, coverart, date, starred, description, url) {
        this.id = ko.observable(id);
        this.parentid = ko.observable(parentid);
        this.name = ko.observable(name);
        this.artist = ko.observable(artist);
        this.coverart = ko.observable(coverart);
        this.date = ko.observable(date);
        this.starred = ko.observable(starred);
        this.description = ko.observable(description);
        this.url = ko.observable(url);
    }
    var Song = function (id, parentid, track, name, artist, artistId, album, albumId, coverartthumb, coverartfull, duration, rating, starred, suffix, specs, url, position, description) {
        var self = this;
        this.id = ko.observable(id);
        this.parentid = ko.observable(parentid);
        this.track = ko.observable(track);
        this.name = ko.observable(name);
        this.artist = ko.observable(artist);
        this.artistId = ko.observable(artistId);
        this.album = ko.observable(album);
        this.albumId = ko.observable(albumId);
        this.coverartthumb = ko.observable(coverartthumb);
        this.coverartfull = ko.observable(coverartfull);
        this.duration = ko.observable(duration);
        this.time = ko.computed(function () {
            if (duration == '') {
                return '00:00'
            } else {
                return utils.secondsToTime(duration);
            }
        });
        //this.time = ko.observable(time);
        this.rating = ko.observable(rating);
        this.starred = ko.observable(starred);
        this.suffix = ko.observable(suffix);
        this.specs = ko.observable(specs);
        this.url = ko.observable(url);
        this.position = ko.observable(position);
        this.selected = ko.observable(false);
        this.playing = ko.observable(false);
        this.description = ko.observable(description);
        this.displayName = ko.computed(function () {
            return self.name() + " - " + self.album() + " - " + self.artist();
        });
    }
    var Option = function (value, text) {
        this.value = ko.observable(value);
        this.text = ko.observable(text);
    }
    return {
        Index: Index,
        Artist: Artist,
        Album: Album,
        Song: Song,
        Option: Option,
    };
});