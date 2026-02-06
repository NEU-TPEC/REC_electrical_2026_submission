

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
    | GPIOXX | Start Button Input |
    | GPIOXX | Start Button LED |

- Ride Stop: 

    Stops the ride

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIOXX | Stop Button Input |
    | GPIOXX | Stop Button LED |

- Soft Reset: 

    Resets the ride into the starting position

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIOXX | Reset Button Input |
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
    | GPIOXX |  Restraint Button Input |

- Tilt Switch:

    A safety check which verifies the state of the lifting mechanism

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIOXX |  Tilt Switch Input |

- ToF Sensor:




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

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIOXX |  I2C Data |
    | GPIOXX |  I2C Clock |



#### Ride Control:

- Motor Controller(s):

    The device that actually controls the state of the motors

    | PICO GPIO Pin | Purpose |
    | --- | --- |
    | GPIOXX | Something |



### Ride States

#### Safe States:

These states are recoverable

- `Ride Locked`:

    The state where the operator has not scanned their tag.

- `Restraints Open`:

    The state where the restraints are open but all other checks are valid.

- `All Clear`:

    The state where all safety checks are valid and operational.

- `Ride Started`:

    The state where the ride is starting its first loop.

- `Ride Tilted`:

    The state where the tilt sensor says the ride is lifted, the restraints must be closed, and the ride must be started.

- `Ride Ended`:

    The state of the ride when it finished one loop.


#### Unsafe States:

- `Moving with Open Restraints`:

    (Note that this is dependant on there being a non-manual restraint safety check)

    The tilt sensor indicates the ride is lifted but the restraints are not closed. -> Motors should be stopped and the riders need to safely removed, either emergency services or lowering the ride to the (un)loaded position.

- `E-Stop`:

    The E-Stop was pressed and the ride must be reset.



## Standard Operational Loop

The Ride begins in the `Locked` state. The operator scans their ID which moves the ride into `Restraints Open` state. Riders can begin to load onto the ride. Once the riders are loaded the restraints are lowered and the operator clicks the restraints check button, this moves the ride into the `All Clear` state. The operator can then press the start button which moves the ride into the `Ride Started` state. In this state the ride beings to rise which causes the tilt sensor to move into the `Ride Tilted` state. As the loop ends and the ride tilts back down the ride moves into the `Ride Ended` state where people can begin to unload, the soft reset button can then be clicked moving the ride into the `Locked` state and the loop repeats.



