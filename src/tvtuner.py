#!/usr/bin/python

__author__="armin.aha@gmail.com"
__date__ ="$Mar 15, 2010 8:45:58 PM$"

import pylirc
import time

import os
import multiprocessing

import logging

import ivtv_tuner

logging.basicConfig(level=logging.DEBUG)


def spawn_daemon(path_to_executable, args):
    """Spawn a completely detached subprocess (i.e., a daemon).

    E.g. for mark:
    spawnDaemon("../bin/producenotify.py", "producenotify.py", "xx")
    """
    # fork the first time (to make a non-session-leader child process)
    try:
        pid = os.fork()
    except OSError, e:
        raise RuntimeError("1st fork failed: %s [%d]" % (e.strerror, e.errno))
    if pid != 0:
        # parent (calling) process is all done
        return

    # detach from controlling terminal (to make child a session-leader)
    os.setsid()
    try:
        pid = os.fork()
    except OSError, e:
        raise RuntimeError("2nd fork failed: %s [%d]" % (e.strerror, e.errno))
        raise Exception, "%s [%d]" % (e.strerror, e.errno)
    if pid != 0:
        # child process is all done
        os._exit(0)

    # grandchild process now non-session-leader, detached from parent
    # grandchild process must now close all open files
    try:
        maxfd = os.sysconf("SC_OPEN_MAX")
    except (AttributeError, ValueError):
        maxfd = 1024

    os.closerange(0, maxfd)

    # redirect stdin, stdout and stderr to /dev/null
    os.open("/dev/null", os.O_RDONLY)    # standard input (0)
    os.open("/dev/null", os.O_RDWR)      # standard output (1)
    os.open("/dev/null", os.O_RDWR)      # standard error (2)


    # and finally let's execute the executable for the daemon!
    try:
        os.execv(path_to_executable, args)
    except Exception, e:
        # oops, we're cut off from the world, let's just give up
        os._exit(255)

def spawn(path_to_executable, args):
    p = multiprocessing.Process(target=spawn_daemon, args=(path_to_executable, args))
    p.start()
    p.join()


def show_tv():
    spawn('/usr/bin/vlc',
        ['vlc',
         '--quiet',
         '--video-filter=deinterlace',
         '--deinterlace-mode=blend',
         'pvr:///dev/video1'])

def handle_code(tuner, code, status):
    logging.debug("Command: %s, Repeat: %d" % (code["config"], code["repeat"]))
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
            time.sleep(0.5)
            if status:
                count += 1
            else:
                count = 0
            if count > 4:
                tuner.set_channel(status-1)
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
