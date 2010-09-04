PYHOME = /usr
PYINCLUDE = \
	-I$(PYHOME)/include/python2.6
AOSDINCLUDE = \
    -I/usr/include/libaosd
AOSDLIBS = \
    -laosd -laosd-text
PANGOCAIRO_CFLAGS = `pkg-config --cflags --libs pangocairo`

%.c:	%.pyx
	pyrexc $<

%.o:	%.c
	gcc -c -fPIC $(PYINCLUDE) $(AOSDINCLUDE) $(PANGOCAIRO_CFLAGS) $<

%.so:	%.o
	gcc -shared $< -lm $(AOSDLIBS) -o $@

all:	aosd.so

clean:
	@echo Cleaning Demos
	@rm -f *.c *.o *.so *~ core core.*

