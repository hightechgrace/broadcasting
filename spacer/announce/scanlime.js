var Gitter = require('node-gitter');
var Twit = require('twit');
var fs = require('fs');
var tracery = require('tracery-grammar');
var post_screenshot = require('./post-screenshot');

var timestamp_path = '/var/rec/scanlime.timestamp';
var tweet_length = 140;

//var minutes_between_tweets = 1;
//var this_is_not_a_test = false;
var minutes_between_tweets = 80;
var this_is_not_a_test = true;

var tMain = null;
var tBot = null;
var G = null;
if (this_is_not_a_test) {
    tMain = new Twit(require('./scanlime_account.json'));
    tBot = new Twit(require('./scanlimelive_account.json'));
    G = new Gitter(require('./gitter_account.json').token);
}

var grammar = tracery.createGrammar({

    'youtube_url': ['https://www.youtube.com/MElizabethScott/live'],
    'twitch_url': ['https://www.twitch.tv/scanlime'],
    'any_url': [ '#youtube_url#', '#twitch_url#' ],

    'main_hashtag': [ '\\#scanlimelive' ],
    'continued_hashtag': [ '\\#scanlimecont' ],

    'stream': [ 'stream', 'stream', 'stream', 'live stream', 'broadcast', 'vid stream', 'livestream' ],
    'started': [ 'started', 'started', 'started', 'going', 'going', 'up' ],
    'shop': [ 'shop', 'shop', 'lab', 'electronics lab' ],
    'exclam': [ '!', '!', '!', '!', '!', '~', '.', '.', '.', '.', '!!' ],
    'excomma': [ ',', '#exclam#' ],
    'excite': [ 'wow', 'whoa', 'neat', 'woww', 'cool' ],

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
    'first_tweet': ['#starting# #content# #main_hashtag# #any_url#'],
    'periodic_tweet': ['#continuing# #content# #continued_hashtag# #any_url#']
});

grammar.addModifiers(tracery.baseEngModifiers);

function tweet(template, media_ids) {
    var flat;
    do {
        flat = grammar.flatten(template);
    } while (flat.length > tweet_length);
    if (tBot) {
        tBot.post('statuses/update', { status: flat, media_ids: media_ids }, function (err, data) {
            if (err) {
                console.log(err);
            } else {
                console.log('Tweet ' + data.id_str + ' sent: ' + data.text);
                if (tMain) {
                    tMain.post('statuses/retweet/:id', { id: data.id_str }, function (err, data) {
                        console.log('Retweeted on main account');
                    });
                }
            }
        });
    } else {
        console.log('Would tweet: ', flat);
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

function minutes_since_last_tweet() {
    var mtime = 0;
    try {
        mtime = fs.statSync(timestamp_path).mtime.getTime();
    } catch (err) {}
    return (new Date().getTime() - mtime) / (60 * 1000.0);
}

if (minutes_since_last_tweet() > minutes_between_tweets) {
    tweet('#first_tweet#');
    gitter_post('#gitter_msg#');
}

setInterval( function () {
    if (minutes_since_last_tweet() > minutes_between_tweets) {
        post_screenshot( tBot, function (err, data) {
            tweet('#periodic_tweet#', [ data.media_id_string ] );
        });
    }
}, 10000);
