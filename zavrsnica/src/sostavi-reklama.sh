#!/bin/bash
# Joins a Seedance video with the transparent end card:
# the last frame is held, a soft white veil fades in, and the logo and text animate on top.
# Videos of 17 s or more: the card is drawn over the last 4 s and the original music is kept.
# Shorter videos: the last frame is held and a short musical ending in the same key is added under
# the logo (so the music resolves instead of stopping), and the mix is normalised to -14 LUFS.
#   bash src/sostavi-reklama.sh seedance.mp4 out.mp4 [key, e.g. C#; detected if omitted]
set -e
IN="$1"; OUT="$2"; KEY="$3"; HERE="$(cd "$(dirname "$0")" && pwd)"
TMP=$(mktemp -d)
node "$HERE/render-overlay.js" overlay-dental.html "$TMP/fr" >/dev/null
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
if python3 -c "import sys; sys.exit(0 if $D >= 17 else 1)"; then MODE=tail; else MODE=hold; fi
HOLD=3.8
T=$(python3 -c "print(round($D+$HOLD,2))")
START=$(python3 -c "print(round($D-0.6,2))")
STING_AT=$(python3 -c "print(round($D-0.5,2))")
STING_LEN=$(python3 -c "print(round($HOLD+0.5,2))")
if [ -z "$KEY" ]; then
  ffmpeg -y -loglevel error -i "$IN" -ac 1 -ar 32000 -f f32le "$TMP/a.raw"
  KEY=$(python3 - "$TMP/a.raw" <<'PY'
import sys, numpy as np
x=np.fromfile(sys.argv[1],dtype=np.float32); sr=32000; x=x[len(x)//3:]
n=8192; ch=np.zeros(12)
for i in range(0,len(x)-n,n//2):
    f=np.abs(np.fft.rfft(x[i:i+n]*np.hanning(n))); fr=np.fft.rfftfreq(n,1/sr); m=(fr>80)&(fr<2000)
    np.add.at(ch,(np.round(69+12*np.log2(fr[m]/440)).astype(int))%12,f[m]**2)
maj=np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
names=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
print(names[int(np.argmax([np.corrcoef(ch,np.roll(maj,k))[0,1] for k in range(12)]))])
PY
)
fi
if [ "$MODE" = tail ]; then
  START=$(python3 -c "print(round($D-4.0,2))")
  ffmpeg -y -loglevel error -i "$IN" -framerate 30 -i "$TMP/fr/o%04d.png" -filter_complex "\
[0:v]scale=1080:1920:flags=lanczos,fps=30,setsar=1,format=rgba[base];\
color=c=white:s=1080x1920:r=30:d=$D,format=rgba,colorchannelmixer=aa=0.6,fade=t=in:st=$START:d=0.9:alpha=1[veil];\
[base][veil]overlay=shortest=1[b2];\
[1:v]setpts=PTS-STARTPTS+$START/TB[ov];\
[b2][ov]overlay=eof_action=pass,format=yuv420p[v];\
[0:a]aresample=48000,acompressor=threshold=-24dB:ratio=3:attack=5:release=250:makeup=4dB,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]" \
  -map "[v]" -map "[a]" -t $D -c:v libx264 -crf 18 -preset slow -c:a aac -b:a 192k -movflags +faststart "$OUT"
  rm -rf "$TMP"; echo "$OUT ($D s, end card over the last 4 s)"; exit 0
fi
python3 "$HERE/sting.py" "$KEY" "$STING_LEN" "$TMP/sting.wav"
ffmpeg -y -loglevel error -i "$IN" -framerate 30 -i "$TMP/fr/o%04d.png" -i "$TMP/sting.wav" -filter_complex "\
[0:v]scale=1080:1920:flags=lanczos,fps=30,setsar=1,tpad=stop_mode=clone:stop_duration=$HOLD,format=rgba[base];\
color=c=white:s=1080x1920:r=30:d=$T,format=rgba,colorchannelmixer=aa=0.6,fade=t=in:st=$START:d=0.9:alpha=1[veil];\
[base][veil]overlay=shortest=1[b2];\
[1:v]setpts=PTS-STARTPTS+$START/TB[ov];\
[b2][ov]overlay=eof_action=pass,format=yuv420p[v];\
[0:a]aresample=48000,acompressor=threshold=-24dB:ratio=4:attack=5:release=200:makeup=6dB,loudnorm=I=-15:TP=-2,aresample=48000,afade=t=out:st=$(python3 -c "print(round($D-0.8,2))"):d=1.0,apad=whole_dur=$T[m];\
[2:a]aresample=48000,volume=-1dB,adelay=$(python3 -c "print(int($STING_AT*1000))")|$(python3 -c "print(int($STING_AT*1000))"),apad=whole_dur=$T[s];\
[m][s]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]" \
-map "[v]" -map "[a]" -t $T -c:v libx264 -crf 18 -preset slow -c:a aac -b:a 192k -movflags +faststart "$OUT"
rm -rf "$TMP"
echo "$OUT ($T s, key $KEY)"
