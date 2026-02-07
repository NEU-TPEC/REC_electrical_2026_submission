from machine import Pin, PWM
from utime import sleep

frequency = 4
usteps = 6400

pulse = Pin(0, Pin.OUT, value=0)
motor = PWM(pulse, freq=frequency*usteps, duty_u16=2**16//2)
en = Pin(1, Pin.OUT, value=1)
dir = Pin(2, Pin.OUT, value=0)

for _ in range(3):
    sleep(1)