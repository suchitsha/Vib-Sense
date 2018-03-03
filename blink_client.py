# monodepth
import numpy as np
import RPi.GPIO as GPIO
import time
from flask import Flask, request
import json
import re

#LedPin = 40    # pin11
pin_arr = [3,5,7,11,13,15,19,21,23]

def setup(LedPin):
  GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
  GPIO.setup(LedPin, GPIO.OUT)   # Set LedPin's mode is output
  # GPIO.output(LedPin, GPIO.HIGH) # Set LedPin high(+3.3V) to turn on led

app = Flask(__name__)

@app.route('/depth_grid', methods=['POST'])
def depth_grid():
  f = request.get_json()
  f = str(f)
  f = f.replace("[","")
  f = f.replace("]","")
  rows = f.split("\n")
  row0 = rows[0]
  row1 = rows[1]
  row2 = rows[2]
  data0 = np.fromstring(row0,sep=' ') 
  data1 = np.fromstring(row1,sep=' ') 
  data2 = np.fromstring(row2,sep=' ')  - 0.1
  arr=[]
  binary0 = data0 
  binary1 = data1
  binary2 = data2 # np.around(data2)
  arr.extend(binary0)
  arr.extend(binary1)
  arr.extend(binary2)
  print(arr)
  for ar in range(len(arr)):
    if (arr[ar] < 0.65):
     arr[ar]=0.0
    else:
      arr[ar]=1.0
  print(arr)
  print(arr[0],arr[1],arr[2])
  print(arr[3],arr[4],arr[5])
  print(arr[5],arr[7],arr[8])
  
  for  it in range(len(arr)):
    if(arr[it]==0):
      pin_num = int(pin_arr[it])
      setup(pin_num)
      GPIO.output(pin_num,GPIO.LOW)
    else:
      #blink led number "it"
      pin_num  = int(pin_arr[it])
      setup(pin_num)
      GPIO.output(pin_num,GPIO.HIGH)
   # time.sleep(1)
  #for it1 in range(len(pin_arr)):
  #  pin_num = int(pin_arr[it1])
  #  setup(pin_num)
  #  GPIO.output(pin_num,GPIO.LOW)
  
  #print(binary0)
  #print(binary1)
  #print(binary2)
  return 'ok'
#  while(True):
#    GPIO.output(LedPin, GPIO.HIGH)  # led on
#    time.sleep(1)
#    GPIO.output(LedPin, GPIO.LOW) # led off
#    time.sleep(1)

def destroy():
  # GPIO.output(LedPin, GPIO.LOW)   # led off
  GPIO.cleanup()                  # Release resource

if __name__ == '__main__':     # Program start from here
  #setup()
  app.run(debug=True,host="0.0.0.0")
  print('say what')
  destroy()
#  try:
#    blink()
#  except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
#    destroy()
