import time
from threading import Thread

import pexpect
import subprocess
import pickle
import sys
import os

patterns_scan1 = ['(.)NEW(.)', pexpect.EOF, pexpect.TIMEOUT]
patterns_scan2 = ["\r\n", pexpect.EOF, pexpect.TIMEOUT]
pattern_connection_successful = ['(.)*', pexpect.EOF, pexpect.TIMEOUT]
pattern_descriptor = [r'Characteristic value/descriptor:', pexpect.EOF, pexpect.TIMEOUT]
patterns_pair = [r'\[agent\](.)*', pexpect.EOF, pexpect.TIMEOUT]
patterns_char = [r'\[agent\](.)*', pexpect.EOF, pexpect.TIMEOUT]

my_mac = "DC:A6:32:68:67:46"

#devices = {}

bl = None

class BluetoothctlError(Exception):
    """This exception is raised, when bluetoothctl fails to start."""
    pass


class gatt:
    """A wrapper for gatttool utility."""

    def __init__(self, mac):
        out = subprocess.check_output("rfkill unblock bluetooth", shell = True)

        self.mac = mac
        #self.child_bctl = pexpect.spawn("bluetoothctl", echo = True, encoding='utf-8', timeout=10)
        self.child_gatt = pexpect.spawn("gatttool -I")
        #self.child_bctl.logfile_read = open("/tmp/log_bctl", "w")
        #self.child_gatttool.logfile_read = open("/tmp/log_gatt",
    
    def run_on_gatttool(self, command):
        """Run a command in gatttool prompt"""
        self.child_gatt.sendline(command)

    def disconnect(self):
        self.run_on_gatttool("disconnect " + self.mac)

    def read_char(self):
        """Connect and read characteristic of device"""

        #Connection process
        self.run_on_gatttool("connect {0}".format(self.mac))
        self.child_gatt.expect("Connection successful", timeout=5)
        print(self.child_gatt.after)
        ####################

        self.run_on_gatttool("mtu 512") #Define read maximum size
        self.run_on_gatttool("char-read-hnd 0x002b") #Reads the characteristic

        #Wait for the value
        self.child_gatt.expect("Characteristic value/descriptor: ", timeout=10)
        self.child_gatt.expect("\r\n", timeout=10)
        ###################

        value = self.child_gatt.before.decode('utf-8')

        #Exit safely
        self.disconnect()
        self.child_gatt.terminate(True)
        ############

        return value


class Bluetoothctl:
    """A wrapper for bluetoothctl utility."""

    def __init__(self):
        #out = subprocess.check_output("sudo rfkill unblock all", shell=True)

        self.child_bctl = pexpect.spawn("bluetoothctl", encoding='utf-8')
        self.child_bctl.logfile_read = open("/tmp/log_bctl", "w")

    def power(self, mode):
        self.run_on_bctl("power " + mode)
    

    def run_on_bctl(self, command):
        """Run a command in bluetoothctl prompt"""
        self.child_bctl.sendline(command)

    def pair(self):
        self.run_on_bctl("pair")

    def scan(self, mode):
        """Start/Stop bluetooth scanning process."""
        try:
            self.run_on_bctl("scan " + mode)
        except BluetoothctlError as e:
            print(e)
            return None

    def getDeviceName(self, list):
        """Aux function to obtain the name of the device that comes after the MAC address"""
        name = ''
        for s in list:
            name += str(s)
            name += ' '

        print(name[:-1])
        return name[:-1]

    def scan_wait(self):
        """Start bluetooth scanning process."""
        """Main function"""
        counter = 0
        print("scan_wait")
        global devices
        try:
            self.scan("on")
        except BluetoothctlError as e:
            print(e)
            return None
        while (1):
            state = self.child_bctl.expect(patterns_scan1, timeout=3)
            if(state == 0):
                state = self.child_bctl.expect(patterns_scan2, timeout=3)
                if (state == 0):  # connectable device
                    devices = {}
                    print(self.child_bctl.before)
                    mac = self.child_bctl.before.split(' ')[2]
                    print(mac)
                    name = self.getDeviceName(self.child_bctl.before.split(' ')[3:])
                    print("append")
                    devices[mac] = name
                    pickle.dump(devices, open("./devices/device_" + str(counter) + ".p", "wb"))
                    counter += 1
                    print("dumped")
                elif (state == 1):  # eof
                    return
                elif (state == 2):  # timeout
                    print("timeout")
                    pickle.dump(devices, open("devices.p", "wb"))
                    print("dumped")
                    self.scan("off")
                    return
                elif (state == 1):  # eof
                    return
            elif (state == 1):  # eof
                return
            elif (state == 2):  # timeout
                print("timeout")
                #pickle.dump(devices, open("devices.p", "wb"))
                print("dumped")
                self.scan("off")
                return

    def power(self, mode):
        """BLE adapter power"""
        try:
            self.run_on_bctl("power " + mode)
        except BluetoothctlError as e:
            print(e)
            return None

    def create_agent(self):
        """ Create agent handler for connections"""
        """NoInputNoOutput is the simplest agent"""
        try:
            self.run_on_bctl("agent off")
            self.run_on_bctl("agent NoInputNoOutput")
        except BluetoothctlError as e:
            print(e)
            return None



def startConnection(mac):
    print("starting connection")
    bl = gatt(mac)
    return bl.read_char()
        
def startBLE():
    print("Starting to scan")
    os.system("sudo systemctl restart bluetooth")
    time.sleep(0.5)
    bl = Bluetoothctl()
    bl.power("on")
    bl.create_agent()
    

    bl.scan_wait()

    bl.child_bctl.terminate(True)


if __name__ == "__main__":
    
    print("running")
    #print("Init bluetooth...")
    bl = Bluetoothctl()
    
    #RESET
    bl.power("off")
    bl.power("on")
    
    bl.create_agent()

    bl.scan_wait()
    
    bl.scan_off()
    bl.power("off")
        





