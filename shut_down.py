import RPi.GPIO as GPIO
import time

#LedPin = 5
l_arr = [3,5,7,11,13,15,19,21,23]   # pin11

def setup(LedPin):
  GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
  GPIO.setup(LedPin, GPIO.OUT)   # Set LedPin's mode is output
  GPIO.output(LedPin, GPIO.HIGH) # Set LedPin high(+3.3V) to turn on led

def blink():
  while True:
    for i in range(len(l_arr)):
      LedPin = l_arr[i]
      #GPIO.output(LedPin, GPIO.HIGH)  # led on
      #time.sleep(1)
      setup(LedPin)
      GPIO.output(LedPin, GPIO.LOW) # led off
      time.sleep(1)

def destroy():
  for j in range(len(l_arr)):
    LedPin = l_arr[j]
    GPIO.output(LedPin, GPIO.LOW)   # led off
    GPIO.cleanup()                  # Release resource

if __name__ == '__main__':     # Program start from here
  #setup()
  try:
    blink()
  except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    destroy()
