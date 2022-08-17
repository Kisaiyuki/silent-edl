#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Video Silence to Edit Decision List (For video editors)
# Copyright 2022 Kisai.

# The following program was written by Kisai for use by Vtuber's
#
# Permission to use this program is subject to the following rules:
# 1. Videos must be free and public to watch (eg Youtube, bilibili, 
#    niconico douga, tiktok)
# 2. No support or warranty will be provided
# 3. No bug reports or patches will be accepted
#
# Use of this software is entirely at your own risk. It is built with 
# python and libraries that are free to use on the internet. If you want to
# change, optimize or refactor the functionality please fork this project 
# instead without removing the above rules. I am not interested in 
# expanding or refactoring this. It was written in one day, to accomplish 
# exactly one thing that is otherwise time consuming.

# Use of this software to create private, members-only, or paywalled 
# content is prohibited. Please use common sense, and recognize that if you
# are asking people to pay for the content you should be paying for the 
# tools and assets used to make it. 
#
# The author of this software, has developed this program to reduce the 
# workflow of live stream to VOD Archive, News and Clipping/shorts by 
# creating an edit decision list in a CMX3600-like EDL file.
#
# This tool is for quickly editing down video using "delete gaps" in 
# Davinci Resolve Studio with no creative thought to it. It is not 
# meant to be the entire process.
#
# Hence, if you are editing free-to-watch video, then the subsequent
# video must be free-to-watch as well.
#
# It is expressly forbidden to make private and/or unlisted youtube,
# twitch, patreon, onlyfans or other subscriber-only content using 
# this tool. Feel free to make commercial content as long as it's 
# free to watch.
# 
# I made this program to save several vtuber's official editor's 
# time who have the original recording. It will not save you very much
# time if your streamer doesn't separate their audio and you rely on a 
# noise threshold from an already published stream.
#
# if you need FFMPEG for Windows: 
#  https://www.gyan.dev/ffmpeg/builds/
# if you need python for Windows: 
#  https://www.python.org/downloads/release/python-3713/
# It may work with later versions of ffmpeg or python, but the developer
# has only used Python 3.7 and bleeding-edge builds of ffmpeg 5.x
#
# The EDL's generated have only been tested in Davinci Resolve Studio 18
# Davinci Resolve is also available for free
# https://www.blackmagicdesign.com/products/davinciresolve
#
# EDL's should also work in Final Cut and Adobe Premiere

# Tunables in silent-edl.ini:
# [main]
# ; audio track starting from 0 to use. You probably want to use your 
# ; microphone track.
# audiotrack = 0 
# ; padding on both sides of the detected audio in ms, if it's less 
# ; it sounds unnatural, likewise, you may want 3 seconds (3000) if you
# ; you are captioning the audio
# padding = 100
# ; Keep the temporary file, eg you're going to run this multiple times
# ; defaults to false
# keeptemp = True
# ; noise threshold for detection, if you didn't separate your audio, 
# ; set above your background noise/music. If you did separate your
# ; audio, then -60 dB should be okay.
# noisethreshold = -60.0

# [work]
# ; frame rate of last demux, written so that saving the temporary file
# ; can be reused
# framerate = 60.0 




import sys
import os
import re
import subprocess
import configparser



filepath=""
inputfile=""
track=0

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  


config = ConfigParser()
config['main']={'audiotrack':0, 'padding':100,'keeptemp':False,'noisethreshold':-60.0}
config['work']={'framerate':60.0,}

config.read('silent-edl.ini')
track = config.getint('main', 'audiotrack')
keeptemp = config.getboolean('main', 'keeptemp')
padding = config.getint('main', 'padding')
noisethreshold=config.getfloat('main', 'noisethreshold')

framerate = config.getfloat('work', 'framerate')


def convert_from_ms( milliseconds ): 
	seconds, milliseconds = divmod(milliseconds,1000) 
	minutes, seconds = divmod(seconds, 60) 
	hours, minutes = divmod(minutes, 60) 
	days, hours = divmod(hours, 24) 
	frames=(milliseconds/(1/framerate * 1000))
	return days, hours, minutes, seconds, frames

