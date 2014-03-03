# FlederSchranke

## Wat?!

Dies hier sind Software-Stückchen zum Überwachen einer Lichtschranke am Eingang eines Fledermausquartieres.

## Hardware

Die Hardware besteht aus folgenden Komponenten:

### Lichtschranke

- OSRAM Infrarot LED 5 mm, 850 nm, 3° (Als "Sendeeinheit" der Lichtschrankenstrahlen)
- 220 Ohm Widerstände (Als Vorwiderstand für die LEDs)
- Fototransistor Everlight Opto PT 331 C Gehäuseart 5 mm (Als "Empfangseinheit" der Lichtschrankenstrahlen)
- 10 kOhm Widerstände (Als Pullup für die Transistoren, wahrscheinlich unnötig da der ATMega2560 diese theoretisch bereits integriert hat)

#### Lichtschranken-Aufbau

Auf einer Seite sitzen die LEDs mit 220 Ohm Vorwiderständen, auf der anderen Seite die IR-Transistoren mit 10 kOhm Pull-Ups.

Die LEDs und Transistoren sitzen in aufeinander ausgerichteten Röhrchen und sind somit (größtenteils) gegen Einflüsse von außen geschützt.

Eine Centronics-Buchse ist direkt mit den IR-Transistoren verbunden, die Stromversorgung erfolgt über eine Hohlstecker-Buchse.

### Box

- BeagleBone Black (Mehr oder weniger als "Kommunikationsgateway", ein Computer halt)
- Arduino Mega 2560 (Als I/O Board)
- DS1307 (Als Echtzeituhr damit das Beaglebone auch ohne Internetverbindung weiß wie spät es ist)
- Huawei E220 (Für die Internetverbindung zum Übertragen der Logs und zur Fernwartung)
- ELV USB-WDE1 (Zum Empfangen von Daten von einigen Wettersensoren, nette zusätzliche Informationen)
- Bluetoothmodul HC-05 (Zum kabellosen Zugriff auf das Beaglebone Black vor Ort)

#### Box-Aufbau

Aussenliegende Anschlüsse zur Lichtschranke (hier ebenfalls eine Centronics-Buchse) gehen direkt an das Arduino Mega.

Das Arduino Mega ist mit UART4 (P9_11, P9_13) und einem GPIO-Pin (P8_33) für den Reset verbunden.
Zwischen BB-RX und Arduino-TX ist ausserdem ein 10kOhm Widerstand positioniert, dieser fungiert als Ersatz für einen Levelconverter,
welchen ich wegen Zeitdruck nicht mehr besorgen konnte.

Der 3G-Stick ist über ein kurzes (~10cm) USB-Verlängerungskabel direkt mit dem Beaglebone Black verbunden.

Die Echtzeituhr ist mit den Pins P9_19 und P9_20 verbunden.

Der ELV USB-WDE1 Wetterdatenlogger ist mit UART5 (P8_37, P8_38) verbunden.

Das HC-05 Bluetoothmodul hängt am FTDI-Header des Beaglebones und ist an den 3.3V Ausgang vom Arduino Mega angeschlossen.
Ich war mir unsicher ob die Stromversorgung am Beaglebone Black beim Reset bestehen bleibt,
und wollte die Verbindung zum Modul bei einem Reset nicht verlieren.

Stromversorgung für den Rest ist direkt aus einer Hohlstecker-Buchse gesplittet und über entsprechende Pinheader
oder angelötete Kabel verbunden.

Weiterhin gibt es eine weitere Hohlstecker-Buchse als Ausgang für den Anschluss der Lichtschranke.

## Installationsanleitung

### Root-Passwort setzen

```bash
passwd root
```

### Systemdienste abschalten

```bash
systemctl disable gdm
systemctl disable mpd
systemctl disable bonescript-autorun
systemctl disable bonescript
systemctl disable cloud9
systemctl disable avahi-daemon
systemctl disable avahi-daemon.socket
systemctl disable connman.service
systemctl disable storage-gadget-init.service
systemctl disable bonescript.socket
systemctl disable cpu-ondemand.timer
```

### HDMI abschalten, UART anschalten

```bash
mount /dev/mmcblk0p1 /media/BEAGLEBONE/
echo 'optargs=capemgr.enable_partno=BB-UART4,BB-UART5 capemgr.disable_partno=BB-BONELT-HDMI,BB-BONELT-HDMIN' > /media/BEAGLEBONE/uEnv.txt
```

### Zeitzone setzen und Zeit automatisch synchronisieren lassen

