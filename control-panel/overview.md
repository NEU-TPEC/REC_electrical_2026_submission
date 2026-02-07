

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
    | GPIOXX | Start Button |
    | GPIOXX | Start Button LED |

- Ride Stop: 

    Stops the ride

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIOXX | Stop Button |
    | GPIOXX | Stop Button LED |

- Soft Reset: 

    Resets the ride into the starting position

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIOXX | Reset Button |
    | GPIOXX | Reset Button LED |

- Operator Tag:

    RFID operator tags to verify the operator

    (this is assuming I2C for the RFID reader)
    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIOXX |  IC2 Data |
    | GPIOXX |  IC2 Clock |



#### Safety Checks:

- Operator Restraint Check: (button)

    A manual safety check for the ride restraints

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIOXX |  Restraint Button |

- Tilt Switch:

    A safety check which verifies the state of the lifting mechanism

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIOXX |  Tilt Switch Output |

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
    | GPIOXX |  Restraint LED Output |

- Loading State Check:

    LED indicating the Loading State of the ride

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIOXX |  Loading LED Output |

- LCD:

    LCD which displays more advanced ride status information

    The LCD VCC pin must be connected to 5V

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIO18 |  I2C Data |
    | GPIO19 |  I2C Clock |



#### Ride Control:

- Actuator Motor Controllers:

    The device that actually controls the state of the motors

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIOXX | Something |

- Frame Motor Controllers:

    The device that actually controls the state of the motors

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIO2 | Pulse |
    | GPIO3 | Enable |
    | GPIO4 | Direction |



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


