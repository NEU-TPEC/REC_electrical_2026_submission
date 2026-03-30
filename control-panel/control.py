from machine import Pin, I2C, PWM
import utime
from utime import sleep, ticks_ms
from DIYables_MicroPython_LCD_I2C import LCD_I2C
from mfrc522 import MFRC522

# LCD Setup

lcd_comm = I2C(
    1,              
    scl=Pin(27),     
    sda=Pin(26),     
    )

LCD_ADDR = 0x27
LCD_ROWS = 2
LCD_COLS = 16
lcd = LCD_I2C(lcd_comm, LCD_ADDR, LCD_ROWS, LCD_COLS)



######################
##                  ##
##    INPUT Pins    ##
##                  ##
######################

## Control Buttons

dispatch_button = Pin(12, Pin.IN, Pin.PULL_UP)  
ride_stop_button = Pin(11, Pin.IN, Pin.PULL_UP) 
soft_reset_button = Pin(10, Pin.IN, Pin.PULL_UP) 
estop_button = Pin(28, Pin.IN, Pin.PULL_UP)


# Safety Checks

operator_restraint_button = Pin(19, Pin.IN, Pin.PULL_UP) 
rfid_sda = machine.Pin(16)
rfid_scl = machine.Pin(17)
rfid_i2c = machine.I2C(0, sda=rifd_sda, scl=rfid_scl, freq=400000)
RESTRAINTS_ENGAGED_BUTTON = False
RFID_SCANNED = False
RESTRAINTS_DOUBLE_ENGAGED = False 

def toggle_restraints():
    RESTRAINTS_ENGAGED_BUTTON = not RESTRAINTS_ENGAGED_BUTTON
    start_time = utime.ticks_ms()
    timeout_ms = timeout_sec * 1000
    card_found = False




    if RFID_SCANNED and RESTRAINTS_ENGAGED_BUTTON:
        RESTRAINTS_DOUBLE_ENGAGED = True
    restraint_indicator.value(RESTRAINTS_DOUBLE_ENGAGED)
operator_restraint_button.irq(trigger=Pin.IRQ_FALLING, handler=toggle_restraints)


tilt_sensor = Pin(22, Pin.IN)                

#######################
##                   ##
##    Output Pins    ##
##                   ##
#######################

dispatch_button_led = Pin(15, Pin.OUT)
stop_button_led = Pin(14, Pin.OUT)
reset_button_led = Pin(13, Pin.OUT)
operator_restraint_led = Pin(18, Pin.OUT)
restraint_indicator = Pin(16, Pin.OUT)
loading_state_indicator = Pin(17, Pin.OUT)


#########################
##                     ##
##    Motor Control    ##
##                     ##
#########################


# Frame Motor
frame_pulse = Pin(0, Pin.OUT, value=0)
frame_direction = Pin(1, Pin.OUT, value=0)
frame_motor = PWM(frame_pulse)
FRAME_USTEPS = 6400

# Actuator Motor 1
act_pulse_1 = Pin(2, Pin.OUT, value=0)
act_direction_1 = Pin(3, Pin.OUT, value=0)
act_motor_1 = PWM(act_pulse_1)
ACT_USTEPS_1 = 6400

# Actuator Motor 2
act_pulse_2 = Pin(4, Pin.OUT, value=0)
act_direction_2 = Pin(5, Pin.OUT, value=0)
act_motor_2 = PWM(act_pulse_2)
ACT_USTEPS_2 = 6400

## Limit Switches
limit1 = Pin(8, Pin.IN)
limit2 = Pin(9, Pin.IN)
limit3 = Pin(21, Pin.IN)
limit4 = Pin(20, Pin.IN)


#######################
##                   ##
##    Ride States    ##
##                   ##
#######################


RIDE_LOCKED = 0
RESTRAINTS_OPEN = 1
ALL_CLEAR = 2
RIDE_STARTED = 3
RIDE_LIFTING = 4
RIDE_TILTED = 5
RIDE_SPINNING = 6
RIDE_SLOWING = 7
RIDE_LOWERING = 8
RIDE_ENDED = 9

