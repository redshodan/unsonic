require.config({
    paths: {
        'knockout': 'plugins/knockout-2.2.1',
        'mapping': 'plugins/knockout.mapping-latest',
        'postbox': 'plugins/knockout-postbox.min',
        'jquery': 'plugins/jquery-1.8.3',
        'jqueryui': 'plugins/jquery-ui-1.9.2.custom.min',
        'jquery.layout': 'plugins/jquery.layout-latest',
        'jquery.cookie': 'plugins/jquery.cookie',
        'jquery.fancybox': 'plugins/fancybox/jquery.fancybox.pack',
        'jquery.scrollTo': 'plugins/jquery.scrollTo.min',
        'sammy': 'plugins/sammy-latest.min',
        'jplayer': 'jplayer/jquery.jplayer.min',
        'model': 'model',
        'global': 'global',
        'utils': 'utils',
        'player': 'player'
    },
    shim: {
        "jqueryui": {
            exports: "$",
            deps: ['jquery']
        },
        'jquery.layout':{
            deps: ['jqueryui']
        },
        'jquery.cookie': {
            deps: ['jquery']
        },
        'jquery.fancybox':{
            deps: ['jquery']
        },
        'jquery.scrollTo':{
            deps: ['jquery']
        },
        'sammy': {
            deps: ['jquery'],
            exports: 'Sammy'
        },
        'jplayer': {
            deps: ['jquery'],
            exports: 'jPlayer'
        }
    },
    baseUrl: "js"
}); 
require(['jquery', 'knockout', 'sammy', 'global', 'utils', 'mainViewModel', 'player', 'jqueryui', 'jquery.layout', 'jquery.fancybox'], function ($, ko, Sammy, global, utils, mainViewModel, player) {
    var self = this;

    $('.noselect').disableSelection();

    $.ajaxSetup({
        'beforeSend': function () {
            $("#loading").show();
        },
        'complete': function () {
            $("#loading").hide();
        }
    });

    var submenu_active = false;
    $('div.submenu').mouseenter(function () {
        submenu_active = true;
    });
    $('div.submenu').mouseleave(function () {
        submenu_active = false;
        $('div.submenu').hide();
        //setTimeout(function () { if (submenu_active == false) $('div.submenu').stop().fadeOut(); }, 400);
    });

    $("a#coverartimage").fancybox({
        beforeShow : function() {
            //this.title = $('#songdetails_artist').html();
        },
        afterLoad : function() {
            //this.inner.prepend( '<h1>1. My custom title</h1>' );
            //this.content = '<h1>2. My custom title</h1>';
        },
        hideOnContentClick: true,
        type: 'image',
        openEffect: 'none',
        closeEffect: 'none',
    });

    $('#audiocontainer .scrubber').mouseover(function (e) {
        $('.audiojs .scrubber').stop().animate({ height: '8px' });
    });
    $('#audiocontainer .scrubber').mouseout(function (e) {
        $('.audiojs .scrubber').stop().animate({ height: '4px' });
    });

    // JQuery UI Sortable - Drag and drop sorting
    var fixHelper = function (e, ui) {
        ui.children().each(function () {
            $(this).width($(this).width());
        });
        return ui;
    };
    $("#tabQueue ul.songlist").sortable({
        helper: fixHelper
    }).disableSelection();

    // JQuery Layout Plugin
    var layoutOptions = {
        east__size: .5,
        east__minSize: 400,
        east__maxSize: .5, // 50% of layout width
        east__initClosed: false,
        east__initHidden: false,
        //center__size: 'auto',
        center__minWidth: .3,
        center__initClosed: false,
        center__initHidden: false,
        west__size: .2,
        west__minSize: 200,
        west__initClosed: false,
        west__initHidden: false,
        //stateManagement__enabled: true, // automatic cookie load & save enabled by default
        showDebugMessages: true // log and/or display messages from debugging & testing code
        //applyDefaultStyles: true
    };
    $('#SubsonicAlbums').layout(layoutOptions);

    // Custom Binding for (stopBinding: true)
    ko.bindingHandlers.stopBinding = {
        init: function () {
            return { controlsDescendantBindings: true };
        }
    };
    //KO 2.1, now allows you to add containerless support for custom bindings
    //ko.virtualElements.allowedBindings.stopBinding = true;

    // Custom Binding for Enter Key (Use on input, returnKey: function)
    ko.bindingHandlers.returnKey = {
        init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
            ko.utils.registerEventHandler(element, 'keydown', function (evt) {
                if (evt.keyCode === 13) {
                    evt.preventDefault();
                    evt.target.blur();
                    valueAccessor().call(viewModel);
                }
            });
        }
    };

    ko.bindingHandlers.templateWithContext = {
        init: function() {
            return ko.bindingHandlers.template.init.apply(this, arguments);
        },
        update: function(element, valueAccessor) {
            var options = ko.utils.unwrapObservable(valueAccessor());

            if (options.context) {
                options.context.data = options.data;
                options.data = options.context;  
                delete options.context;
            }

            ko.bindingHandlers.template.update.apply(this, arguments); 
        } 
    };           

    ko.applyBindings(new mainViewModel());
    //ko.applyBindings(subsonicViewModel, $('#tabLibrary')[0]);

    // Variable Init
    if (global.settings.SaveTrackPosition()) {
        player.loadTrackPosition();
    }
    if (global.settings.Theme() == 'Dark') {
        utils.switchTheme(global.settings.Theme());
    }

});