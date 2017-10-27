#!/usr/bin/python

import broadlink, configparser
import sys, getopt
import time, binascii
import netaddr
import Settings
import re
from os import path
from Crypto.Cipher import AES

SettingsFile = configparser.ConfigParser()
SettingsFile.optionxform = str
SettingsFile.read(Settings.BlackBeanControlSettings)

def execute_command(
    SentCommand, 
    DeviceName='',
    ReKeyCommand=False, 
    AlternativeIPAddress='',
    AlternativePort='',
    AlternativeMACAddress='',
    AlternativeTimeout=''    
    ):
    if SentCommand == '':
        print('Command name parameter is mandatory')
        return 2

    if SentCommand == 'DISCOVER':
        print('Scanning network for Broadlink devices ... ')

        mydevices = broadlink.discover(timeout=5)
        print(('Found ' + str(len(mydevices )) + ' broadlink device(s)'))
        time.sleep(1)
        for index, item in enumerate(mydevices):
            mydevices[index].auth()

        m = re.match(r"\('([0-9.]+)', ([0-9]+)", str(mydevices[index].host))
        ipadd = m.group(1)
        port = m.group(2)

        macadd = str(''.join(format(x, '02x') for x in mydevices[index].mac[::-1]))
        macadd = macadd[:2] + ":" + macadd[2:4] + ":" + macadd[4:6] + ":" + macadd[6:8] + ":" + macadd[8:10] + ":" + macadd[10:12]

        print(('Device ' + str(index + 1) +':\nIPAddress = ' + ipadd + '\nPort = ' + port + '\nMACAddress = ' + macadd))
        return

    if (DeviceName != '') and (
        (AlternativeIPAddress != '') or 
        (AlternativePort != '') or 
        (AlternativeMACAddress != '') or 
        (AlternativeTimeout != '')
    ):
        print('Device name parameter can not be used in conjunction with IP Address/Port/MAC Address/Timeout parameters')
        return 2

    if (
        (
            (AlternativeIPAddress != '') or 
            (AlternativePort != '') or 
            (AlternativeMACAddress != '') or 
            (AlternativeTimeout != '')
        ) and (
            (AlternativeIPAddress == '') or 
            (AlternativePort == '') or 
            (AlternativeMACAddress == '') or 
            (AlternativeTimeout == '')
        )
    ):
        print('IP Address, Port, MAC Address and Timeout parameters can not be used separately')
        return 2

    if DeviceName != '':
        if SettingsFile.has_section(DeviceName):
            if SettingsFile.has_option(DeviceName, 'IPAddress'):
                DeviceIPAddress = SettingsFile.get(DeviceName, 'IPAddress')
            else:
                DeviceIPAddress = ''

            if SettingsFile.has_option(DeviceName, 'Port'):
                DevicePort = SettingsFile.get(DeviceName, 'Port')
            else:
                DevicePort = ''

            if SettingsFile.has_option(DeviceName, 'MACAddress'):
                DeviceMACAddress = SettingsFile.get(DeviceName, 'MACAddress')
            else:
                DeviceMACAddress = ''

            if SettingsFile.has_option(DeviceName, 'Timeout'):
                DeviceTimeout = SettingsFile.get(DeviceName, 'Timeout')
            else:
                DeviceTimeout = ''
        else:
            print('Device does not exist in BlackBeanControl.ini')
            return 2

    if (DeviceName != '') and (DeviceIPAddress == ''):
        print('IP address must exist in BlackBeanControl.ini for the selected device')
        return 2

    if (DeviceName != '') and (DevicePort == ''):
        print('Port must exist in BlackBeanControl.ini for the selected device')
        return 2

    if (DeviceName != '') and (DeviceMACAddress == ''):
        print('MAC address must exist in BlackBeanControl.ini for the selected device')
        return 2

    if (DeviceName != '') and (DeviceTimeout == ''):
        print('Timeout must exist in BlackBeanControl.ini for the selected device')
        return 2

    if DeviceName != '':
        RealIPAddress = DeviceIPAddress
    elif AlternativeIPAddress != '':
        RealIPAddress = AlternativeIPAddress
    else:
        RealIPAddress = Settings.IPAddress

    if RealIPAddress == '':
        print('IP address must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
        return 2

    if DeviceName != '':
        RealPort = DevicePort
    elif AlternativePort != '':
        RealPort = AlternativePort
    else:
        RealPort = Settings.Port

    if RealPort == '':
        print('Port must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
        return 2
    else:
        RealPort = int(RealPort)

    if DeviceName != '':
        RealMACAddress = DeviceMACAddress
    elif AlternativeMACAddress != '':
        RealMACAddress = AlternativeMACAddress
    else:
        RealMACAddress = Settings.MACAddress

    if RealMACAddress == '':
        print('MAC address must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
        return 2
    else:
        RealMACAddress = netaddr.EUI(RealMACAddress)

    if DeviceName != '':
        RealTimeout = DeviceTimeout
    elif AlternativeTimeout != '':
        RealTimeout = AlternativeTimeout
    else:
        RealTimeout = Settings.Timeout

    if RealTimeout == '':
        print('Timeout must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
        return 2
    else:
        RealTimeout = int(RealTimeout)

    RM3Device = broadlink.rm((RealIPAddress, RealPort), RealMACAddress)
    RM3Device.auth()

    if ReKeyCommand:
        if SettingsFile.has_option('Commands', SentCommand):
            CommandFromSettings = SettingsFile.get('Commands', SentCommand)

            if CommandFromSettings[0:4] != '2600':
                RM3Key = RM3Device.key
                RM3IV = RM3Device.iv

                DecodedCommand = binascii.unhexlify(CommandFromSettings)
                AESEncryption = AES.new(str(RM3Key), AES.MODE_CBC, str(RM3IV))
                EncodedCommand = AESEncryption.encrypt(str(DecodedCommand))
                FinalCommand = EncodedCommand[0x04:]
                EncodedCommand = binascii.hexlify(FinalCommand).decode("ascii")

                BlackBeanControlIniFile = open(path.join(Settings.ApplicationDir, 'BlackBeanControl.ini'), 'w')
                SettingsFile.set('Commands', SentCommand, EncodedCommand)
                SettingsFile.write(BlackBeanControlIniFile)
                BlackBeanControlIniFile.close()
                sys.exit()
            else:
                print("Command appears to already be re-keyed.")
                return 2
        else:
            print("Command not found in ini file for re-keying.")
            return 2


    if SettingsFile.has_option('Commands', SentCommand):
        CommandFromSettings = SettingsFile.get('Commands', SentCommand)
    else:
        CommandFromSettings = ''

    if CommandFromSettings != '':
        DecodedCommand = binascii.unhexlify(CommandFromSettings)
        RM3Device.send_data(DecodedCommand)
    else:
        RM3Device.enter_learning()
        time.sleep(RealTimeout)
        LearnedCommand = RM3Device.check_data()

        if LearnedCommand is None:
            print('Command not received')
            sys.exit()

        print(LearnedCommand)
        # EncodedCommand = LearnedCommand.encode('hex')
        EncodedCommand = binascii.hexlify(LearnedCommand).decode("ascii")
        print(EncodedCommand)

        if EncodedCommand:
            BlackBeanControlIniFile = open(path.join(Settings.ApplicationDir, 'BlackBeanControl.ini'), 'w')
            SettingsFile.set('Commands', SentCommand, EncodedCommand)
            SettingsFile.write(BlackBeanControlIniFile)
            BlackBeanControlIniFile.close()
            print('Set command {0}'.format(SentCommand))


if __name__ == "__main__":
    SentCommand = ''
    ReKeyCommand = False
    DeviceName=''
    DeviceIPAddress = ''
    DevicePort = ''
    DeviceMACAddres = ''
    DeviceTimeout = ''
    AlternativeIPAddress = ''
    AlternativePort = ''
    AlternativeMACAddress = ''
    AlternativeTimeout = ''

    try:
        Options, args = getopt.getopt(sys.argv[1:], 'c:d:r:i:p:m:t:h', ['command=','device=','rekey=','ipaddress=','port=','macaddress=','timeout=','help'])
    except getopt.GetoptError:
        print('BlackBeanControl.py -c <Command name> [-d <Device name>] [-i <IP Address>] [-p <Port>] [-m <MAC Address>] [-t <Timeout>] [-r <Re-Key Command>]')
        sys.exit(2)

    for Option, Argument in Options:
        if Option in ('-h', '--help'):
            print('BlackBeanControl.py -c <Command name> [-d <Device name>] [-i <IP Address>] [-p <Port>] [-m <MAC Address>] [-t <Timeout> [-r <Re-Key Command>]')
            sys.exit()
        elif Option in ('-c', '--command'):
            SentCommand = Argument.strip()
        elif Option in ('-d', '--device'):
            DeviceName = Argument.strip()
        elif Option in ('-r', '--rekey'):
            ReKeyCommand = True
            SentCommand = Argument.strip()
        elif Option in ('-i', '--ipaddress'):
            AlternativeIPAddress = Argument.strip()
        elif Option in ('-p', '--port'):
            AlternativePort = Argument.strip()
        elif Option in ('-m', '--macaddress'):
            AlternativeMACAddress = Argument.strip()
        elif Option in ('-t', '--timeout'):
            AlternativeTimeout = Argument

        execute_command(
        SentCommand, 
        DeviceName=DeviceName,
        ReKeyCommand=ReKeyCommand, 
        AlternativeIPAddress=AlternativeIPAddress,
        AlternativePort=AlternativePort,
        AlternativeMACAddress=AlternativeMACAddress,
        AlternativeTimeout=AlternativeTimeout
        )