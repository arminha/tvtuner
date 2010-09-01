
cdef extern from "aosd.h":
    struct c_Aosd "Aosd":
        pass

    c_Aosd* aosd_new()

    void aosd_destroy(c_Aosd* aosd)

    ctypedef enum c_AosdTransparency "AosdTransparency":
        c_TRANSPARENCY_NONE "TRANSPARENCY_NONE" = 0,
        c_TRANSPARENCY_FAKE "TRANSPARENCY_FAKE",
        c_TRANSPARENCY_COMPOSITE "TRANSPARENCY_COMPOSITE"

    void aosd_set_transparency(c_Aosd* aosd, c_AosdTransparency mode)

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

