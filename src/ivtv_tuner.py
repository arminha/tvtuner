__author__ = 'armin.aha@gmail.com'
__date__  = '$Mar 15, 2010 8:54:12 PM$'

import subprocess
import logging
import re

def check_output(*popenargs, **kwargs):
    """
    Reimplement subprocess.check_output from python 2.7
    """
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, _ = process.communicate()
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
    def __init__(self, device):
        """
        Initialize Tuner.

        :param device: The name of the tuner device (usually something like '/dev/video0')
        :type device: string
        :param device_short: The short name of the device (usually a number like '0')
        :type device_short: string
        """
        object.__init__(self)
        self._channels = []
        self._current_channel = 0
        self._device = device

    def channels(self):
        """
        Return the names of the available channels.

        :return: Channel list
        :rtype: [string]
        """
        for (name, _) in self._channels:
            yield name

    def current_channel(self):
        """
        Return the current channel.

        :return: The current channel
        :rtype: int
        """
        return self._current_channel

    def set_channel(self, channel):
        """
        Set channel to the given channel.

        :param channel: The channel to set
        :type channel: int
        """
        (_, frequency) = self._channels[channel % len(self._channels)]
        command = ['ivtv-tune', '-d', self._device, '-f', frequency.__str__()]
        output = check_output(
            command,
            stderr=subprocess.STDOUT)
        logging.debug('call "%s", output = "%s"', ' '.join(command), output)
        self._current_channel = channel

    def next_channel(self):
        """
        Set channel to the next channel.

        :return: The current channel
        :rtype: int
        """
        channel = self._current_channel + 1
        if channel == len(self._channels):
            channel = 0
        self.set_channel(channel)
        return channel

    def prev_channel(self):
        """
        Set channel to the previous channel.

        :return: The current channel
        :rtype: int
        """
        channel = self._current_channel - 1
        if channel == -1:
            channel = len(self._channels) - 1
        self.set_channel(channel)
        return channel

    def init_stations(self, stations):
        self._channels = []
        for station in stations:
            self._channels.append((station['name'], station['channel']))
        if self._channels:
            self.set_channel(0)

    def get_audio_mode(self):
        command = ['v4l2-ctl', '-d', self._device, '-T']
        output = check_output(
            command,
            stderr=subprocess.STDOUT)
        logging.debug('call "%s", output = "%s"', ' '.join(command), output)
        match = re.search('Current audio mode\s*:\s*(?P<mode>.*)', output)
        mode = match.group('mode')
        return mode

    def get_available_audio_modes(self):
        command = ['v4l2-ctl', '-d', self._device, '-T']
        output = check_output(
            command,
            stderr=subprocess.STDOUT)
        logging.debug('call "%s", output = "%s"', ' '.join(command), output)
        match = re.search('Available subchannels\s*:\s*(?P<modes>.*)', output)
        modes = match.group('modes')
        return modes.split()

    def set_audio_mode(self, mode):
        command = ['v4l2-ctl', '-d', self._device, '-t', mode]
        output = check_output(
            command,
            stderr=subprocess.STDOUT)
        logging.debug('call "%s", output = "%s"', ' '.join(command), output)
