# Build and install on the Pi itself:
#
#   make            # the module (nhe-i2s-codec.ko) and the overlay (.dtbo)
#   sudo make install
#   sudo reboot
#
# Needs the headers for the running kernel (see README.md) and dtc
# (sudo apt install device-tree-compiler). After a kernel update, run
# make and sudo make install again: a module is built for one kernel.

obj-m := nhe-i2s-codec.o

KVER    ?= $(shell uname -r)
KDIR    ?= /lib/modules/$(KVER)/build
OVERLAYS ?= $(firstword $(wildcard /boot/firmware/overlays /boot/overlays))

all: module dtbo

module:
	$(MAKE) -C $(KDIR) M=$(CURDIR) modules

dtbo: nhe-i2s-duplex.dtbo

nhe-i2s-duplex.dtbo: nhe-i2s-duplex-overlay.dts
	dtc -@ -I dts -O dtb -o $@ $<

install: all
	install -D -m 644 nhe-i2s-codec.ko /lib/modules/$(KVER)/extra/nhe-i2s-codec.ko
	depmod -a $(KVER)
	install -m 644 nhe-i2s-duplex.dtbo $(OVERLAYS)/nhe-i2s-duplex.dtbo
	@echo "Installed. Add 'dtoverlay=nhe-i2s-duplex' to config.txt (and remove"
	@echo "'dtoverlay=hifiberry-dac' if you tried that first), then reboot."

clean:
	$(MAKE) -C $(KDIR) M=$(CURDIR) clean
	rm -f nhe-i2s-duplex.dtbo

.PHONY: all module dtbo install clean
