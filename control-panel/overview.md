

# Overview of the REC 2026 Controls/Control Panel Code

## Battery Power

Make sure to connect the battery to the VSYS pin on the pico (PIN 39 silkscreen on front) through a pfet with the gate pin connected to vbus, this gets disconnected when the pico is plugged in through USB so that the supplies don't compete.

## Theory of Operation

### Inputs:

#### Controls:

- Dispatch: 

    Starts the ride given all the safety checks are valid

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIO12 | Start Button |
    | GPIO15 | Start Button LED |

- Ride Stop: 

    Stops the ride

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIO11 | Stop Button |
    | GPIO14 | Stop Button LED |

- Soft Reset: 

    Resets the ride into the starting position

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIO10 | Reset Button |
    | GPIO13 | Reset Button LED |

- Operator Tag:

    RFID operator tags to verify the operator

    (this is assuming I2C for the RFID reader)
    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIO6 |  SDA  |
    | GPIO7 |  SCK  |
    | GPIO8 |  MOSI |
    | GPIO9 |  MISO |



#### Safety Checks:

- Operator Restraint Check: (button)

    A manual safety check for the ride restraints

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIO19 | Restraint Button |
    | GPIO18 | Restraint button light |
 
- Tilt Switch:

    A safety check which verifies the state of the lifting mechanism

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIO22 |  Tilt Switch Output |

- ToF Sensor:

    A safety check which verifies the position of the ride frame

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIOXX |  ToF Sensor Output |




### Outputs:

#### Operator Information:

- Restraint Indicator: 

    LED indicating the status of the restraints on the ride

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIO16 |  Restraint LED Output |

- Loading State Check:

    LED indicating the Loading State of the ride

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIO17 |  Loading LED Output |

- LCD:

    LCD which displays more advanced ride status information

    The LCD VCC pin must be connected` to 5V

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIO27 |  SDA |
    | GPIO26 |  SCL |



#### Ride Control:

- Frame Motor Controller (x1):

    The device that actually controls the state of the motors

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIO0 | Pulse |
    | GPIO1 | Direction |

- Actuator Motor Controllers (x2):

    The device that actually controls the state of the motors

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIO2 | Pulse1 |
    | GPIO3 | Direction1 |
    | GPIO4 | Pulse2 |
    | GPIO5 | Direction2 |

### Full GPIO Pins ###
    | Pico Pin | Purpose     | Middle   | Purpose       | Pico Pin  | Extra             |
    | ---      |       ---   | ---      | ---           | ---       | ---               |
    | GP0      | Frame DIR   |          | VBUS          |           |                   |
    | GP1      | Frame PULSE |          |               | VSYS      |                   |
    | GND      |             |          |               | GND       |                   |
    | GP2      | Lin 1 DIR   |          |               | 3V3_EN    |                   |
    | GP3      | Lin 1 PULSE |          |               | 3V3 (OUT) |Tilt, LCD, Estop pwr|
    | GP4      | Lin 2 DIR   |          |               | ADC_VREF  |                   |
    | GP5      | Lin 2 PULSE |          | EStop Input   | GP28      |                   |
    | GND      |             |          |               | GND       | LCD GND/Estop GND |
    | GP6      | RFID SCL    |          | LCD SDA       | GP27      |                   |
    | GP7      | RFID SDA    |          | LCD SCL       | GP26      |                   |
    | GP8      | Limit 1     |          |               | RUN       |                   |
    | GP9      | Limit 2     |          | Tilt Sensor   | GP22      |                   |
    | GND      |             |          |               | GND       | Tilt GND          |
    | GP10     | Reset But   |          | Limit 3       | GP21      |                   |
    | GP11     | Stop But    |          | Limit 4       | GP20      |                   |
    | GP12     | Start But   |          | Restr. ButLED | GP19      |                   |
    | GP13     | Reset LED   |          | Restraint But | GP18      |                   |
    | GND      |             |          |               | GND       | LED GND           |
    | G14      | Stop LED    |          | Loading LED   | GP17      |                   |
    | G15      | Start LED   |          | Restraint LED | GP16      |                   |
















### Ride States

#### Safe States:

These states are recoverable

- `Ride Locked`:

    The “Ride Locked” state is the state where the restraint operator has not scanned their tag yet. The ride must also be lowered and not moving. 

- `Restraints Open`: 

    The “Restraints Open” state is the state where the restraint operator has scanned in but has not yet closed the restraints. The ride must also be lowered and not moving. 

- `All Clear`: 

    The “All Clear” state is the state where the restraints are closed; the ride is lowered and not moving, and the restraint operator has scanned in. 

- `Ride Started`: 

    The “Ride Started” state is the state after the ride operator hit the dispatch button. This state requires the restraint operator to be scanned in, the restraints to be closed, and the ride to be in the lowered position. 

- `Ride Lifting`: 

    The “Ride Lifting” state is the state which directly follows the “Ride Started” state, this is where the ride begins to lift the frame, during this state the tilt sensor should switch its state, if the tilt sensor does not switch the ride will enter a “Lift Failed” state. This state requires all the same checks as the “Ride Started” state. 

- `Ride Titled`: 

    The “Ride Tilted” state is the state which follows a successful lift. This state is a momentary state before the ride frame begins to move. This state requires all the same checks as the “Ride Started” state. 

- `Ride Spinning`: 

    The “Ride Spinning” state is the state after the “Ride Tilted” state, during this state the ride frame spins. This state requires all the same checks as the “Ride Started” state. 

- `Ride Slowing`: 

    The “Ride Slowing” state is the end of the “Ride Spinning” state. This slows the ride frame to a stop so that the ride can be lowered. This state requires that the ride frame end in the 30-degree tilted state so that the ride can be lowered. This state requires all the same checks as the “Ride Started” state. 

- `Ride Lowering`: 

    The “Ride Lowering” state is the state which directly follows the “Ride Slowing” state, this is where the ride begins to lower the frame, during this state the tilt sensor should switch its state, if the tilt sensor does not switch the ride will enter a “Lower Failed” state. This state requires all the same checks as the “Ride Started” state. 

- `Ride Ended`: 

    The “Ride Ended” state is the state which directly follows the “Ride Lowering” state. This state requires the tilt sensor to be in the tilted position. This state is where the Restraint Operator can help the riders get off the ride. 

#### Unsafe States:

- `Attempted Start with Open Restraints`: 

    This is the state of the ride where the operator attempts to dispatch the ride frame when the restraints are not engaged. 

- `Lift Failed`: 

    This is the state of the ride where the ride attempted to lift the ride frame, but the tilt sensor did not switch from the lowered to raised state. 

- `Lower Failed`: 

    This is the state of the ride where the ride attempted to lower the ride frame, but the tilt sensor did not switch from the raised to the lowered state. 

- `Moving with Open Restraints`: 

    This is the state of the ride where the ride frame is running, but the restraints are not engaged. 

- `Rotation Failed`: 

    This is the state of the ride where the ride frame rotation does not match the expected state. At the start and end of the main rotation cycle, the ride should be either 30 or 210 degrees. 

- `E-Stopped`: 

    This is the state of the ride where the E-Stop has been activated, and the ride has not yet been reset. 

- `E-Stopped manual Movement`: 

    This is the state of the ride where the E-Stop was activated but has now been disengaged. The ride can now be manually moved by moving the motors one degree at the time. 


