from machine import Pin, I2C, PWM
from utime import sleep
# from enum import Enum
from DIYables_MicroPython_LCD_I2C import LCD_I2C


######################
##                  ##
##    INPUT Pins    ##
##                  ##
######################



## Control Buttons

# dispatch_button = Pin(0, Pin.IN)    # TODO: Change Pin
# ride_stop_button = Pin(0, Pin.IN)   # TODO: Change Pin
# soft_reset_button = Pin(0, Pin.IN)  # TODO: Change Pin


# operator_tag = I2C(
#     0,              # TODO: Change I2C Driver
#     scl=Pin(0),     # TODO: Change Pin
#     sda=Pin(0),     # TODO: Change Pin
#     freq=400000     # TODO: Change Frequency
#     )


## Safety Checks

# operator_restraint_button = Pin(0, Pin.IN)  # TODO: Change Pin

# tilt_sensor = Pin(0, Pin.IN)                # TODO: Change Pin

# tof_sensor = Pin(0, Pin.IN)


#######################
##                   ##
##    Output Pins    ##
##                   ##
#######################

# restraint_indicator = Pin(0, Pin.OUT)
# loading_state_indicator = Pin(0, Pin.OUT)

lcd_comm = I2C(
    1,              # TODO: Change I2C Driver
    scl=Pin(19),     # TODO: Change Pin
    sda=Pin(18),     # TODO: Change Pin
    )

LCD_ADDR = 0x27
LCD_ROWS = 2
LCD_COLS = 16
lcd = LCD_I2C(lcd_comm, LCD_ADDR, LCD_ROWS, LCD_COLS)


#########################
##                     ##
##    Motor Control    ##
##                     ##
#########################


frame_pulse = Pin(2, Pin.OUT, value=0)
frame_enable = Pin(3, Pin.OUT, value=1)
frame_direction = Pin(4, Pin.OUT, value=0)
frame_motor = PWM(frame_pulse)
FRAME_USTEPS = 6400



#######################
##                   ##
##    Ride States    ##
##                   ##
#######################

# class Ride_States(Enum):
#     RIDE_LOCKED = {
#         "Safe": True
#     }

#     RESTRAINTS_OPEN = {
#         "Safe": True
#     }

#     ALL_CLEAR = {
#         "Safe": True
#     }

#     RIDE_STARTED = {
#         "Safe": True
#     }

#     RIDE_TILTED = {
#         "Safe": True
#     }

#     RIDE_ENDED = {
#         "Safe": True
#     }

#     MOVING_WITH_OPEN_RESTRAINTS = {
#         "Safe": False
#     }

#     E_STOP = {
#         "Safe": False
#     }



def ramp_up(pwm:PWM, init_speed:float, speed:float, ):
    pass

def set_ride_speed(pwm:PWM, speed:float):
    if speed < 0:
        frame_direction.value(1)
        speed = -speed
    else:
        frame_direction.value(0)

    pwm.deinit()
    frequency = speed*FRAME_USTEPS
    pwm.init(freq=int(frequency), duty_u16=2**16//2)



#####################
##                 ##
##    Main Loop    ##
##                 ##
#####################

if __name__ == "__main__":
    lcd.clear()
    lcd.home()

    init_speed = -5
    for speed in range(101):
        if init_speed + speed/10 == 0:
            continue
        lcd.clear()
        lcd.print(f"Speed: {round(init_speed + speed/10, 2)} Hz")
        set_ride_speed(frame_motor, init_speed + speed/10)
        sleep(0.02)

    sleep(1)



