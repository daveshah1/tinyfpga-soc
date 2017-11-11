include ../include/generated/variables.mak
include $(MISOC_DIRECTORY)/software/common.mak

OBJECTS=loader.o

all: loader.bin

%.bin: %.elf
	$(OBJCOPY) -O binary $< $@
	chmod -x $@
	$(PYTHON) -m misoc.tools.mkmscimg $@

loader.elf: $(LOADER_DIRECTORY)/linker.ld $(OBJECTS)

%.elf:
	$(LD) $(LDFLAGS) -T $< -N -o $@ $(OBJECTS)
	chmod -x $@

%.o: $(LOADER_DIRECTORY)/%.S
	$(assemble)

clean:
	$(RM) $(OBJECTS) loader.elf loader.bin .*~ *~

.PHONY: all clean
