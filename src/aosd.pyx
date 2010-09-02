
cdef extern from "aosd.h":
    ctypedef int Bool

    struct c_Aosd "Aosd":
        pass

    struct AosdMouseEvent:
        # relative coordinates
        int x
        int y
        # global coordinates
        int x_root
        int y_root
        int send_event

        # button being pressed
        unsigned int button
        unsigned long time

    # relative coordinates for positioning
    ctypedef enum c_AosdCoordinate "AosdCoordinate":
        c_COORDINATE_MINIMUM "COORDINATE_MINIMUM",
        c_COORDINATE_CENTER "COORDINATE_CENTER",
        c_COORDINATE_MAXIMUM "COORDINATE_MAXIMUM"

    ctypedef enum c_AosdTransparency "AosdTransparency":
        c_TRANSPARENCY_NONE "TRANSPARENCY_NONE",
        c_TRANSPARENCY_FAKE "TRANSPARENCY_FAKE",
        c_TRANSPARENCY_COMPOSITE "TRANSPARENCY_COMPOSITE"

    # object (de)allocators
    c_Aosd* aosd_new()
    void aosd_destroy(c_Aosd* aosd)

    # object inspectors
    #void aosd_get_name(c_Aosd* aosd, XClassHint* result)
    void aosd_get_names(c_Aosd* aosd, char** res_name, char** res_class)
    c_AosdTransparency aosd_get_transparency(c_Aosd* aosd)
    void aosd_get_geometry(c_Aosd* aosd, int* x, int* y, int* width, int* height)
    void aosd_get_screen_size(c_Aosd* aosd, int* width, int* height)
    Bool aosd_get_is_shown(c_Aosd* aosd)

    # object configurators
    #void aosd_set_name(c_Aosd* aosd, XClassHint* name)
    void aosd_set_names(c_Aosd* aosd, char* res_name, char* res_class)
    void aosd_set_transparency(c_Aosd* aosd, c_AosdTransparency mode)
    void aosd_set_geometry(c_Aosd* aosd, int x, int y, int width, int height)
    void aosd_set_position(c_Aosd* aosd, unsigned pos, int width, int height)
    void aosd_set_position_offset(c_Aosd* aosd, int x_offset, int y_offset)
    void aosd_set_position_with_offset(c_Aosd* aosd,
        c_AosdCoordinate abscissa, c_AosdCoordinate ordinate, int width, int height,
        int x_offset, int y_offset)
    #void aosd_set_renderer(c_Aosd* aosd, AosdRenderer renderer, void* user_data)
    #void aosd_set_mouse_event_cb(c_Aosd* aosd, AosdMouseEventCb cb, void* user_data)
    void aosd_set_hide_upon_mouse_event(c_Aosd* aosd, Bool enable)

COORDINATE_MINIMUM = c_COORDINATE_MINIMUM
COORDINATE_CENTER = c_COORDINATE_CENTER
COORDINATE_MAXIMUM = c_COORDINATE_MAXIMUM

TRANSPARENCY_NONE = c_TRANSPARENCY_NONE
TRANSPARENCY_FAKE = c_TRANSPARENCY_FAKE
TRANSPARENCY_COMPOSITE = c_TRANSPARENCY_COMPOSITE

cdef class Aosd:
    cdef c_Aosd * _aosd

    def __cinit__(self):
        self._aosd = aosd_new()

    def __dealloc__(self):
        aosd_destroy(self._aosd)

    def set_transparency(self, int mode):
        aosd_set_transparency(self._aosd, <c_AosdTransparency>mode)

