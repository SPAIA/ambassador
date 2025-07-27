ifneq ($(KERNELRELEASE),)
include Kbuild

else
KVERSION ?= `uname -r`
KDIR ?= /lib/modules/${KVERSION}/build
default:
	CONFIG_DRIVER_ST_VL53L7CX=m $(MAKE) -C $(KDIR) M=$(PWD)

clean:
	CONFIG_DRIVER_ST_VL53L7CX=m $(MAKE) -C $(KDIR) M=$(PWD) clean

dtb:
	sudo rm -f /boot/overlays/stmvl53l7cx.dtbo
	dtc -I dts -O dtb -o stmvl53l7cx.dtbo stmvl53l7cx.dts
	sudo cp stmvl53l7cx.dtbo /boot/overlays/stmvl53l7cx.dtbo

insert :
	sudo insmod stmvl53l7cx.ko

remove :
	sudo rmmod stmvl53l7cx
	
endif
