from machine import Pin, I2C
from utime import sleep
from enum import Enum


######################
##                  ##
##    INPUT Pins    ##
##                  ##
######################



## Control Buttons

dispatch_button = Pin(0, Pin.IN)    # TODO: Change Pin
ride_stop_button = Pin(0, Pin.IN)   # TODO: Change Pin
soft_reset_button = Pin(0, Pin.IN)  # TODO: Change Pin

operator_tag = I2C(
    0,              # TODO: Change I2C Driver
    scl=Pin(0),     # TODO: Change Pin
    sda=Pin(0),     # TODO: Change Pin
    freq=400000     # TODO: Change Frequency
    )


## Safety Checks

operator_restraint_button = Pin(0, Pin.IN)  # TODO: Change Pin

tilt_sensor = Pin(0, Pin.IN)                # TODO: Change Pin



#######################
##                   ##
##    Output Pins    ##
##                   ##
#######################

restraint_indicator = Pin(0, Pin.OUT)
loading_state_indicator = Pin(0, Pin.OUT)

lcd_output = I2C(
    0,              # TODO: Change I2C Driver
    scl=Pin(0),     # TODO: Change Pin
    sda=Pin(0),     # TODO: Change Pin
    freq=400000     # TODO: Change Frequency
    )






#######################
##                   ##
##    Ride States    ##
##                   ##
#######################

class Ride_States(Enum):
    RIDE_LOCKED = {
        "Safe": True
    }

    RESTRAINTS_OPEN = {
        "Safe": True
    }

    ALL_CLEAR = {
        "Safe": True
    }

    RIDE_STARTED = {
        "Safe": True
    }

    RIDE_TILTED = {
        "Safe": True
    }

    RIDE_ENDED = {
        "Safe": True
    }

    MOVING_WITH_OPEN_RESTRAINTS = {
        "Safe": False
    }

    E_STOP = {
        "Safe": False
    }

