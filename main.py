#--------------------------------------------------------------
# Short programm for testing microphyton on esp32
# Author: King Keule
# GitHub: https://github.com/KingKeule/ESP32_Toolbox_MicroPython
#--------------------------------------------------------------


# Define menu entries
def showMenu():
   print('###### ESP32 Toolbox (MicroPython) ######')
   print('  0. Exit toolbox')
   print('  1. System info') 
   print('  2. Network status')
   print('  3. WLAN - manager')
   print('  4. WLAN - port scanner')
   print('  5. WLAN - deauther')
   print('  6. Bluetooth LE - scan')
   print('  7. Time synchronization')
   print('  8. Directory overview')
   print('  9. Debug options')
   print(' 10. I2C - display (SSD1306)')
   print(' 11. Touch pin check')
   print('-----------------------------------------')

def showSelectedMenuEntry(argument):
   switcher = {
                1: systemInfo,
                2: networkStat,
                3: scanWLAN,
                4: portScanWLAN,
                6: scanBLE,
                7: timeSync,
                8: fileManager,
                9: debugOpt,
               10: i2cDisplaySSD1306,
               11: touchPinCheck
             }
   switcher.get(argument, lambda:'Invalid menu entry.')()

# -------------------- Toolbox functions --------------------
def systemInfo(): 
   import sys
   import machine
   from machine import RTC
   import esp
   import esp32
   import os
   
   print('######  ESP32 info ######')
   print(' Hardware')
   print('  - ESP plattform: ' + sys.platform)
   print('  - CPU frequenz: %d kHz' % (machine.freq()/1000000))
   print('  - MCU Temperature: %d °C' % ((esp32.raw_temperature() - 32) * 5/9))
   print('  - Flash size: %d kBytes' % (esp.flash_size()/1024))
   print('  - Flash user start: %d' % esp.flash_user_start())
   print(' Software')
   print('  - Python version: %s' % sys.version)
   print('  - MicroPython version: %s'  % os.uname()[3]) #https://docs.micropython.org/en/latest/library/os.html
   # print(sys.modules)
   rtc = RTC()
   print(' Info')
   print('  - Real time clock')
   print('     Date: %02d.%02d.%d' % (rtc.datetime()[2], rtc.datetime()[1], rtc.datetime()[0]))
   print('     Time: %02d:%02d:%02d' % (rtc.datetime()[4], rtc.datetime()[5], rtc.datetime()[6]))   
   
def networkStat():
   import network
   import ubinascii
   import ubluetooth
   
   print('###### Network status ######')
   # https://docs.micropython.org/en/latest/library/network.WLAN.html
   wlan = network.WLAN(network.STA_IF)
   print(' WLAN:')    
   print('  - MAC: '+ ubinascii.hexlify(network.WLAN().config('mac'),':').decode('utf-8'))
   
   connected = wlan.isconnected()
   if connected:
      print('  - Connected to "%s" (RSSI: %d)' % (wlan.config('essid'), wlan.status('rssi')))
      print('     Network name: %s' % wlan.config('dhcp_hostname'))
      print('     IP:      %s' % wlan.ifconfig()[0])
      print('     Netmask: %s' % wlan.ifconfig()[1]) 
      print('     Gateway: %s' % wlan.ifconfig()[2]) 
      print('     DNS:     %s' % wlan.ifconfig()[3])
   else:
      print('  - Connected: %s' % connected)
   
   ble = ubluetooth.BLE()
   ble.active(True) #must be active before using any other methods of BLE().
   print(' Bluetooth LE:')
   print('    MAC: '+ ubinascii.hexlify(ble.config('mac')[1],':').decode('utf-8'))
   print('    Name: ' + ble.config('gap_name').decode('utf-8'))

   # print("\nNetworking:")
   # print("AP ifconfig:", network.WLAN(network.AP_IF).ifconfig())

