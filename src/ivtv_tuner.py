__author__="armin.aha@gmail.com"
__date__ ="$Mar 15, 2010 8:54:12 PM$"

import re
import subprocess

import logging

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
        raise subprocess.CalledProcessError(retcode, cmd, output=output)
    return output

class Tuner(object):
    """
    Documentation
    """
    def __init__(self, device):
        object.__init__(self)
        self.__channels = []
        self.__current_channel = 0
        self.__device = device

    def channels(self):
        for (name, _) in self.__channels:
            yield name

    def current_channel(self):
        return self.__current_channel

    def set_channel(self, channel):
        (_,frequency) = self.__channels[channel]
        command = ['ivtv-tune', '-d', self.__device, '-f', frequency.__str__()]
        output = check_output(
            command,
            stderr=subprocess.STDOUT)
        logging.debug('call "%s", output = "%s"' % (' '.join(command), output))
        self.__current_channel = channel

    def next_channel(self):
        channel = self.__current_channel + 1
        if channel == len(self.__channels):
            channel = 0
        self.set_channel(channel)

    def prev_channel(self):
        channel = self.__current_channel - 1
        if channel == -1:
            channel = len(self.__channels) - 1
        self.set_channel(channel)

    def init_channels(self, filename):
        f = open(filename)
        self.__channels = []
        line = f.readline()
        while line:
            m = re.search('\{([^\}]*)\} ([0-9.]*) 0', line)
            if m:
                self.__channels.append((m.group(1), float(m.group(2))))
            line = f.readline()
        if self.__channels:
            self.set_channel(0)