E_STOP = 100
LIFT_FAILED = 101
LOWER_FAILED = 102
ROT_FAILED = 103
MOVING_WITH_OPEN_RESTRAINTS = 104
ATTEMPTED_START_WITH_OPEN = 105
E_STOP_MANUAL_MOVEMENT = 106

def set_ride_speed(pwm:PWM, speed:float):
    '''
    Sets the speed of the given PWM object using the globally defined microsteps

    Parameters
    ----------
    pwm : PWM
        The motor to control
    speed : float
        The speed in Hz.
    '''
    if speed < 0:
        frame_direction.value(1)
    else:
        frame_direction.value(0)

    pwm.deinit()
    frequency = speed*FRAME_USTEPS
    if abs(frequency) >= 10:
        pwm.init(freq=int(abs(frequency)), duty_u16=2**16//2)



def restraints_closed() -> bool: 
    """Checks if the operator restraints are closed."""
    return RESTRAINTS_ENGAGED_BUTTON

def ride_lowered() -> bool:
    """Checks if the ride is in the lowered position."""
    return (limit1.value() == 0 and limit2.value() == 0)

def ride_raised() -> bool:
    """Checks if the ride is in the raised position."""
    return (limit1.value() == 1 and limit2.value() == 1)

def e_stop_pressed() -> bool:
    """Checks if the emergency stop button is pressed."""
    return estop_button.value() == 1

def dispatch_pressed() -> bool:
    """Checks if the dispatch button is pressed."""
    return dispatch_button.value() == 1

def rotation_limit1() -> bool:
    """Checks if the first rotation limit switch is triggered."""
    return limit3.value() == 1

def rotation_limit2() -> bool:
    """Checks if the second rotation limit switch is triggered."""
    return limit4.value() == 1

def check_safety(state) -> int:
    """Checks the safety conditions and returns the current state"""
    if e_stop_pressed():
        return E_STOP

    if not restraints_closed() and state in [
        RIDE_STARTED, RIDE_LIFTING, RIDE_TILTED,
        RIDE_SPINNING, RIDE_SLOWING, RIDE_LOWERING
    ]:
        return MOVING_WITH_OPEN_RESTRAINTS

    return state


# Emergency stop
state = RIDE_LOCKED

ESTOP_PUSHED = False
def emergency_stop():
    ESTOP_PUSHED = True
    state = E_STOP
estop_button.irq(trigger=Pin.IRQ_FALLING, handler=emergency_stop)



freq = [(0, 0.00), (1, 0.0012), (2, 0.0049), (3, 0.012), (4, 0.020), (5, 0.031), (6, 0.047), (7, 0.062), (8, 0.078), 
        (9, 0.094), (10, 0.12), (11, 0.16), (12, 0.16), (13, 0.19), (14, 0.22), (15, 0.22), (16, 0.22), (17, 0.25), 
        (18, 0.25), (19, 0.25), (20, 0.25), (21, 0.25), (22, 0.25), (23, 0.25), (24, 0.22), (25, 0.22), (26, 0.22), 
        (27, 0.19), (28, 0.16), (29, 0.16), (30, 0.12), (31, 0.094), (32, 0.078), (33, 0.062), (34, 0.047), (35, 0.031), 
        (36, 0.020), (37, 0.012), (38, 0.0049), (39, 0.0012), (40, 0.00), (41, -0.0012), (42, -0.0049), (43, -0.012), 
        (44, -0.020), (45, -0.031), (46, -0.047), (47, -0.062), (48, -0.078), (49, -0.094), (50, -0.12), (51, -0.16), 
        (52, -0.19), (53, -0.22), (54, -0.25), (55, -0.25), (56, -0.31), (57, -0.38), (58, -0.38), (59, -0.44), 
        (60, -0.50), (61, -0.50), (62, -0.62), (63, -0.62), (64, -0.62), (65, -0.75), (66, -0.75), (67, -0.75), (68, -0.88), 
        (69, -0.88), (70, -0.88), (71, -0.88), (72, -0.88), (73, -1.0), (74, -1.0), (75, -1.0), (76, -1.0), (77, -1.0), 
        (78, -1.0), (79, -1.0), (80, -1.0), (81, -1.0), (82, -1.0), (83, -1.0), (84, -1.0), (85, -1.0), (86, -1.0), 
        (87, -1.0), (88, -0.88), (89, -0.88), (90, -0.88), (91, -0.88), (92, -0.88), (93, -0.75), (94, -0.75), 
        (95, -0.75), (96, -0.62), (97, -0.62), (98, -0.62), (99, -0.50), (100, -0.50), (101, -0.44), (102, -0.38), 
        (103, -0.38), (104, -0.31), (105, -0.25), (106, -0.25), (107, -0.22), (108, -0.19), (109, -0.16), (110, -0.12), 
        (111, -0.094), (112, -0.078), (113, -0.062), (114, -0.047), (115, -0.031), (116, -0.020), (117, -0.012), 
        (118, -0.0049), (119, -0.0012), (120, 0.00), (121, 0.0012), (122, 0.0049), (123, 0.012), (124, 0.020), 
        (125, 0.031), (126, 0.047), (127, 0.062), (128, 0.078), (129, 0.094), (130, 0.12), (131, 0.16), (132, 0.19), 
        (133, 0.22), (134, 0.25), (135, 0.25), (136, 0.31), (137, 0.38), (138, 0.38), (139, 0.44), (140, 0.50), 
        (141, 0.50), (142, 0.62), (143, 0.62), (144, 0.62), (145, 0.75), (146, 0.75), (147, 0.75), (148, 0.88), 
        (149, 0.88), (150, 0.88), (151, 0.88), (152, 0.88), (153, 1.0), (154, 1.0), (155, 1.0), (156, 1.0), (157, 1.0), 
        (158, 1.0), (159, 1.0), (160, 1.0), (161, 1.0), (162, 1.0), (163, 1.0), (164, 1.0), (165, 1.0), (166, 1.0), 
        (167, 1.0), (168, 0.88), (169, 0.88), (170, 0.88), (171, 0.88), (172, 0.88), (173, 0.75), (174, 0.75), (175, 0.75), 
        (176, 0.62), (177, 0.62), (178, 0.62), (179, 0.50), (180, 0.50), (181, 0.44), (182, 0.38), (183, 0.38), (184, 0.31), 
        (185, 0.25), (186, 0.25), (187, 0.22), (188, 0.19), (189, 0.16), (190, 0.12), (191, 0.094), (192, 0.078), (193, 0.062), 
        (194, 0.047), (195, 0.031), (196, 0.020), (197, 0.012), (198, 0.0049), (199, 0.0012), (200, 0.00), (201, -0.0012), 
        (202, -0.0049), (203, -0.012), (204, -0.020), (205, -0.031), (206, -0.047), (207, -0.062), (208, -0.078), (209, -0.094), 
        (210, -0.12), (211, -0.16), (212, -0.19), (213, -0.22), (214, -0.25), (215, -0.25), (216, -0.31), (217, -0.38), 
        (218, -0.38), (219, -0.44), (220, -0.50), (221, -0.50), (222, -0.62), (223, -0.62), (224, -0.62), (225, -0.75), 
        (226, -0.75), (227, -0.75), (228, -0.88), (229, -0.88), (230, -0.88), (231, -0.88), (232, -0.88), (233, -1.0), 
        (234, -1.0), (235, -1.0), (236, -1.0), (237, -1.0), (238, -1.0), (239, -1.0), (240, -1.0), (241, -1.0), (242, -1.0), 
        (243, -1.0), (244, -1.0), (245, -1.0), (246, -1.0), (247, -1.0), (248, -0.88), (249, -0.88), (250, -0.88), 
        (251, -0.88), (252, -0.88), (253, -0.75), (254, -0.75), (255, -0.75), (256, -0.62), (257, -0.62), (258, -0.62), 
        (259, -0.50), (260, -0.50), (261, -0.44), (262, -0.38), (263, -0.38), (264, -0.31), (265, -0.25), (266, -0.25), 
        (267, -0.22), (268, -0.19), (269, -0.16), (270, -0.12), (271, -0.094), (272, -0.078), (273, -0.062), (274, -0.047), 
        (275, -0.031), (276, -0.020), (277, -0.012), (278, -0.0049), (279, -0.0012), (280, 0.00), (281, 0.0012), (282, 0.0049), 
        (283, 0.012), (284, 0.020), (285, 0.031), (286, 0.047), (287, 0.062), (288, 0.078), (289, 0.094), (290, 0.12), 
        (291, 0.16), (292, 0.19), (293, 0.22), (294, 0.25), (295, 0.25), (296, 0.31), (297, 0.38), (298, 0.38), (299, 0.44), 
        (300, 0.50), (301, 0.50), (302, 0.62), (303, 0.62), (304, 0.62), (305, 0.75), (306, 0.75), (307, 0.75), (308, 0.88), 
        (309, 0.88), (310, 0.88), (311, 0.88), (312, 0.88), (313, 1.0), (314, 1.0), (315, 1.0), (316, 1.0), (317, 1.0), 
        (318, 1.0), (319, 1.0), (320, 1.0), (321, 1.0), (322, 1.0), (323, 1.0), (324, 1.0), (325, 1.0), (326, 1.0), (327, 1.0), 
        (328, 0.88), (329, 0.88), (330, 0.88), (331, 0.88), (332, 0.88), (333, 0.75), (334, 0.75), (335, 0.75), (336, 0.62), 
        (337, 0.62), (338, 0.62), (339, 0.50), (340, 0.50), (341, 0.44), (342, 0.38), (343, 0.38), (344, 0.31), (345, 0.25), 
        (346, 0.25), (347, 0.22), (348, 0.19), (349, 0.16), (350, 0.12), (351, 0.094), (352, 0.078), (353, 0.062), (354, 0.047), 
        (355, 0.031), (356, 0.020), (357, 0.012), (358, 0.0049), (359, 0.0012), (360, 0.00), (361, -0.0012), (362, -0.0049), 
        (363, -0.012), (364, -0.020), (365, -0.031), (366, -0.047), (367, -0.062), (368, -0.078), (369, -0.094), (370, -0.12), 
        (371, -0.16), (372, -0.19), (373, -0.22), (374, -0.25), (375, -0.25), (376, -0.31), (377, -0.38), (378, -0.38), 
        (379, -0.44), (380, -0.50), (381, -0.50), (382, -0.62), (383, -0.62), (384, -0.62), (385, -0.75), (386, -0.75), 
        (387, -0.75), (388, -0.88), (389, -0.88), (390, -0.88), (391, -0.88), (392, -0.88), (393, -1.0), (394, -1.0), 
        (395, -1.0), (396, -1.0), (397, -1.0), (398, -1.0), (399, -1.0), (400, -1.0), (401, -1.0), (402, -1.0), (403, -1.0), 
        (404, -1.0), (405, -1.0), (406, -1.0), (407, -1.0), (408, -0.88), (409, -0.88), (410, -0.88), (411, -0.88), (412, -0.88), (413, -0.75), (414, -0.75), (415, -0.75), (416, -0.62), (417, -0.62), (418, -0.62), (419, -0.50), (420, -0.50), (421, -0.44), (422, -0.38), (423, -0.38), (424, -0.31), (425, -0.25), (426, -0.25), (427, -0.22), (428, -0.19), (429, -0.16), (430, -0.12), (431, -0.094), (432, -0.078), (433, -0.062), (434, -0.047), (435, -0.031), (436, -0.020), (437, -0.012), (438, -0.0049), (439, -0.0012), (440, 0.00), (441, 0.0012), (442, 0.0049), (443, 0.012), (444, 0.020), (445, 0.031), (446, 0.047), (447, 0.062), (448, 0.078), (449, 0.094), (450, 0.12), (451, 0.16), (452, 0.19), (453, 0.22), (454, 0.25), (455, 0.25), (456, 0.31), (457, 0.38), (458, 0.38), (459, 0.44), (460, 0.50), (461, 0.50), (462, 0.62), (463, 0.62), (464, 0.62), (465, 0.75), (466, 0.75), (467, 0.75), (468, 0.88), (469, 0.88), (470, 0.88), (471, 0.88), (472, 0.88), (473, 1.0), (474, 1.0), (475, 1.0), (476, 1.0), (477, 1.0), (478, 1.0), (479, 1.0), (480, 1.0), (481, 1.0), (482, 1.0), (483, 1.0), (484, 1.0), (485, 1.0), (486, 1.0), (487, 1.0), (488, 0.88), (489, 0.88), (490, 0.88), (491, 0.88), (492, 0.88), (493, 0.75), (494, 0.75), (495, 0.75), (496, 0.62), (497, 0.62), (498, 0.62), (499, 0.50), (500, 0.50), (501, 0.44), (502, 0.38), (503, 0.38), (504, 0.31), (505, 0.25), (506, 0.25), (507, 0.22), (508, 0.19), (509, 0.16), (510, 0.12), (511, 0.094), (512, 0.078), (513, 0.062), (514, 0.047), (515, 0.031), (516, 0.020), (517, 0.012), (518, 0.0049), (519, 0.0012), (520, 0.00), (521, -0.0012), (522, -0.0049), (523, -0.012), (524, -0.020), (525, -0.031), (526, -0.047), (527, -0.062), (528, -0.078), (529, -0.094), (530, -0.12), (531, -0.16), (532, -0.16), (533, -0.19), (534, -0.22), (535, -0.22), (536, -0.22), (537, -0.25), (538, -0.25), (539, -0.25), (540, -0.25), (541, -0.25), (542, -0.25), (543, -0.25), (544, -0.22), (545, -0.22), (546, -0.22), (547, -0.19), (548, -0.16), (549, -0.16), (550, -0.12), (551, -0.094), (552, -0.078), (553, -0.062), (554, -0.047), (555, -0.031), (556, -0.020), (557, -0.012), (558, -0.0049), (559, -0.0012)]


#####################
##                 ##
##    Main Loop    ##
##                 ##
#####################

if __name__ == "__main__":
    lift_start = 0
    lower_start = 0
    spin_index = 0
    lcd.clear()
    print(lcd_comm.scan())

    state = RIDE_LOCKED
    RESTRAINTS_ENGAGED_BUTTON = operator_restraint_button.value()
    ESTOP_PUSHED = estop_button.value()
    RFID_SCANNED = False
   
    while True:
        state = check_safety(state)

        lcd.home()
        lcd.print(f"State: {state:3}")

        ## State Regulator
        if state == RIDE_LOCKED:
            lcd.print(f"Ride locked.")
            set_ride_speed(frame_motor, 0)
            if operator_restraint_button.value():
                state = RESTRAINTS_OPEN

        elif state == RESTRAINTS_OPEN:
            lcd.print(f"Restraints open.")
            if restraints_closed():
                state = ALL_CLEAR

        elif state == ALL_CLEAR:
            lcd.print(f"All clear!")
            if dispatch_pressed():
                state = RIDE_STARTED

        elif state == RIDE_STARTED:
            lcd.print(f"Starting ride...")
            if not restraints_closed():
                state = ATTEMPTED_START_WITH_OPEN
                lcd.print(f"Restraints open! Cannot begin ride.")
            else:
                lift_start = ticks_ms()
                state = RIDE_LIFTING

        elif state == RIDE_LIFTING:
            # set_ride_speed(frame_motor, 0.25) update with correct motors, should be actuators
            lcd.print(f"Ride lifting.")
            if not restraints_closed():
                state = MOVING_WITH_OPEN_RESTRAINTS
            elif ride_raised():
                spin_index = 0
                state = RIDE_SPINNING
            # if lift took more than 3 seconds
            elif ticks_ms() - lift_start > 3000:
                state = LIFT_FAILED

        elif state == RIDE_SPINNING: #Use rotation_limit functions
            lcd.print(f"Ride running.")
            set_ride_speed(frame_motor, freq[spin_index][1])
            if not restraints_closed():
                state = MOVING_WITH_OPEN_RESTRAINTS
                
            elif rotation_limit1() or rotation_limit2():
                state = RIDE_SLOWING
            else:
                spin_index = (spin_index + 1) % len(freq)
            sleep(1/10)

    # for t, f in freq:
    #     set_ride_speed(frame_motor, f)
    #     sleep(1/10)