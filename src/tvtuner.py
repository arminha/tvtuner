__author__ = 'armin.aha@gmail.com'
__date__ = '$Mar 15, 2010 8:45:58 PM$'

import pylirc
import yaml

import time
import os
import multiprocessing
import logging
import subprocess

from ivtv_tuner import Tuner, scan_for_devices
from osd import Osd

def spawn_daemon(path_to_executable, args):
    """
    Spawn a completely detached subprocess (i.e., a daemon).
    """
    # fork the first time (to make a non-session-leader child process)
    try:
        pid = os.fork()
    except OSError, ex:
        raise RuntimeError("1st fork failed: %s [%d]" % (ex.strerror, ex.errno))
    if pid != 0:
        # parent (calling) process is all done
        return

    # detach from controlling terminal (to make child a session-leader)
    os.setsid()
    try:
        pid = os.fork()
    except OSError, ex:
        raise RuntimeError("2nd fork failed: %s [%d]" % (ex.strerror, ex.errno))
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
    except:
        # oops, we're cut off from the world, let's just give up
        os._exit(255)

def spawn(path_to_executable, args):
    """
    Spawn executable as a completely detached subprocess (i.e., a daemon).
    """
    process = multiprocessing.Process(
        target=spawn_daemon,
        args=(path_to_executable, args))
    process.start()
    process.join()

def is_running(process_name):
    with os.popen("ps x") as lines:
        for line in lines:
            fields = line.split()
            process = fields[4]
            if process_name == process:
                return True
        return False

def shutdown():
    """
    Close the Gnome session and shutdown the computer using dbus.
    Obviously only works when Gnome is running.
    Was only tested on Gnome 2.30 on Ubuntu 10.4.

    > dbus-send --print-reply --dest=org.gnome.SessionManager
      /org/gnome/SessionManager org.gnome.SessionManager.RequestShutdown
    """
    logging.info('shutdown computer')
    subprocess.check_call(
        ['dbus-send',
         '--print-reply',
         '--dest=org.gnome.SessionManager',
         '/org/gnome/SessionManager',
         'org.gnome.SessionManager.RequestShutdown'])
    exit(0)

_OSD_SECONDS = 2
_SINGLE_DIGIT_SECONDS = 2

class Remote(object):
    def __init__(self, config_data):
        device = config_data['device']
        stations = config_data['stations']
        devices = []
        if device.lower() == 'auto':
            devices = scan_for_devices()
        else:
            devices = [device]

        self._devices = devices
        self._device = devices[0]
        self._tuners = []
        for dev in self._devices:
            tuner = Tuner(dev)
            tuner.init_stations(stations)
            self._tuners.append(tuner)
        self._tuner = self._tuners[0]
        self._osd = Osd()
        self._sleep_time = 0.2
        self._osd_time = None
        self._first_digit = None
        self._show_digit_time = 0
        self._show_shutdown_message = False

    def show_tv(self):
        """
        Start vlc to show tv.
        """
        spawn('/usr/bin/vlc',
            ['vlc',
            '--quiet',
            '--video-filter=deinterlace',
            '--deinterlace-mode=blend',
            'pvr://%s' % self._device])

    def set_channel(self, channel):
        """
        Set channel.
        """
        self._tuner.set_channel(channel-1)
        self.show_osd(str(channel))
        self._first_digit = None

    def show_osd(self, message):
        """
        Show osd message for _OSD_SECONDS seconds.
        """
        self._osd.show(message)
        self._osd_time = _OSD_SECONDS

    def toggle_audio_mode(self):
        """
        Toggle between the available audio modes of the current channel.
        """
        mode = self._tuner.get_audio_mode()
        modes = self._tuner.get_available_audio_modes()
        index = 0
        try:
            index = modes.index(mode) + 1
        except ValueError:
            pass
        new_mode = modes[index % len(modes)]
        self._tuner.set_audio_mode(new_mode)
        self.show_osd(new_mode)

    def switch_device(self):
        ind = (self._devices.index(self._device) + 1) % len(self._devices)
        self._device = self._devices[ind]
        self._tuner = self._tuners[ind]

    def handle_code(self, code):
        """
        Handle the lirc commands.
        """
        logging.debug("Command: %s, Repeat: %d", code["config"], code["repeat"])
        config = code["config"]
        if config.isdigit():
            digit = int(config)
            if self._first_digit is None:
                self.show_osd('%d-' % digit)
                self._first_digit = digit
                self._show_digit_time = _SINGLE_DIGIT_SECONDS
            else:
                channel = self._first_digit * 10 + digit
                self.set_channel(channel)
        elif config == "ChanUp":
            channel = self._tuner.next_channel()
            self.show_osd(str(channel + 1))
        elif config == "ChanDown":
            channel = self._tuner.prev_channel()
            self.show_osd(str(channel + 1))
        elif config == "ShowTv":
            self.show_tv()
        elif config == "Enter" and not self._first_digit is None:
            self.set_channel(self._first_digit)
        elif config == "ToggleAudio":
            self.toggle_audio_mode()
        if config == 'Shutdown' and not is_running('vlc'):
            if self._show_shutdown_message:
                shutdown()
            else:
                self.show_osd('Shutdown?')
                self._show_shutdown_message = True
        else:
            self._show_shutdown_message = False
        if config == "SwitchDevice":
            self.switch_device()

    def _lirc_main_loop(self):
        """
        Pylirc main loop.
        """
        code = {"config" : ""}
        while True:
            # Delay...
            time.sleep(self._sleep_time)

            # reduce osd time
            if self._osd_time and self._osd_time > 0:
                self._osd_time -= self._sleep_time

            # set channel if one digit is set
            if self._first_digit:
                self._show_digit_time -= self._sleep_time
                if self._show_digit_time <= 0:
                    self.set_channel(self._first_digit)

            # hide osd message
            if self._osd_time and self._osd_time <= 0:
                self._osd.hide()
                self._osd_time = None

            # Read next code
            codes = pylirc.nextcode(1)

            # Loop as long as there are more on the queue
            # (dont want to wait a second if the user pressed many buttons...)
            while codes:
                for code in codes:
                    self.handle_code(code)

                # Read next code?
                codes = pylirc.nextcode(1)

    def start_main_loop(self):
        """
        Read lirc config file and start main pylirc main loop.
        """
        if pylirc.init("tvtuner", "~/.lircrc", False):
            try:
                self._lirc_main_loop()
            except KeyboardInterrupt:
                self._osd.hide()
                pylirc.exit()
        del self._osd
        logging.debug('Exiting..')

def run():
    config_file = os.path.expanduser('~/.tvtuner/config.yaml')
    stream = open(config_file)
    config_data = yaml.load(stream)
    stream.close()

    # initialize logging
    if config_data.has_key('logfile'):
        logging.basicConfig(
            filename=config_data['logfile'],
            level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.DEBUG)

    try:
        remote = Remote(config_data)
        remote.start_main_loop()
    except:
        logging.exception("Unexpected Error:")
