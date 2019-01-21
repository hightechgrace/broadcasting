#!/usr/bin/env python

import os, time, subprocess, re

class MovieConverter:

    def __init__(self, inputDirs, outputDir, inputSuffixes=['.mov', '.mkv', '.flv']):
        self.inputDirs = inputDirs
        self.outputDir = outputDir
        self.inputSuffixes = inputSuffixes
        self._lastInputs = []

    def _collectInputSizes(self):
        files = []
        for d in self.inputDirs:
            for f in os.listdir(d):
                if os.path.splitext(f)[1] in self.inputSuffixes:
                    p = os.path.join(d, f)
                    try:
                        filesize = os.stat(p).st_size
                    except OSError:
                        continue
                    files.append((p, filesize))
        return files

    def poll(self):
        inputs = self._collectInputSizes()
        for fileAndSize in inputs:
            if fileAndSize in self._lastInputs:
                # File has been present and the same size for two cycles
                self.processFile(fileAndSize[0])
        self._lastInputs = inputs

    def _outFile(self, slug, speedup):
        return os.path.join(self.outputDir, '%s-x%d.mp4' % (slug, speedup))

    def processFile(self, original):
        slug = re.sub(r'^-', '', re.subn(r'[/\\]', '-', os.path.splitext(original)[0])[0])
        self._remux(original, os.path.join(self.outputDir, '%s-remux.mp4' % slug))
        self._lapserStage(original, self._outFile(slug, 16), 4)
        self._lapserStage(self._outFile(slug, 16), self._outFile(slug, 32), 1)
        self._lapserStage(self._outFile(slug, 16), self._outFile(slug, 64), 2)
        self._lapserStage(self._outFile(slug, 16), self._outFile(slug, 128), 3)
        self._lapserStage(self._outFile(slug, 16), self._outFile(slug, 256), 4)
        self._lapserStage(self._outFile(slug, 256), self._outFile(slug, 512), 1)
        self._lapserStage(self._outFile(slug, 256), self._outFile(slug, 1024), 2)
        self._lapserStage(self._outFile(slug, 256), self._outFile(slug, 2048), 3)
        self._lapserStage(self._outFile(slug, 256), self._outFile(slug, 4096), 4)

    def _remux(self, input, output):
        self._ffmpeg(['-i', input, '-c:v', 'copy', '-c:a', 'copy'], output)

    def _lapserStage(self, input, output, log2):
        vf = ('tblend=average,framestep=2,' * log2) + ('setpts=%f*PTS' % (1.0 / (1 << log2)))
        self._ffmpeg([
            '-c:v', 'h264_cuvid',
            '-i', input,
            '-vf', vf,
            '-an', '-r', '30',
            '-c:v', 'h264_nvenc', '-profile:v', 'high',
            '-preset:v', 'default', '-b:v', '12000k'
        ], output)

    def _ffmpeg(self, options, output):
        tempout = os.path.join(os.path.dirname(output), 'temp-' + os.path.basename(output))
        if os.path.isfile(tempout):
            os.unlink(tempout)
        try:
            if not os.path.isfile(output):
                try:
                    subprocess.check_call(['ffmpeg'] + options + [tempout])
                    os.rename(tempout, output)
                except subprocess.CalledProcessError:
                    pass
        finally:
            if os.path.isfile(tempout):
                os.unlink(tempout)


if __name__ == '__main__':
    mc = MovieConverter([
        '/mnt/colorburst/obs',
        '/mnt/brassica',
        '/mnt/cylindroid/obs',
        '/mnt/podcaster',
    ],  '/mnt/colorburst/lapser')
    while True:
        time.sleep(15)
        mc.poll()
