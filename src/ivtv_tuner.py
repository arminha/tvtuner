__author__ = 'armin.aha@gmail.com'
__date__  = '$Mar 15, 2010 8:54:12 PM$'

import subprocess
import logging
import re

# TODO audio mode
# get audio mode: v4l2-ctl -d 1 -T
# set audio mode: v4l2-ctl -d 1 -t lang1 ...

# reimplement subprocess.check_output from python 2.7
def check_output(*popenargs, **kwargs):
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd)
    return output

_AUDIO_LANG1 = 'lang1'
_AUDIO_LANG2 = 'lang2'
_AUDIO_MONO = 'mono'
_AUDIO_STEREO = 'stereo'

class Tuner(object):
    """
    Tuner supporting ivtv-based tv tuner devices
    """
    def __init__(self, device, device_short):
        """
        Initialize Tuner.

        :param device: The name of the tuner device (usually something like '/dev/video0')
        :type device: string
        :param device_short: The short name of the device (usually a number like '0')
        :type device_short: string
        """
        object.__init__(self)
        self.__channels = []
        self.__current_channel = 0
        self.__device = device
        self.__device_short = device_short

    def channels(self):
        for (name, _) in self.__channels:
            yield name

    def current_channel(self):
        return self.__current_channel

    def set_channel(self, channel):
        """
        Set channel to the given channel.

        :param channel: The channel to set
        :type channel: int
        """
        (_, frequency) = self.__channels[channel]
        command = ['ivtv-tune', '-d', self.__device, '-f', frequency.__str__()]
        output = check_output(
            command,
            stderr=subprocess.STDOUT)
        logging.debug('call "%s", output = "%s"', ' '.join(command), output)
        self.__current_channel = channel

    def next_channel(self):
        """
        Set channel to the next channel.

        :return: The current channel
        :rtype: int
        """
        channel = self.__current_channel + 1
        if channel == len(self.__channels):
            channel = 0
        self.set_channel(channel)
        return channel

    def prev_channel(self):
        """
        Set channel to the previous channel.

        :return: The current channel
        :rtype: int
        """
        channel = self.__current_channel - 1
        if channel == -1:
            channel = len(self.__channels) - 1
        self.set_channel(channel)
        return channel

    def init_stations(self, stations):
        self.__channels = []
        for station in stations:
            self.__channels.append((station['name'], station['channel']))
        if self.__channels:
            self.set_channel(0)

    def get_audio_mode(self):
        command = ['v4l2-ctl', '-d', self.__device_short, '-T']
        output = check_output(
            command,
            stderr=subprocess.STDOUT)
        logging.debug('call "%s", output = "%s"', ' '.join(command), output)
        match = re.search('Current audio mode\s*:\s*(?P<mode>.*)', output)
        mode = match.group('mode')
        return mode

    def get_available_audio_modes(self):
        command = ['v4l2-ctl', '-d', self.__device_short, '-T']
        output = check_output(
            command,
            stderr=subprocess.STDOUT)
        logging.debug('call "%s", output = "%s"', ' '.join(command), output)
        match = re.search('Available subchannels\s*:\s*(?P<modes>.*)', output)
        modes = match.group('modes')
        return modes.split()

    def set_audio_mode(self, mode):
        command = ['v4l2-ctl', '-d', self.__device_short, '-t', mode]
        output = check_output(
            command,
            stderr=subprocess.STDOUT)
        logging.debug('call "%s", output = "%s"', ' '.join(command), output)
