var Gitter = require('node-gitter'); 
var tracery = require('tracery-grammar');
var G = new Gitter(require('./gitter_account.json').token);

var grammar = tracery.createGrammar({

	'url': ['http://www.youtube.com/c/MElizabethScott/live'],

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

	'first_msg': ['#starting# #content# #url#'],
});

grammar.addModifiers(tracery.baseEngModifiers);
 
G.currentUser().then(function(user) {

	console.log('You are logged in as:', user.username);

	G.rooms.join('scanlime/live').then(function(room) {
		console.log('Joined room: ', room.name);

		var flat = grammar.flatten('#first_msg#');
		room.send(flat);
		console.log('Sent: ' + flat);
	})
});


setInterval( function () {
	console.log('Gitter bot still doing nothing');
}, 45 * 60 * 1000);
