# coding=utf8

__author__ = 'armin.aha@gmail.com'
__date__  = '$Sep 1, 2010 7:47:20 PM$'

import aosd

class Osd(object):
    """
    Wrapper for aosd

    >>>osd = Osd()
    >>>osd.show_for(u'안녕 world', 1000)
    >>>for i in range(3):
    >>>    osd.show_for(str(i+1), 1000)
    >>>osd.hide()
    """
    def __init__(self):
        self._aosd = None
        self._x_offset = 0
        self._y_offset = 0
        self._position = 0

    def show(self, text):
        if not self._aosd:
            self._setup()
        self._set_text(text)
        self._aosd.show()
        self._aosd.loop_once()

    def show_for(self, text, milliseconds):
        if not self._aosd:
            self._setup()
        self._set_text(text)
        self._aosd.show()
        self._aosd.loop_for(milliseconds)

    def hide(self):
        if not self._aosd:
            self._setup()
        self._aosd.hide()
        self._aosd.loop_once()

    def _set_text(self, text):
        self._aosd.set_text(text)
        (width, height) = self._aosd.get_text_size()
        self._aosd.set_position(self._position, width, height)
        self._aosd.set_position_offset(self._x_offset, self._y_offset)
        self._aosd.render()

    def _setup(self):
        self._aosd = aosd.AosdText()
        self._aosd.set_transparency(aosd.TRANSPARENCY_COMPOSITE)

        self._aosd.geom_x_offset = 20
        self._aosd.geom_y_offset = 10

        self._aosd.back_color = 'blue'
        self._aosd.back_opacity = 200

        self._aosd.shadow_color = 'black'
        self._aosd.shadow_opacity = 127
        self._aosd.shadow_x_offset = 2
        self._aosd.shadow_y_offset = 2

        self._aosd.fore_color = 'white'
        self._aosd.fore_opacity = 255

        self._aosd.set_font('Droid Sans Mono 72')

        self._position = 2
        self._x_offset = -30
        self._y_offset = 30
