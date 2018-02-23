var Jimp = require('jimp');
var async = require('async')
var fs = require('fs');
var path = require('path');

var dir = '/var/rec';

module.exports = function (T, cb) {
    fs.readdir(dir, function (err, files) {
        if (err) return cb(err);

        // Keyframe-looking files, starting with recent ones
        var candidates = files.filter( function (f) {
            return f.startsWith('kf-') && f.endsWith('.png');
        });
        candidates.sort();
        candidates.reverse();

        // Post the latest one we can parse and compress
        async.detectSeries(candidates, function (item, series_cb) {
            Jimp.read(path.join(dir, item), function (err, img) {
                if (err) series_cb(null, false);  // Not an image, skip it
                img.getBuffer(Jimp.MIME_JPEG, function (err, jpg) {
                    if (T) {
                        T.post('media/upload', { media_data: jpg.toString('base64') }, cb);
                    } else {
                        // Mock for testing without a twitter client
                        console.log('Would have uploaded', item);
                        cb(null, { media_id_string: '' });
                    }
                    series_cb(null, true);
                });
            })
        });
    });
}
