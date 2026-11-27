#!/bin/bash
# Joins a Seedance video with the transparent end card:
# the last frame is held, a soft white veil fades in, and the logo and text animate on top.
#   bash src/sostavi-reklama.sh seedance.mp4 out.mp4
set -e
IN="$1"; OUT="$2"; HERE="$(cd "$(dirname "$0")" && pwd)"
FR=$(mktemp -d)
node "$HERE/render-overlay.js" overlay-dental.html "$FR" >/dev/null
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
HOLD=3.8
T=$(python3 -c "print(round($D+$HOLD,2))")
START=$(python3 -c "print(round($D-0.6,2))")
ffmpeg -y -loglevel error -i "$IN" -framerate 30 -i "$FR/o%04d.png" -filter_complex "\
[0:v]scale=1080:1920:flags=lanczos,fps=30,setsar=1,tpad=stop_mode=clone:stop_duration=$HOLD,format=rgba[base];\
color=c=white:s=1080x1920:r=30:d=$T,format=rgba,colorchannelmixer=aa=0.6,fade=t=in:st=$START:d=0.9:alpha=1[veil];\
[base][veil]overlay=shortest=1[b2];\
[1:v]setpts=PTS-STARTPTS+$START/TB[ov];\
[b2][ov]overlay=eof_action=pass,format=yuv420p[v];\
[0:a]aresample=48000,apad=whole_dur=$T,afade=t=out:st=$(python3 -c "print(round($D-1,2))"):d=$(python3 -c "print(round($HOLD+1,2))")[a]" \
-map "[v]" -map "[a]" -t $T -c:v libx264 -crf 18 -preset slow -c:a aac -b:a 192k -movflags +faststart "$OUT"
rm -rf "$FR"
echo "$OUT ($T s)"
