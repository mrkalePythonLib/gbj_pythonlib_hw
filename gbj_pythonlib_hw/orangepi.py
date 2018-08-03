#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Module for controlling GPIOs of Orange Pi microcomputers.

- The library orangepi_PC_gpio_pyH3 should be installed:
  https://github.com/duxingkei33/orangepi_PC_gpio_pyH3
- For controlling in-built LEDs their control at the operating system level
  should be set to None.
"""
__version__ = "0.3.0"
__status__ = "Development"
__author__ = "Libor Gabaj"
__copyright__ = "Copyright 2018, " + __author__
__credits__ = ["https://github.com/duxingkei33"]
__license__ = "MIT"
__maintainer__ = __author__
__email__ = "libor.gabaj@gmail.com"


import logging
from pyA20.gpio import gpio
from pyA20.gpio import port
from pyA20.gpio import connector


###############################################################################
# Module constants
###############################################################################
INPUT = gpio.INPUT
OUTPUT = gpio.OUTPUT
HIGH = gpio.HIGH
LOW = gpio.LOW


###############################################################################
# SoC parameters
###############################################################################
PERC_MAXTEMP_ON = 85.0  # Fan ON default percentage of maximal temperature
PERC_MAXTEMP_OFF = 75.0  # Fan OFF default percentage of maximal temperature


###############################################################################
# Classes
###############################################################################
class OrangePiOne(object):
    """Creating a GPIO manager for microcomputer Orange Pi One."""

    def __init__(self, pins=[{}], leds=[{}]):
        """Initialize instance object - constructor.

        Positional arguments:
        ---------------------
        pins -- list of pins dictionaries to be registered
                [{pin: mode}], e.g.,
                [{"PA13": gbj_orangepi.OUTPUT}, {"PA13": gbj_orangepi.INPUT}]
        leds -- list of LEDs to be registered
                [led, led], e.g., ["STATUS_LED", "POWER_LED"]
        """
        self._logger = logging.getLogger(" ".join([__name__, __version__]))
        self._logger.debug("Instance of %s created", self.__class__.__name__)
        gpio.init()
        self._pins = []
        self._leds = []
        # Register pins
        if not isinstance(pins, list):
            pins = list(pins)
        for pin_def in pins:
            for pin, mode in pin_def.iteritems():
                self.pin_register(pin, mode)
        # Register LEDs
        if not isinstance(leds, list):
            leds = list(leds)
        for led_def in leds:
            for led in led_def:
                self.led_register(led)

    def __str__(self):
        """Represent instance object as a string."""
        return "Pins {}".format(len(self._pins))

    def _pin_process(self, pin, value=gpio.HIGH, mode=gpio.OUTPUT):
        """Set output pin to logical 0 or 1.

        Positional arguments:
        ---------------------
        pin -- registered pin identifier
        value -- logical value [gpio.HIGH, gpio.LOW]
        mode -- mode of a pin [gpio.OUTPUT, gpio.INPUT]

        Returns:
        --------
        Read pin value (binary state) - if pin has input mode
        Exception NameError - if pin is not registered
        Exception TypeError - if pin is not of output mode

        """
        present = False
        for i, pin_record in enumerate(self._pins):
            if pin_record["name"] == pin:
                if pin_record["mode"] == mode:
                    if mode == gpio.OUTPUT:
                        gpio.setcfg(pin_record["port"], gpio.OUTPUT)
                        gpio.output(pin_record["port"], value)
                        self._pins[i]["state"] = value
                    elif mode == gpio.INPUT:
                        gpio.setcfg(pin_record["port"], gpio.INPUT)
                        value = gpio.input(pin_record["port"])
                        self._pins[i]["state"] = value
                        return value
                else:
                    errmsg = "Oposite mode of pin {}".format(pin)
                    self._logger.error(errmsg)
                    raise TypeError(errmsg)
                present = True
                break
        if not present:
            errmsg = "Non-registered pin {}".format(pin)
            self._logger.error(errmsg)
            raise NameError(errmsg)

    def pin_register(self, pin, mode=OUTPUT):
        """Register pin and its mode.

        Positional arguments:
        ---------------------
        pin -- pyA20 port or connector identifier for a pin
        mode -- I/O mode of the pin [OUTPUT, INPUT]

        Returns:
        --------
        Exception NameError - if pin is unknown
        Exception TypeError - if pin is of unknown mode

        """
        # Determine type and check pin
        self._logger.debug("Registering pin %s with mode %s", pin, mode)
        if pin in dir(port):
            port_num = getattr(port, pin)
        elif pin in dir(connector):
            port_num = getattr(connector, pin)
        else:
            errmsg = "Unknown pin {}".format(pin)
            self._logger.error(errmsg)
            raise NameError(errmsg)
        # Check pin mode
        if mode is not None and mode not in [OUTPUT, INPUT]:
            errmsg = "Unknown mode {} of pin {}".format(mode, pin)
            self._logger.error(errmsg)
            raise TypeError(errmsg)

        # Find existing pin, remove or update it
        new = True
        for i, pin_record in enumerate(self._pins):
            if pin_record["name"] == pin:
                if mode is None:
                    self._pins.pop(i)
                    self._logger.debug("Removed pin %s", pin)
                else:
                    pin_record["mode"] = mode
                    self._logger.debug("Updated pin %s", pin)
                new = False
                break
        # Create new pin
        if new:
            pin_record = {
                "name": pin,
                "port": port_num,
                "mode": mode,
                "state": gpio.LOW,
            }
            self._pins.append(pin_record)
            self._logger.debug("Registered pin %s", pin)

    def pin_set(self, pin, value=gpio.HIGH):
        """Set output pin to logical value."""
        self._pin_process(pin, value, mode=gpio.OUTPUT)

    def pin_on(self, pin):
        """Set output pin to logical 1."""
        self.pin_set(pin, value=gpio.HIGH)

    def pin_off(self, pin):
        """Set output pin to logical 0."""
        self.pin_set(pin, value=gpio.LOW)

    def pin_read(self, pin, mode=gpio.INPUT):
        """Read input pin."""
        return self._pin_process(pin, mode=gpio.INPUT)

    def pin_state(self, pin):
        """Return recent pin state."""
        pin_record = filter(lambda pin_def: pin_def["name"] == pin, self._pins)
        if pin_record is None:
            return None
        else:
            return pin_record[0]["state"]

    def _led_process(self, led, value=gpio.HIGH):
        """Turn signalling LED on or off.

        Positional arguments:
        ---------------------
        led -- registered LED identifier
        value -- logical value [gpio.HIGH, gpio.LOW]

        Returns:
        --------
        Exception NameError - if LED is not registered

        """
        present = False
        for i, led_record in enumerate(self._leds):
            if led_record["name"] == led:
                gpio.setcfg(led_record["port"], gpio.OUTPUT)
                gpio.output(led_record["port"], value)
                self._leds[i]["state"] = value
                present = True
                break
        if not present:
            errmsg = "Non-registered LED {}".format(led)
            self._logger.error(errmsg)
            raise NameError(errmsg)

    def led_register(self, led):
        """Register LED.

        Positional arguments:
        ---------------------
        led -- pyA20 port or connector identifier for an LED

        Returns:
        --------
        Exception NameError - if LED is unknown

        """
        # Check LED
        self._logger.debug("Registering LED %s", led)
        if led in dir(port) and led in ["STATUS_LED", "POWER_LED"]:
            port_num = getattr(port, led)
        elif led in dir(connector) and led in ["LEDp1", "LEDp2"]:
            port_num = getattr(connector, led)
        else:
            errmsg = "Unknown LED {}".format(led)
            self._logger.error(errmsg)
            raise NameError(errmsg)

        # Update existing LED
        new = True
        for led_record in self._leds:
            if led_record["name"] == led:
                self._logger.debug("Updated LED %s", led)
                new = False
                break
        # Create new LED
        if new:
            led_record = {
                "name": led,
                "port": port_num,
                "state": None,
            }
            self._leds.append(led_record)
            self._logger.debug("Created LED %s", led)

    def led_remove(self, led):
        """Remove LED for the registering list.

        Positional arguments:
        ---------------------
        led -- pyA20 port or connector identifier for an LED

        Returns:
        --------
        Exception NameError - if LED is unknown

        """
        # Check LED
        self._logger.debug("Removing LED %s", led)
        if led in dir(port) and led in ["STATUS_LED", "POWER_LED"]:
            pass
        elif led in dir(connector) and led in ["LEDp1", "LEDp2"]:
            pass
        else:
            return
        # Remove existing LED
        for i, led_record in enumerate(self._leds):
            if led_record["name"] == led:
                self._pins.pop(i)
                self._logger.debug("Updated LED %s", led)
                return

    def led_set(self, led, value=gpio.HIGH):
        """Turn LED on or off."""
        self._led_process(led, value)

    def led_on(self, led):
        """Turn LED on."""
        self.led_set(led, value=gpio.HIGH)

    def led_off(self, led):
        """Turn LED off."""
        self.led_set(led, value=gpio.LOW)

    def led_state(self, led):
        """Return recent known LED state."""
        led_record = filter(lambda led_def: led_def["name"] == led, self._leds)
        if led_record is None:
            return None
        else:
            return led_record[0]["state"]
