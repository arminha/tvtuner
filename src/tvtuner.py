__author__ = 'armin.aha@gmail.com'
__date__ = '$Mar 15, 2010 8:45:58 PM$'

import pylirc
import yaml

import time
import os
import multiprocessing
import logging

import ivtv_tuner
from osd import Osd

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
    process = multiprocessing.Process(
        target=spawn_daemon,
        args=(path_to_executable, args))
    process.start()
    process.join()


def show_tv():
    spawn('/usr/bin/vlc',
        ['vlc',
         '--quiet',
         '--video-filter=deinterlace',
         '--deinterlace-mode=blend',
         'pvr:///dev/video1'])

def handle_code(tuner, osd, code, status):
    logging.debug("Command: %s, Repeat: %d", code["config"], code["repeat"])
    config = code["config"]
    osd_count = 0
    if config.isdigit():
        if status is None:
            channel = int(config)
            osd.show('%d-' % channel)
            osd_count = 5
            return (channel, osd_count)
        else:
            channel = status * 10 + int(config)
            osd_count = set_channel(tuner, osd, channel)
    elif config == "ChanUp":
        channel = tuner.next_channel()
        osd.show(str(channel + 1))
        osd_count = 4
    elif config == "ChanDown":
        channel = tuner.prev_channel()
        osd.show(str(channel + 1))
        osd_count = 4
    elif config == "show-tv":
        show_tv()
    elif config == "enter" and not status is None:
        channel = status
        osd_count = set_channel(tuner, osd, channel)
    return (None, osd_count)

def set_channel(tuner, osd, channel):
    tuner.set_channel(channel-1)
    osd.show(str(channel))
    return 4

def lirc_remote(tuner, osd):
    blocking = False

    status = None
    osd_count = 0

    if(pylirc.init("tvtuner", "~/.lircrc", blocking)):
        code = {"config" : ""}
        count = 0
        # TODO remove 'quit'
        while(code["config"] != "quit"):
            # Delay...
            time.sleep(0.5)
            if status:
                count += 1
            else:
                count = 0
            if count > 4:
                osd_count = set_channel(tuner, osd, status)
                status = None
                count = 0

            if osd_count > 0:
                osd_count -= 1
                if osd_count == 0:
                    osd.hide()

            # Read next code
            codes = pylirc.nextcode(1)

            # Loop as long as there are more on the queue
            # (dont want to wait a second if the user pressed many buttons...)
            while(codes):
                # Print all the configs...
                for (code) in codes:
                    (status, osd_count) = handle_code(tuner, osd, code, status)

                # Read next code?
                codes = pylirc.nextcode(1)

        # Clean up lirc
        pylirc.exit()

def run():
    config_file = os.path.expanduser('~/.tvtuner/config.yaml')
    stream = open(config_file)
    config_data = yaml.load(stream)
    stream.close()

    device = config_data['device']
    device_short = device[-1:]
    stations = config_data['stations']

    tuner = ivtv_tuner.Tuner(device, device_short)
    tuner.init_stations(stations)
    osd = Osd()
    try:
        lirc_remote(tuner, osd)
    except KeyboardInterrupt:
        osd.hide()
        del osd
        pylirc.exit()
        logging.debug('Exiting..')
