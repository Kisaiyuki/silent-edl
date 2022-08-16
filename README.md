# silent-edl
Silent-EDL A program for making an edit decision list from the non-silent parts of a video
Copyright 2022 Kisai

This tool is for quickly editing down video using "delete gaps" in 
Davinci Resolve Studio with no creative thought to it. It is not 
meant to be the entire process.

The following program was written by Kisai for use by Vtuber's

Permission to use this program is subject to the following rules:
1. Videos must be free and public to watch (eg Youtube, bilibili, niconico douga, tiktok)
2. No support or warranty will be provided
3. No bug reports or patches will be accepted

It is expressly forbidden to make private and/or unlisted youtube,
twitch, patreon, onlyfans or other subscriber-only content using 
this tool. Feel free to make commercial content as long as it's 
free to watch.
 
I made this program to save several vtuber's official editor's 
time who have the original recording. It will not save you very much
time if your streamer doesn't separate their audio and you rely on a 
noise threshold from an already published stream.

if you need FFMPEG for Windows: 
  https://www.gyan.dev/ffmpeg/builds/
if you need python for Windows: 
  https://www.python.org/downloads/release/python-3713/
It may work with later versions of ffmpeg or python, but the developer
has only used Python 3.7 and bleeding-edge builds of ffmpeg 5.x

You can save yourself a headache and use the windows build under releases
if you do not know how to use or install python

The EDL's generated have only been tested in Davinci Resolve Studio 18
Davinci Resolve is also available for free
https://www.blackmagicdesign.com/products/davinciresolve

EDL's should also work in Final Cut and Adobe Premiere

Tunables in silent-edl.ini:
```
[main]
; audio track starting from 0 to use. You probably want to use your 
; microphone track.
audiotrack = 0 
; padding on both sides of the detected audio in ms, if it's less 
; it sounds unnatural, likewise, you may want 3 seconds (3000) if you
; you are captioning the audio
padding = 100
; Keep the temporary file, eg you're going to run this multiple times
; defaults to false
keeptemp = True
; noise threshold for detection, if you didn't separate your audio, 
; set above your background noise/music. If you did separate your
; audio, then -60 dB should be okay.
noisethreshold = -60.0

[work]
; frame rate of last demux, written so that saving the temporary file
; can be reused
framerate = 60.0 
```
