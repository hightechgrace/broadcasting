var Twit = require('twit')
var tracery = require('tracery-grammar')

var T = new Twit(require('./senriolabs_account.json'))

var grammar = tracery.createGrammar({

	'url': ['https://www.twitch.tv/senriolabs'],

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
	'secondContent': [ 'video', 'experiments', 'science', 'learning something new', 'warm socks' ],
	'lastContent': [ 'cat', 'cat', 'cat', 'kitty', 'little tiger', 'purr monster', 'fluff tiger' ],

	'first_tweet': ['#starting# #content# #url#'],
	'periodic_tweet': ['#continuing# #content# #url#']
});

grammar.addModifiers(tracery.baseEngModifiers);

function tweet(template) {
	var flat;
	do {
		flat = grammar.flatten(template);
	} while (flat.length > 140);
	if (T) {
		T.post('statuses/update', { status: flat }, function (err, data) {
			if (err) {
				console.log(err);
			} else {
				console.log('Tweet sent: ' + data.text);
			}
		});
	} else {
		console.log(flat);
	}
}

tweet('#first_tweet#');
setInterval( function () { tweet('#periodic_tweet#'); }, 95 * 60 * 1000);