def write_edl(xcue,in_ms,out_ms):
    global EDLoutput
    (indays,inhours,inminutes,inseconds,inframes) = convert_from_ms(in_ms)
    (outdays,outhours,outminutes,outseconds,outframes) = convert_from_ms(out_ms)            
    intime='%02u:%02u:%02u:%02u' % (inhours, inminutes, inseconds,inframes)
    outtime='%02u:%02u:%02u:%02u' % (outhours, outminutes, outseconds,outframes)
    
    EDLoutput=EDLoutput+'{0:04}  {1:03}      V      C        {2:s} {3:s} {4:s} {5:s}\n\n'.format(int(xcue),int(1),str(intime),str(outtime),str(intime),str(outtime))

    

#For best results, put your voice-alone on track , and keep it on the same channel (eg 4) on all scenes in OBS, ffmpeg starts from 0, not 1
# Kisai's OBS setup is:
# 0 Track 1 Stream mix
# 1 Track 2 VOD mix (same as stream minus audio in media share)
# 2 Track 3 Game audio
# 3 Track 4 My Voice
# 4 Track 5 BGM or Discord audio during collabs
# 5 Track 6 Twitch Alerts/streamelements (so they can be removed from edited video)


if len(sys.argv) == 1:
    print("silent-edl 1.0 written by Kisai \n")
    print("USAGE: \n")
    print("silent-edl INPUT.MP4")
#    print("or, specify the audio track, use ffmpeg or ffprobe, or just open the video and check")
#    print("default will be the first track")
 #   print("silent-edl INPUT.MP4 --track 3")

for inputfile in sys.argv[1:]:
    mastertimestamp=0
    intimestamp=0
    outtimestamp=0
    lasttimestamp=0

    cue=0

    EDLoutput=""
    EDLfilename=""

    file_path=inputfile

#Step 1, use FFMPEG to pull the audio out

    work_file=f"{file_path}.wav"

    #this could also be done as one step, but appears to run 10x slower.
    if os.path.exists(work_file) is False:
        command = f'ffmpeg -i "{file_path}" -map 0:a:{track} -ac 1 -acodec pcm_s16le -y -ar 48000 -hide_banner "{work_file}"'
        u = subprocess.Popen(command,stderr=subprocess.PIPE)
        utext=u.stderr.read()
        retcode = u.wait()
        utext = utext.decode('utf-8')
        mfps = re.compile("\s[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+) fps")
        for (datafps) in re.findall(mfps,utext):
            
            if float(datafps[0]) >0.0:
                framerate=float(datafps[0])
            print(f"FPS: {framerate}")
            config.set('work','framerate',str(framerate))
#Step 2

    command = f'ffmpeg -i "{work_file}" -af silencedetect=noise={noisethreshold}dB:d=1 -nostats -hide_banner -f null -'
    p = subprocess.Popen(command,stderr=subprocess.PIPE)
    text=p.stderr.read()
    retcode = p.wait()
    text = text.decode('utf-8')
    mpatstart = re.compile("silence_(start|end):\s[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)",re.MULTILINE|re.DOTALL)
    cue=0
    
    for (data) in re.findall(mpatstart,text):
        if data[0] == "end":
            cue=cue+1
  
            intimestamp=float(data[1])*1000
            #default creates EDL "too perfect", this + or -'s 100ms
            intimestamp=intimestamp-padding

        if data[0] == "start":

           outtimestamp=float(data[1])*1000
           outtimestamp=outtimestamp+padding

        
        #this is so cheap it's stupid
        if(intimestamp<outtimestamp):
            write_edl(cue,intimestamp,outtimestamp)
 
    EDLfilename=f"{file_path}.edl"
    
    text_file = open(EDLfilename, "w")
    if(framerate.is_integer()):
        EDLheader=f"TITLE:  {file_path}\nFCM: NON - DROP FRAME\n\n"
    else:    
        EDLheader=f"TITLE:  {file_path}\nFCM: DROP FRAME\n\n"
        
    writtenbytes=text_file.write(EDLheader+EDLoutput)
    text_file.close()
    
    if writtenbytes >0:
     print(f"written to {EDLfilename}\n")    
    else:
     print(f"failed to write to {EDLfilename}\n")    
    
    if keeptemp is False:
        os.remove(f"{work_file}")
    
    with open('silent-edl.ini', 'w') as configfile:
         config.write(configfile)
