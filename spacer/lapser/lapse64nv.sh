#!/bin/sh
ffmpeg -c:v h264_cuvid -i "$1" -vf "tblend=average,framestep=2,tblend=average,framestep=2,tblend=average,framestep=2,tblend=average,framestep=2,tblend=average,framestep=2,tblend=average,framestep=2,setpts=0.015625*PTS" -an -r 30 -c:v h264_nvenc -profile:v high -preset:v default -b:v 12000k "$2"
