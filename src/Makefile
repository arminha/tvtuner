PYHOME = /usr
PYINCLUDE = \
	-I$(PYHOME)/include/python2.6
AOSDINCLUDE = \
    -I/usr/include/libaosd
AOSDLIBS = \
    -laosd

%.c:	%.pyx
	pyrexc $<

%.o:	%.c
	gcc -c -fPIC $(PYINCLUDE) $(AOSDINCLUDE) $<

%.so:	%.o
	gcc -shared $< -lm $(AOSDLIBS) -o $@

all:	aosd.so

clean:
	@echo Cleaning Demos
	@rm -f *.c *.o *.so *~ core core.*

