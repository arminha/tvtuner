
cdef extern from "aosd.h":
    struct c_Aosd "Aosd":
        pass

    c_Aosd* c_aosd_new "aosd_new"()

    void c_aosd_destroy "aosd_destroy" (c_Aosd* aosd)

cdef class Aosd:
    cdef c_Aosd * _aosd

    def __cinit__(self):
        self._aosd = c_aosd_new()

    def __dealloc__(self):
        c_aosd_destroy(self._aosd)

