from machine import Pin, PWM
from utime import sleep



################
##   INPUTS   ##
################

## Restraint Sensor Definition (Limit Switch? Reeds Switch?)
Restraint_Sense = Pin(13, Pin.IN)

## Controller Buttons Definitions
ControllerButton_Restraints = Pin(8, Pin.IN)
ControllerButton_RideStart = Pin(9, Pin.IN)
ControllerButton_RideStop = Pin(2, Pin.IN)





##################
##   OUTPUTS   ###
##################

## Motor Definition
Motor_Step = PWM(Pin(6, Pin.OUT))
Motor_Dir = Pin(7, Pin.OUT, value=1) # set default value to be high


## LCD Definition
# you need to install this library https://github.com/gusandrioli/liquid-crystal-pico
# to the pico to use the following code, to remove any errors in VSCode / Thony then
# put the file `liquid_crystal_pico.py` in the same folder (should remove errors *fingers crossed*)

from liquid_crystal_pico import LiquidCrystalPico
rs = Pin(12, Pin.OUT)
e  = Pin(11, Pin.OUT)
d4 = Pin(5, Pin.OUT)
d5 = Pin(4, Pin.OUT)
d6 = Pin(3, Pin.OUT)
d7 = Pin(10, Pin.OUT)

lcd = LiquidCrystalPico(rs, e, d4, d5, d6, d7)

## LED Strip Definition
import neopixel # Im assuming that the plan was neo pixel strips but the old code doesn't implement anything with the LED Control
LED_Control = Pin(0, Pin.OUT)
num_leds = 72 # change this with length of led strips
LED_Strip = neopixel.NeoPixel(LED_Control, num_leds)





################
##   Flags   ###
################

cycles = 0
stopped = False
delay_time = 1





def emergency_stop(pin:Pin):
    global stopped
    print("E-Stop Loop")
    
    # NGL not entirely sure why there is a for loop
    for i in range(20):
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.write("Emergency!")
        Motor_Step.duty_u16(0)
        sleep(0.1)

    stopped = True
        

# these need to be defined after function is defined
ControllerButton_RideStop.irq(handler=emergency_stop, trigger=Pin.IRQ_RISING)
Restraint_Sense.irq(handler=emergency_stop, trigger=Pin.IRQ_RISING)



def run_ride():
    global cycles

    # this code needs to be written
    lcd.clear()
    cycles += 1


    for i in range(5):
        lcd.move_to(0, 0)
        lcd.write("Ride is running!")
        lcd.move_to(1, 0)

        sleep(1)

        if stopped:
            break

        Motor_Step.duty_u16(200) # not sure if the value mapping is 1->1 but pretending it is
        Motor_Dir.value(True)
        sleep(delay_time)

        if stopped:
            break

        Motor_Dir.value(False)
        sleep(delay_time)

        if stopped:
            break

        # Idk what the LED Wipe code it wasn't in the old code 
    
    Motor_Step.duty_u16(0)
    sleep(1)

    if stopped:
        print("Ride E-Stopped")


# This is like the setup and loop functions in arduino combined.
if __name__ == "__main__":

    # Print the welcome message
    lcd.write("Welcome")
    lcd.move_to(1, 0)
    lcd.write("Ride Operator")
    sleep(5000)


    while True:
        # Set flags
        restraints = False


        # Clear LCD
        lcd.clear()
        lcd.move_to(0, 0)


        # If the restraints button is pressed, check status of the sensor
            # Pin.value() returns 0 (False) or 1 (True), in this first example I check
            # if its equal to true but after I just use the output as its the same.
        if ControllerButton_Restraints.value() == True: 
            restraints = Restraint_Sense.value()

            # Print to console
            print(f"Restraints are {'closed' if restraints else 'open'}!")

            # Output to LCD
            lcd.clear()
            lcd.write(f"Restraints are {'closed' if restraints else 'open'}.")
            lcd.move_to(1, 0)
            lcd.write('Ready to run!' if restraints else 'Please toggle restraints!')

            sleep(1000)
        
        # If the start ride button was pressed
        if ControllerButton_RideStart.value():
            # If the restraints are *not* active
            if not restraints:
                lcd.clear()
                lcd.move_to(0, 0)
                lcd.write("Please close restraints.")
                sleep(1000)
                continue # this restarts the loop
        
            # if the E-Stop is active
            if ControllerButton_RideStop.value():
                lcd.clear()
                lcd.move_to(0, 0)
                lcd.write("E-Stop Active")
                lcd.move_to(1, 0)
                lcd.write("Toggle to Run.")
                sleep(1000)
                continue

            # To get to this point:
            # - the ride start button must be pressed
            # - the restraints must be enabled
            # - the e-stop must not be engaged

            run_ride()
            print(f"Ride Cycles {cycles}")

            
        else:
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.write("Ride is Stopped")
            lcd.move_to(1, 0)
            if ControllerButton_RideStop.value():
                lcd.write("Toggle E-Stop")
                sleep(1000)
                continue

            if restraints:
                lcd.write("Toggle Restraints")
                sleep(1000)
                continue

            
            
                

