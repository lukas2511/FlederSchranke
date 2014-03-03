MCU=atmega2560
MCUFREQ=-DF_CPU=16000000UL
SERPORT=/dev/cu.usbmodem1411
SERPORT_BB=/dev/ttyO4
PROGTYPE=wiring
BAUDRATE=115200
SOURCES=main.c
TARGET=main

.PHONY: build upload

build: $(TARGET).hex

upload: build
	avrdude -D -P $(SERPORT) -p $(MCU) -c $(PROGTYPE) -b $(BAUDRATE) -U flash:w:$(TARGET).hex:i

upload_bb: build
	echo 0 > /sys/class/gpio/gpio9/value
	sleep 1
	echo 1 > /sys/class/gpio/gpio9/value
	avrdude -D -P $(SERPORT_BB) -p $(MCU) -c $(PROGTYPE) -b $(BAUDRATE) -U flash:w:$(TARGET).hex:i

avrdude:
	avrdude -P $(SERPORT) -p $(MCU) -c $(PROGTYPE) -b $(BAUDRATE)

$(TARGET).elf: $(SOURCES) Makefile
	avr-gcc $(MCUFREQ) -O3 -o $@ -mmcu=$(MCU) $(SOURCES)
	
$(TARGET).hex: $(TARGET).elf Makefile
	avr-objcopy -O ihex -R .eeprom $< $@

clean:
	rm -f main.hex main.elf

rebuild: clean build