```bash
opkg install tzdata-europe
timedatectl set-timezone Europe/Berlin
opkg install ntp
```

### Sakis3G Abhängigkeiten installieren

```bash
opkg install glibc-utils ppp libusb-1.0-0 libusb-0.1-4 libusb-1.0-dev libusb-0.1-dev
```

### OpenVPN bauen

Ist leider nicht in den Paketquellen enthalten und muss daher frisch gebaut werden.

```bash
cd /usr/src
wget http://swupdate.openvpn.org/community/releases/openvpn-2.3.2.tar.gz
tar -vzxf openvpn-2.3.2.tar.gz
cd openvpn-2.3.2
./configure --enable-ssl --enable-lzo
make
make install
```

### OpenSSH installieren

Ich würde zwar gerne Dropbear benutzen da es doch um einiges schmaler daher kommt,
aber leider lässt es nach einigen Stunden Uptime keine Verbindung mehr zu,
läuft aber weiter und wirft auch keine Fehler...

```bash
opkg remove dropbear --force-remove --force-removal-of-dependent-packages
killall -9 dropbear
opkg install openssh
systemctl restart sshd
```

### Python installieren

```bash
opkg update
opkg install python-pip python-setuptools python-smbus python-pyserial
pip install pytz
```

### Automatisch neu starten bei Systemfehler (Software-"Watchdog")

```bash
echo 'kernel.panic = 20' >> /etc/sysctl.conf
```

### Hardware-Watchdog (Reset bei Absturz)

```bash
sed -i 's/#RuntimeWatchdogSec=0/RuntimeWatchdogSec=10/g' /etc/systemd/system.conf
sed -i 's/#ShutdownWatchdogSec=10min/ShutdownWatchdogSec=50/g' /etc/systemd/system.conf
```

### gnokii 

Ist leider nicht in den Paketquellen enthalten und muss daher frisch gebaut werden.
Wird nicht unbedingt benötigt, ist aber praktisch um z.B. Provider-SMS zu Empfangen.

```bash
opkg install intltool
cd /usr/src
wget http://www.gnokii.org/download/gnokii/0.6.x/gnokii-0.6.31.tar.bz2
tar xvf gnokii-0.6.31.tar.bz2
cd gnokii-0.6.31
./configure
make
make install
```

### Services installieren

```bash
cp /home/root/lichtschranke/lichtschranke.service /lib/systemd/system/
systemctl enable lichtschranke.service
cp /home/root/lichtschranke/3g/ping.service /lib/systemd/system/
systemctl enable ping.service
cp /home/root/lichtschranke/rtc/rtc-ds1307.service /lib/systemd/system/
systemctl enable rtc-ds1307.service
```

### Wake-up-Call konfigurieren

```bash
echo 'number="+491711234567"' > /home/root/lichtschranke/wakeupcall/config.py
```

### Neu starten, und hoffen.

```bash
reboot
```

### Read-Only /-Partition

Da ich nicht wollte dass mir irgendetwas meine /-Partition mit Logs o.Ä. vollschreibt habe ich diese Read-Only gemountet.

Um trotzdem noch Logs für die Lichtschranke und die Wetterdaten zu schreiben habe ich eine MicroSD-Karte verbaut und `/etc/fstab` folgendermaßen angepasst:

```
rootfs               /                    auto       defaults,noatime,ro   1  1
UUID="52E2-E81E"     /media/BEAGLEBONE    vfat       defaults,noatime      0  0

proc                 /proc                proc       defaults              0  0
devpts               /dev/pts             devpts     mode=0620,gid=5       0  0
tmpfs                /tmp                 tmpfs      defaults              0  0

tmpfs                /var/tmp             tmpfs      defaults              0  0
tmpfs                /var/run             tmpfs      defaults              0  0
tmpfs                /var/log             tmpfs      defaults              0  0
tmpfs                /var/lock            tmpfs      defaults              0  0

UUID="530F-FFFE"     /home/root/logs      vfat       defaults,noatime      0  0
```

Ausserdem muss auf der MicroSD-Karte eine Datei `uEnv.txt` mit folgendem Inhalt angelegt werden:

```
mmcdev=1
bootpart=1:2
mmcroot=/dev/mmcblk1p2 ro
optargs=capemgr.enable_partno=BB-UART4,BB-UART5 capemgr.disable_partno=BB-BONELT-HDMI,BB-BONELT-HDMIN
```

# Lizenz

Da die meiste verwendete Software unter GPL(v2) steht setze ich meine Parts unter GPLv3.
