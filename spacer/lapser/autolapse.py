#!/usr/bin/env python

import os, time, subprocess

class MovieConverter:

    def __init__(self, inputDirs, outputDir, inputSuffix='.mov'):
        self.inputDirs = inputDirs
        self.outputDir = outputDir
        self.inputSuffix = inputSuffix
        self._lastInputs = []

    def _collectInputSizes(self):
        files = []
        for d in self.inputDirs:
            for f in os.listdir(d):
                if f.endswith(self.inputSuffix):
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
        return os.path.join(self.outputDir, '%s-x%d.m4v' % (slug, speedup))

    def processFile(self, original):
        slug = os.path.basename(original[:-len(self.inputSuffix)])
        self._lapserStage(original, self._outFile(slug, 16), 4)
        self._lapserStage(self._outFile(slug, 16), self._outFile(slug, 32), 1)
        self._lapserStage(self._outFile(slug, 16), self._outFile(slug, 64), 2)
        self._lapserStage(self._outFile(slug, 16), self._outFile(slug, 128), 3)
        self._lapserStage(self._outFile(slug, 16), self._outFile(slug, 256), 4)
        self._lapserStage(self._outFile(slug, 256), self._outFile(slug, 512), 1)
        self._lapserStage(self._outFile(slug, 256), self._outFile(slug, 1024), 2)
        self._lapserStage(self._outFile(slug, 256), self._outFile(slug, 2048), 3)
        self._lapserStage(self._outFile(slug, 256), self._outFile(slug, 4096), 4)

    def _lapserStage(self, input, output, log2):
        if os.path.isfile(input) and not os.path.isfile(output):
            vf = ('tblend=average,framestep=2,' * log2) + ('setpts=%f*PTS' % (1.0 / (1 << log2)))
            subprocess.check_call(['ffmpeg', '-c:v', 'h264_cuvid', '-i', input, '-vf', vf, '-an', '-r', '30',
                '-c:v', 'h264_nvenc', '-profile:v', 'high', '-preset:v', 'default', '-b:v', '12000k', output])


if __name__ == '__main__':
    mc = MovieConverter([
        '/mnt/colorburst',
        '/mnt/brassica',
        '/mnt/cylindroid/obs'
    ],  '/mnt/colorburst')
    while True:
        mc.poll()
        time.sleep(5)
