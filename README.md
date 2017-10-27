# BlackBeanControl - Broadlink RM 3 Mini (aka Black Bean) control script
This repo use most of the code from  
https://github.com/davorf/BlackBeanControl and   
https://github.com/mjg59/python-broadlink  
Just put it together, add some enchance and update to support python3   


## Setup
```
git clone https://github.com/TheGU/rm3_mini_controller.git
cd rm3_mini_controller
pip install -r requirements.txt
python test_run.py
```
After call test run. The script will dicover RM3 in your network and display info about it. Then ask you to test input any remote key to rm3 and it will repeat signal to test read and send ir remote.

Use the information you got from test_run to config BlackBeanControl.ini something like this:
```
[General]
IPAddress = 192.168.0.1
Port = 80
MACAddress = AA:BB:CC:DD:EE:FF
Timeout = 30
```

## Usage
For more detail command please see [README_blackbeancontrol.md](README_blackbeancontrol.md)
#### Learn command run  
```
python BlackBeanControl.py -c <COMMAND NAME>
```
After learned command. <COMMAND NAME> will appear in BlackBeanControl.ini file under [Command] section with learned ir code   

#### Send command
```
python BlackBeanControl.py -c <COMMAND NAME>
```
If <COMMAND NAME> exist in BlackBeanControl.ini, script will forward ir code for RM3 to broadcast.

