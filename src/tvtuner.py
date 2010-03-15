#!/usr/bin/python

__author__="armin.aha@gmail.com"
__date__ ="$Mar 15, 2010 8:45:58 PM$"

import pylirc
import subprocess
import time

import ivtv_tuner

def show_tv():
    tv_process = subprocess.Popen(
        ['vlc',
         '--quiet',
         '--video-filter=deinterlace',
         '--deinterlace-mode=blend',
         'pvr:///dev/video1'])

def handle_code(tuner, code):
    print "Command: %s, Repeat: %d" % (code["config"], code["repeat"])
    config = code["config"]
    if config.isdigit():
        channel = int(config) - 1
        tuner.set_channel(channel)
    elif(config == "ChanUp"):
        tuner.next_channel()
    elif(config == "ChanDown"):
        tuner.prev_channel()
    elif(config == "show-tv"):
        show_tv()

def lirc_remote(tuner):
    pass
    blocking = True;

    if(pylirc.init("tvtuner", "~/.lircrc", blocking)):
        code = {"config" : ""}
        while(code["config"] != "quit"):
            # Very intuitive indeed
            if(not blocking):
                print "."

                # Delay...
                time.sleep(1)

            # Read next code
            s = pylirc.nextcode(1)

            # Loop as long as there are more on the queue
            # (dont want to wait a second if the user pressed many buttons...)
            while(s):

                # Print all the configs...
                for (code) in s:
                    handle_code(tuner, code)

                # Read next code?
                if(not blocking):
                    s = pylirc.nextcode(1)
                else:
                    s = []

        # Clean up lirc
        pylirc.exit()

if __name__ == "__main__":
    device = '/dev/video1'
    tuner = ivtv_tuner.Tuner(device)
    tuner.init_channels('/home/armin/.tv-viewer/config/stations_europe-west.conf')
    lirc_remote(tuner)
