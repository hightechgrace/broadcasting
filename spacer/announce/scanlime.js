var Gitter = require('node-gitter');
var Twit = require('twit');
var Mastodon = require('mastodon');
var fs = require('fs');
var tracery = require('tracery-grammar');
var Jimp = require('jimp');
var async = require('async')
var fs = require('fs');
var path = require('path');

var screenshot_dir = '/var/rec';
var temp_jpg_path = '/var/rec/scanlime.toot.jpg';
var timestamp_path = '/var/rec/scanlime.timestamp';
var social_post_length = 280;

//var minutes_between_posts = 1;
//var this_is_not_a_test = false;
var minutes_between_posts = 80;
var this_is_not_a_test = true;

var tMain = null;
var tBot = null;
var G = null;
var Toot = null;

if (this_is_not_a_test) {
    tMain = new Twit(require('./scanlime_account.json'));
    tBot = new Twit(require('./scanlimelive_account.json'));
    G = new Gitter(require('./gitter_account.json').token);
    Toot = new Mastodon(require('./socialcoop_account.json'));
} else {
    tMain = new Twit(require('./robotbabyhw_account.json'));
    tBot = new Twit(require('./robotbabyhw_account.json'));
    Toot = new Mastodon(require('./botsinspace_account.json'));
}

var grammar = tracery.createGrammar({

    'youtube_url': ['https://www.youtube.com/channel/UC8G48_G7suQlScUudVXyGkg/live'],
    'twitch_url': ['https://www.twitch.tv/scanlime'],
    'any_url': [ '#youtube_url#', '#twitch_url#' ],
    'both_urls': [ '#youtube_url# #twitch_url#', '#twitch_url# #youtube_url#' ],

    'main_hashtag': [ '\\#scanlimelive' ],
    'continued_hashtag': [ '\\#scanlimecont' ],

    'stream': [ 'stream', 'stream', 'stream', 'live stream', 'broadcast', 'vid stream', 'livestream' ],
    'started': [ 'started', 'started', 'started', 'going', 'going', 'up' ],
    'shop': [ 'shop', 'shop', 'lab', 'electronics lab' ],
    'exclam': [ '!', '!', '!', '!', '!', '~', '.', '.', '.', '.', '!!' ],
    'excomma': [ ',', '#exclam#' ],
    'excite': [ 'neat', 'cool', 'alright', 'yeah' ],

    'starting': [
        'Getting another #stream# #started##exclam#',
        'Going LIVE#exclam#',
        'Starting up another #stream#;',
        'Let\'s get another #stream# #started##exclam#',
        'Streaming now#exclam#',
        '#stream.capitalize# time#exclam#',
        'Broadcasting LIVE#exclam#',
        'Going LIVE from the #shop##exclam#',
    ],

    'continuing': [
        '#excite.capitalize##excomma# #stream.capitalize# is still going#exclam#',
        '#stream.capitalize# is still going#exclam#',
        '#stream.capitalize# still happening#exclam#',
        'Still #stream#ing#exclam#',
    ],

    'content': [
        '#firstContent.capitalize#, #secondContent#, and #lastContent##exclam#',
        '#firstContent.capitalize# & #lastContent##exclam#',
        '#firstContent.capitalize# & #lastContent##exclam#',
    ],

    'firstContent': [ 'electronics', 'electronics', 'hardware', 'hardware', 'engineering', 'widgets', 'circuits' ],
    'secondContent': [ 'video', 'experiments', 'science', 'reverse engineering', 'learning something', 'warm socks' ],
    'lastContent': [ 'cat', 'cat', 'cat', 'kitty', 'little tiger', 'purr monster', 'fluff tiger', 'fluffy labmate', 'Tuco the cat' ],

    'gitter_msg': ['#starting# #content# #youtube_url#'],
    'first_social_post': ['#starting# #content# #main_hashtag# #both_urls#'],
    'periodic_social_post': ['#continuing# #content# #continued_hashtag# #both_urls#']
});

grammar.addModifiers(tracery.baseEngModifiers);

function get_screenshot(cb)
{
    // let's rewrite this to use modern async and promises soon

    fs.readdir(screenshot_dir, function (err, files) {
        if (err) return cb(err);

        // Keyframe-looking files, starting with recent ones
        var candidates = files.filter( function (f) {
            return f.startsWith('kf-') && f.endsWith('.png');
        });
        candidates.sort();
        candidates.reverse();

        // Post the latest one we can parse and compress
        async.detectSeries(candidates, function (item, series_cb) {
            Jimp.read(path.join(screenshot_dir, item), function (err, img) {
                if (err) series_cb(null, false);  // Not an image, skip it
                img.getBuffer(Jimp.MIME_JPEG, function (err, jpg) {
                    cb(null, jpg);
                    series_cb(null, true);
                });
            });
        });
    });
}

function social_post(template, media) {
    var flat;
    do {
        flat = grammar.flatten(template);
    } while (flat.length > social_post_length);

    if (tBot) {
        function post_tweet(media_ids) {
            tBot.post('statuses/update', {
                status: flat, media_ids
            }, function (err, data) {
                if (err) {
                    console.log(err);
                } else {
                    console.log('Tweet ' + data.id_str + ' sent: ' + data.text);
                    if (tMain) {
                        tMain.post('statuses/retweet/:id', { id: data.id_str }, function (err) {
                            console.log('Retweeted on main account');
                        });
                    }
                }
            });
        }

        if (media) {
            tBot.post('media/upload', { media_data: media.toString('base64') }, function (err, data) {
                if (err) {
                    console.log(err);
                    post_tweet([]);
                } else {
                    post_tweet([ data.media_id_string ]);
                }
            });
        } else {
            post_tweet([]);
        }
    }

    if (Toot) {
        function post_toot(media_ids) {
            Toot.post('statuses', {
                status: flat,
                visibility: 'unlisted',
                spoiler_text: 'streaming bot',
                sensitive: false,
                media_ids
            }).then(function (resp) {
                console.log('Toot sent, ' + resp.data.uri);
            });
        }

        if (media) {
            fs.writeFile(temp_jpg_path, media, function (err) {
                if (err) return console.log(err);
                Toot.post('media', { file: fs.createReadStream(temp_jpg_path) }).then(function (resp) {
                    post_toot([ resp.data.id ]);
                });
            });
        } else {
            post_toot([]);
        }
    }

    fs.closeSync(fs.openSync(timestamp_path, 'w'));
}

function gitter_post(template) {
    var flat = grammar.flatten(template);
    if (G) {
        G.currentUser().then(function(user) {
            console.log('You are logged in as:', user.username);
            G.rooms.join('scanlime/live').then(function(room) {
                console.log('Joined room: ', room.name);
                room.send(flat);
                console.log('Sent: ' + flat);
            })
        });
    } else {
        console.log('Would post to gitter: ', flat);
    }
}

function minutes_since_last_post() {
    var mtime = 0;
    try {
        mtime = fs.statSync(timestamp_path).mtime.getTime();
    } catch (err) {}
    return (new Date().getTime() - mtime) / (60 * 1000.0);
}

if (minutes_since_last_post() > minutes_between_posts) {
    social_post('#first_social_post#');
    gitter_post('#gitter_msg#');
}

setInterval( function () {
    if (minutes_since_last_post() > minutes_between_posts) {
        get_screenshot(function (err, media_buffer) {
            social_post('#periodic_social_post#', media_buffer);
        });
    }
}, 10000);
