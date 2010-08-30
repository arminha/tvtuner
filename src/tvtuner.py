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

def handle_code(tuner, code, status):
    print "Command: %s, Repeat: %d" % (code["config"], code["repeat"])
    config = code["config"]
    if config.isdigit():
        if status is None:
            return int(config)
        else:
            channel = status * 10 + int(config) - 1
            tuner.set_channel(channel)
    elif config == "ChanUp":
        tuner.next_channel()
    elif config == "ChanDown":
        tuner.prev_channel()
    elif config == "show-tv":
        show_tv()
    elif config == "enter" and not status is None:
        channel = status - 1
        tuner.set_channel(channel)
    return None

def lirc_remote(tuner):
    blocking = False;

    status = None

    if(pylirc.init("tvtuner", "~/.lircrc", blocking)):
        code = {"config" : ""}
        count = 0
        while(code["config"] != "quit"):
            # Delay...
            time.sleep(1)
            if status:
                count += 1
            else:
                count = 0
            if count > 3:
                tuner.set_channel(status)
                status = None
                count = 0

            # Read next code
            s = pylirc.nextcode(1)

            # Loop as long as there are more on the queue
            # (dont want to wait a second if the user pressed many buttons...)
            while(s):
                # Print all the configs...
                for (code) in s:
                    status = handle_code(tuner, code, status)

                # Read next code?
                s = pylirc.nextcode(1)

        # Clean up lirc
        pylirc.exit()

if __name__ == "__main__":
    device = '/dev/video1'
    tuner = ivtv_tuner.Tuner(device)
    tuner.init_channels('/home/armin/.tv-viewer/config/stations_europe-west.conf')
    lirc_remote(tuner)