def scanWLAN():
   import network
   import machine
   import time
   import ubinascii
   
   print('###### WLAN manager ######')    
   wlan = network.WLAN(network.STA_IF)
   if wlan.isconnected():
      print('Connected to WLAN: %s' % wlan.config('essid'))
   else:
      print('Connected to WLAN: None')
       
   operation = int(input("Operation (0: exit menu, 1: disconnect current WLAN, 2: scan WLANs): "))
   if operation == 0:
       return
  
   if operation == 1:
       if wlan.isconnected():
          wlan.disconnect()
          print('Disconnect from WLAN "%s" successful.' % wlan.config('essid'))
       else:
          print('Disconnecting the WLAN is not possible because it is not connected.')
       return

   if operation > 2:
       print('Operation not defined.')
       return
 
   wlan.active(True)
   wlanNetworks = wlan.scan()
   # https://docs.micropython.org/en/latest/library/network.WLAN.html
   AUTHMODES = {0: "open", 1: "WEP", 2: "WPA-PSK", 3: "WPA2-PSK", 4: "WPA/WPA2-PSK", 7: "WPA2-WPA3"} 
   i=1
   print('###### WLAN networks ######')    
   #for ssid, bssid, channel, rssi, authmode, hidden in sorted(wlanNetworks, key=lambda x: x[3], reverse=True):
   for ssid, bssid, channel, rssi, authmode, hidden in wlanNetworks:
       print(" %2d: SSID: %-25s | Channel: %2d | RSSI: %d | Hidden: %05s | Auth: %s" %
            (i, ssid.decode('utf-8'), channel, rssi, hidden, AUTHMODES.get(authmode, 'unknown')))
       i += 1

   userSelectedWlan = int(input("Select WLAN: "))
   selectedWLAN = wlanNetworks[userSelectedWlan-1]
   ssid = selectedWLAN[0]
   authmode = selectedWLAN[4]

   if wlan.isconnected():
     wlan.disconnect()

   password =''
   if (authmode > 0):
       password = input("Password: ")
   wlan.connect(ssid.decode('utf-8'), password)
     
   i = 1
   while not wlan.isconnected():
         #TODO handle wrong password
#        status = wlan.status() # not working yet https://forum.micropython.org/viewtopic.php?f=18&t=7942
#        if status == network.STAT_IDLE:
#           print( 'STAT_IDLE')
#        elif status == network.STAT_CONNECTING:
#           print( 'STAT_CONNECTING')
#        elif status == network.STAT_WRONG_PASSWORD:
#           print( 'STAT_WRONG_PASSWORD')
#        elif status == network.STAT_NO_AP_FOUND:
#           print( 'STAT_NO_AP_FOUND')
#        elif status == network.STAT_CONNECT_FAIL:
#           print( 'STAT_CONNECT_FAIL')
#        elif status == network.STAT_GOT_IP:
#           print( 'STAT_GOT_IP')
#        else:
#           print( "Unknown wlan status")
#        machine.idle() # save power while waiting alterative "pass"

       i += 1
       time.sleep(1)
       if i == 5: # connection timeout after 5 sec
          print('Connection to WLAN "%s" not successful. Maybe password wrong?' % ssid.decode('utf-8'))
          wlan.active(False) #otherwise wlan.scan() not working?!
          return  

   print('Connection to WLAN "%s" successful.' % ssid.decode('utf-8'))
   
def portScanWLAN():
   #https://docs.micropython.org/en/latest/library/socket.html#socket.socket
   import network
   import socket

   wlan = network.WLAN(network.STA_IF)
   if not wlan.isconnected():
      print('No connection to Internet. Please connect first.')
      return
    
   print('###### WLAN port scanner ######')    
   host = '192.168.1.23'
   portStart = 6111
   portEnd = 6114
   #https://www.geeksforgeeks.org/port-scanner-using-python/
   print(' Port scan on host: %s for port(s): %d - %d' % (host, portStart, portEnd))
   for port in range(portStart, portEnd):
      try:
        s = socket.socket()
      # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        res = s.connect((host, port))
        if res == None:
           print(" Port %d open" % port)
        s.close()
      except Exception as e:
        print(" Port %d probably closed. (Reason: %s)" % (port, e))
          
def scanBLE():
   import network
   import ubinascii
   import ubluetooth
   
   print('###### Bluetooth LE Scanner ######')    
   ble = ubluetooth.BLE()
   ble.active(True) #must be active before using any other methods of BLE().
   print(ble.gap_scan(1000))
   #TODO

def timeSync():
   import network
   import ntptime
   from machine import RTC
   
   # ntptime.host = 'time.google.com' # change ntp server, default host is: pool.ntp.org
  
   wlan = network.WLAN(network.STA_IF)
   if not wlan.isconnected():
      print('No connection to Internet. Please connect first.')
      return

   print('###### Time synchronization ######')    
   print('Local time before synchronization:  Date: %02d.%02d.%d   Time: %02d:%02d:%02d' %
         (time.localtime()[2], time.localtime()[1], time.localtime()[0], time.localtime()[3], time.localtime()[4], time.localtime()[5]))
   print('NTP synchronisation with "%s"' % ntptime.host)
   ntptime.settime()
   # add 2 more hours cause of time zone difference in Germany # TODO change between summer and winter time
   rtc = RTC()
   date = list(rtc.datetime())
   date[4] += 2 
   rtc.datetime(date)
   print('Local time after synchronization:   Date: %02d.%02d.%d   Time: %02d:%02d:%02d' %
         (time.localtime()[2], time.localtime()[1], time.localtime()[0], time.localtime()[3], time.localtime()[4], time.localtime()[5]))

