
#########################################
# Extern C definitions
#########################################

cdef extern from "aosd.h":
    ctypedef int Bool

    struct cairo_t:
        pass

    struct XClassHint:
        pass

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

    # various callbacks
    ctypedef void (*AosdRenderer)(cairo_t* cr, void* user_data)
    ctypedef void (*AosdMouseEventCb)(AosdMouseEvent* event, void* user_data)

    # object (de)allocators
    c_Aosd* aosd_new()
    void aosd_destroy(c_Aosd* aosd)

    # object inspectors
    void aosd_get_name(c_Aosd* aosd, XClassHint* result)
    void aosd_get_names(c_Aosd* aosd, char** res_name, char** res_class)
    c_AosdTransparency aosd_get_transparency(c_Aosd* aosd)
    void aosd_get_geometry(c_Aosd* aosd, int* x, int* y, int* width, int* height)
    void aosd_get_screen_size(c_Aosd* aosd, int* width, int* height)
    Bool aosd_get_is_shown(c_Aosd* aosd)

    # object configurators
    void aosd_set_name(c_Aosd* aosd, XClassHint* name)
    void aosd_set_names(c_Aosd* aosd, char* res_name, char* res_class)
    void aosd_set_transparency(c_Aosd* aosd, c_AosdTransparency mode)
    void aosd_set_geometry(c_Aosd* aosd, int x, int y, int width, int height)
    void aosd_set_position(c_Aosd* aosd, unsigned pos, int width, int height)
    void aosd_set_position_offset(c_Aosd* aosd, int x_offset, int y_offset)
    void aosd_set_position_with_offset(c_Aosd* aosd,
        c_AosdCoordinate abscissa, c_AosdCoordinate ordinate, int width, int height,
        int x_offset, int y_offset)
    void aosd_set_renderer(c_Aosd* aosd, AosdRenderer renderer, void* user_data)
    void aosd_set_mouse_event_cb(c_Aosd* aosd, AosdMouseEventCb cb, void* user_data)
    void aosd_set_hide_upon_mouse_event(c_Aosd* aosd, Bool enable)

    # object manipulators
    void aosd_render(c_Aosd* aosd)
    void aosd_show(c_Aosd* aosd)
    void aosd_hide(c_Aosd* aosd)

    # X main loop processing
    void aosd_loop_once(c_Aosd* aosd)
    void aosd_loop_for(c_Aosd* aosd, unsigned loop_ms)

    # automatic object manipulator
    void aosd_flash(c_Aosd* aosd, unsigned fade_in_ms,
        unsigned full_ms, unsigned fade_out_ms)


cdef extern from "aosd-text.h":
    struct PangoLayout:
        pass

    struct PangoAttribute:
        pass

    PangoLayout* pango_layout_new_aosd()
    void pango_layout_unref_aosd(PangoLayout* lay)

    void pango_layout_get_size_aosd(PangoLayout* lay,
        unsigned* width, unsigned* height, int* lbearing)

    # Converts all \n occurrences into U+2028 symbol
    void pango_layout_set_text_aosd(PangoLayout* lay, char* text)
    void pango_layout_set_attr_aosd(PangoLayout* lay, PangoAttribute* attr)
    void pango_layout_set_font_aosd(PangoLayout* lay, char* font_desc)

    struct TextRenderData:
        pass

    void aosd_text_renderer(cairo_t* cr, void* TextRenderData_ptr)
    void aosd_text_get_size(TextRenderData* trd, unsigned* width, unsigned* height)
    int aosd_text_get_screen_wrap_width(c_Aosd* aosd, TextRenderData* trd)


#########################################
# Python definitions
#########################################

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

    def get_transparency(self):
        return aosd_get_transparency(self._aosd)

    def get_screen_size(self):
        cdef int width
        cdef int height
        aosd_get_screen_size(self._aosd, &width, &height)
        return (width, height)

    def is_shown(self):
        return aosd_get_is_shown(self._aosd)

    def show(self):
        aosd_show(self._aosd)

    def hide(self):
        aosd_hide(self._aosd)

    def render(self):
        aosd_render(self._aosd)

