include ../include/generated/variables.mak
include $(SOC_DIRECTORY)/software/common.mak

OBJECTS=crt0.o main.o

all: loader.bin

%.bin: %.elf
	$(OBJCOPY) -O binary $< $@
	chmod -x $@
	$(PYTHON) -m misoc.tools.mkmscimg $@

loader.elf: $(LOADER_DIRECTORY)/linker.ld $(OBJECTS)

%.elf:
	$(LD) $(LDFLAGS) -T $< -N -o $@ $(OBJECTS)
	chmod -x $@

main.o: $(LOADER_DIRECTORY)/main.c
	$(compile)

%.o: $(LOADER_DIRECTORY)/%.S
	$(assemble)

clean:
	$(RM) $(OBJECTS) loader.elf loader.bin .*~ *~

.PHONY: all clean main.o
