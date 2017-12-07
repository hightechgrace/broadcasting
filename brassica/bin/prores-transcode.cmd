@echo off
setlocal enabledelayedexpansion

set DEST=F:\Transcode
set ACCEL=-hwaccel dxva2
set OPTS=-y -codec:v prores -profile:v 3 -qscale:v 12 -pix_fmt yuv422p10le

for %%i in (%1 %2 %3 %4 %5 %6 %7 %8 %9) do (
	set SRC=%%i
	set TMP="%DEST%\temp-%%~ni.mov"
	set FINAL="%DEST%\%%~ni.mov"
	ffmpeg %ACCEL% -i !SRC! %OPTS% !TMP! && move !TMP! !FINAL! && echo Wrote !FINAL!
)
