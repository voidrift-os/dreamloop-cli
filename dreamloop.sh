#!/bin/bash

# Dreamloop CLI: Build video from images and voice
mkdir -p video/outputs

for i in {1..5}
do
  echo "Processing scene$i..."
  ffmpeg -y -loop 1 -i images/scene$i.png -i voice/scene$i.mp3 -shortest -vf "scale=720:1280" video/scene$i.mp4
done

# Generate filelist
echo -n > video/filelist.txt
for i in {1..5}
do
  echo "file 'scene$i.mp4'" >> video/filelist.txt
done

# Combine all into final video
ffmpeg -f concat -safe 0 -i video/filelist.txt -c copy video/final_dreamloop_short.mp4
echo "✅ Final video saved as video/final_dreamloop_short.mp4"