def debugOpt(): #todo not working
   import esp
   import sys
   
   print('###### Debug options ######')
   #print(' - Debug mode: %s' % esp.osdebug)
   #esp.osdebug(None)
   #esp.osdebug("*", esp.LOG_VERBOSE)
   esp.osdebug(0, esp.LOG_DEBUG)

#subfunction for fileManager
#print all file names of a given folder and recursive call of the same function for all subfolders in the given folder
def printSubDir(folder): 
    import os
    
    dirList = sorted(os.ilistdir(folder), key=lambda item: item[3] > 0, reverse=True) # optimize sorting
    #print(dirList)
    for dirEntry in dirList:
      if dirEntry[1] == 32768: # 32768 = regular file, 16384 = folder 
         if(folder == '/'):
           print('/%s' % dirEntry[0])
         else:
           print('%s/%s' % (folder, dirEntry[0]))
      else:
         if(folder == '/'):
           printSubDir('/%s' % dirEntry[0])
         else:
           printSubDir('%s/%s' % (folder, dirEntry[0]))

def fileManager(): 
   import os
   print('###### Directory overview ######')    
   printSubDir('/')

# driver: https://github.com/micropython/micropython/blob/master/drivers/display/ssd1306.py
# https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html
def i2cDisplaySSD1306():
   from machine import Pin, SoftI2C
   from ssd1306 import SSD1306_I2C
   import time 

   print('###### I2C - display (SSD1306) ######')
   # use of SoftI2C interface due I2C(-1, ...) is deprecated
   # ESP32 Dev Kit C V4 - I2C pins are: SDA: 21, SCL: 22
   # due to lack of space on the breadboard the following pins are used alternatively SDA: GPIO9 (D2), SCL: GPIO10 (D3)
   i2cBus = SoftI2C(scl=Pin(10), sda=Pin(9), freq = 400000) # I2C Fast Mode (Fm): 0,4 Mbit/s
   
   i2cBusDevices = i2cBus.scan()
   print('Scan for devices on I2C bus')

   if len(i2cBusDevices) == 0:
     print("No i2c device found. Please check your circuit!")
     return
   else:
    print('Number of devices on I2C bus: %d' % len(i2cBusDevices))
   
   addrDisplay = 60  # default address of the display: 0x3C
   for deviceAddr in i2cBusDevices: 
      if deviceAddr == addrDisplay:
         oledIsConnected = True
         print('Found display on I2C bus at address: %s' %hex(deviceAddr))

   if not oledIsConnected:
      print("No I2C dislay found. Please check your circuit!")
      return
  
   print('Activate display and show text')
   oledWidth = 128
   oledHeight = 32
   oled = SSD1306_I2C(oledWidth, oledHeight, i2cBus, addrDisplay) 
   oled.contrast(100)  # brightness (0 - 255)
   oled.invert(False)
   oled.fill(0) # clear display to remove old drawings
   oled.text("ESP32 Toolbox", 0, 0)
   oled.text("(MicroPython)", 0, 12)
   oled.text("by KingKeule", 0, 24)
   oled.rect(113, 0, 15, 32, 1) # x, y, width, height, color
   oled.show()
   
   time.sleep(1)
 
   for column in range(1, 31):
      oled.hline(114, column, 13, 1) # x, y, width, color
      oled.show()
      time.sleep(0.1)

   time.sleep(2)
   print('Deactivate display')
   oled.poweroff()

#https://docs.micropython.org/en/latest/esp32/quickref.html#capacitive-touch
def touchPinCheck():
   from machine import TouchPad, Pin
   import time

   #configure touchpin(s): GPIO32 (Touch 9), GPIO33 (Touch 8)
   tPin32 = TouchPad(Pin(32))
   tPin33 = TouchPad(Pin(33))
   
   print('###### Touch pin check ######')
   print(' NOTE: This check only works if the touch pin was not tapped during startup!')
   print(' You have 10 seconds to tap a configured touch pin ;-)')
   
   startValuetPin32 = tPin32.read()
   startValuetPin33 = tPin33.read()
 
   for sec in range (20):
      curValuetPin32 = tPin32.read()
      curValuetPin33 = tPin33.read()

      # Checking whether the current value is less than 50% of the maximum value measured at startup
      if ((curValuetPin32 / startValuetPin32 * 100) < 50): 
         print(' Touch pin (GPIO32) tapped')
      if ((curValuetPin33 / startValuetPin33 * 100) < 50): 
         print(' Touch pin (GPIO33) tapped')  

      time.sleep(0.5)

# -------------------- Toolbox loop --------------------
while True:  
   import time 

   showMenu()   
   userSelectedMenuEntry = int(input("Select menu entry: "))
   if userSelectedMenuEntry == 0: # stop the loop
       break
   showSelectedMenuEntry(userSelectedMenuEntry)
   print('')
   time.sleep(2)

