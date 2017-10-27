#!/usr/bin/python

import broadlink
import time
import re
import binascii

print('Scanning network for Broadlink devices (5s timeout) ... ')
devices = broadlink.discover(timeout=5)
print(('Found ' + str(len(devices )) + ' broadlink device(s)'))
time.sleep(1)
for index, item in enumerate(devices):
    devices[index].auth()
m = re.match(r"\('([0-9.]+)', ([0-9]+)", str(devices[index].host))
ipadd = m.group(1)
port = m.group(2)
macadd = str(''.join(format(x, '02x') for x in devices[index].mac[::-1]))
macadd = macadd[:2] + ":" + macadd[2:4] + ":" + macadd[4:6] + ":" + macadd[6:8] + ":" + macadd[8:10] + ":" + macadd[10:12]
print(('Device ' + str(index + 1) +':\nIPAddress = ' + ipadd + '\nPort = ' + port + '\nMACAddress = ' + macadd))
print("enter_learning (5s timeout) please press any key on remote to test")
devices[0].enter_learning()
time.sleep(5)
print("Check data")
ir_packet = devices[0].check_data()
if ir_packet:
    decode_command = binascii.hexlify(ir_packet).decode("ascii")
    print(decode_command)
    encode_command = binascii.unhexlify(decode_command)
    print("Test resend")
    devices[0].send_data(encode_command)
else:
    print("RM3 not receive any remote command")