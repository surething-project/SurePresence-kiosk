# SurePresence-kiosk
Kiosk Component of SurePresence, a SureThing application integrating the SureThing framework.

## Installation
This component is heavily based on Python3 (Tested with 3.7 and 3.9).
### Pip packages

#### PyQt5
```bash
pip3 install PyQt5
```
If it takes too long or outputs errors, try
```bash
sudo apt-get install python3-pyqt5
```

#### Tkinter
```bash
pip3 install tkintertable
```

If it takes too long or outputs errors, try

```bash
sudo apt-get install python3-tk
```

#### ImageTk
```bash
sudo apt-get install python3-pil.imagetk
```

### Windows / AMD64 Linux Distributions
To make use of the citizen card reader you need to install the 
official portuguese government middleware.

https://www.autenticacao.gov.pt/web/guest/cc-aplicacao

### Raspberry Pi / ARM64 Linux Distributions
Tested with:
 - Raspberry Pi 4 with Ubuntu Desktop 21.04

The following steps were taken from https://github.com/amagovpt/autenticacao.gov but with minor changes:

#### Dependencies installation
Run
```bash
sudo apt install build-essential libpcsclite-dev libpoppler-qt5-dev libzip-dev libopenjp2-7-dev libpng-dev qtbase5-dev qt5-qmake qtbase5-private-dev qt5-default qtdeclarative5-dev qtquickcontrols2-5-dev qml-module-qtquick-controls2 libssl-dev libxerces-c-dev libxml-security-c-dev swig libcurl4-nss-dev
```
If apt does not find the *qt5-default* just remove if from the command above.

Then, run

```bash
sudo apt install pcscd qml-module-qt-labs-folderlistmodel qml-module-qt-labs-settings qml-module-qt-labs-platform qml-module-qtgraphicaleffects qml-module-qtquick-controls qml-module-qtquick-controls2 qml-module-qtquick-dialogs qml-module-qtquick-layouts qml-module-qtquick-templates2 qml-module-qtquick-window2 qml-module-qtquick2 qt5-gtk-platformtheme libnsspem fonts-lato
```

Then, clone the official github repo
```bash
git clone https://github.com/amagovpt/autenticacao.gov
```

Then, compile the project
```bash
cd autenticacao.gov/pteid-mw-pt/_src/eidmw
qmake pteid-mw.pro
make
```

If you get the mistake that jinit.h file cannot be found and the make process has 
to abort is because a specific Makefile is expecting the openJDK amd64 version and 
not the arm64 one.

#### Solution
```bash
nano eidlibJava_Wrapper/Makefile 
```
Go to the ***INC_PATH*** option and locate these two parameters
```bash
-I/usr/lib/jvm/java-11-openjdk-amd64/include -I/usr/lib/jvm/java-11-openjdk-amd64/include/linux
```
Change them to
```bash
-I/usr/lib/jvm/java-11-openjdk-arm64/include -I/usr/lib/jvm/java-11-openjdk-arm64/include/linux
```
If you have other Java version, simply the number will change.

Exit nano and save the file (CTRL ^ X + Y + Enter)

Finish the installation with
```bash
make install && sudo ldconfig
```
## How to run
```bash
python kiosk_new.py
```
or
```bash
python3 kiosk_new.py
```
depending on your python installations.

