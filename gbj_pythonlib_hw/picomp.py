# -*- coding: utf-8 -*-
"""Module for common fuctionalities of microcomputers of the class Pi.

Notes
-----
Focused on microcomputers:

    - Orange Pi One
    - Orange Pi Zero
    - Nano Pi Neo
    - Raspberry Pi B

"""
__version__ = "0.2.0"
__status__ = "Beta"
__author__ = "Libor Gabaj"
__copyright__ = "Copyright 2018-2019, " + __author__
__credits__ = []
__license__ = "MIT"
__maintainer__ = __author__
__email__ = "libor.gabaj@gmail.com"


import logging


###############################################################################
# Classes
###############################################################################
class PiComputer(object):
    """Common Pi computers management.

    Arguments
    ---------
    temp_decimals : int
        Positive integer number of decimal places for rounding temperature
        value. If None is provided, no rounding occures.
    perc_decimals : int
        Positive integer number of decimal places for rounding percentual
        value. If None is provided, no rounding occures.

    Notes
    -----
    - All temperature values are expressed in float centigrades, i.e., degrees
      of Celsius.
    - The microprocesor's temperature sensor provides temperature resolution
      in millicentigrades, which is hardly the same measurement accuracy.

    """

    def __init__(self, temp_decimals=None, perc_decimals=None):
        """Create the class instance - constructor."""
        self._logger = logging.getLogger(" ".join([__name__, __version__]))
        self._logger.debug("Instance of %s created", self.__class__.__name__)
        try:
            self._temp_decimals = abs(int(temp_decimals))
        except TypeError:
            self._temp_decimals = None
        try:
            self._perc_decimals = abs(int(perc_decimals))
        except TypeError:
            self._perc_decimals = None
        self._temp_limit = self._read_temperature(
            "/sys/class/thermal/thermal_zone0/trip_point_0_temp"
            )
        self._logger.debug("Temperature limit %s°C", self._temp_limit)

    def __str__(self):
        """Represent instance object as a string."""
        if self._temp_current is None:
            return "No temperature available."
        else:
            return "Temperature {}°C, Limit {}°C"\
                .format(self.get_temp(), self.get_temperature_limit())

    def round_temp(self, value):
        """Round temperature value if needed and possible.

        Arguments
        ---------
        value : float
            Value to be processed.
            *The argument is mandatory and has no default value.*

        Returns
        -------
        float
            Rouded value, if number of decimal places is defined, otherwise the
            input value.

        """
        try:
            r = round(value, self._temp_decimals)
        except TypeError:
            r = value
        return r

    def round_perc(self, value):
        """Round percentage value if needed and possible.

        Arguments
        ---------
        value : float
            Value to be processed.
            *The argument is mandatory and has no default value.*

        Returns
        -------
        float
            Rouded value, if number of decimal places is defined, otherwise the
            input value.

        """
        try:
            r = round(value, self._perc_decimals)
        except TypeError:
            r = value
        return r

    def _read_temperature(self, system_path):
        """Read system file and interpret the content as the temperature.

        Arguments
        ---------
        system_path : str
            Full path to a file with system temperature.

        Returns
        -------
        temperature : float
            System temperature in centigrades Celsius.
            If some problem occurs with reading system file, the None is
            provided.

        """
        try:
            system_file = open(system_path)
            content = system_file.read()
            temperature = float(content)
            # Raspbian with temp in centigrades, other Pis in millicentigrades
            if temperature > 85.0:
                temperature /= 1000.0
            system_file.close()
        except Exception:
            temperature = None
        return temperature

    def convert_temperature_percentage(self, temperature):
        """Convert temperature to percentage of limit.

        Arguments
        ---------
        temperature : float
            System temperature in degrees of Celsius.

        Returns
        -------
        percentage : float
            System temperature expressed in percentage of temperature
            limit of the system.
            If some problem occurs with conversion, the None is provided.

        """
        try:
            perc = temperature / self.get_temperature_limit() * 100.0
        except TypeError:
            perc = None
        return self.round_perc(perc)

    def convert_percentage_temperature(self, percentage):
        """Convert percentage of limit to temperature.

        Arguments
        ---------
        percentage : float
            System temperature expressed in percentage of temperature
            limit of the system.

        Returns
        -------
        temperature : float
            System temperature in degrees of Celsius.
            If some problem occurs with conversion, the None is provided.

        """
        try:
            temp = percentage * self.get_temperature_limit() / 100.0
        except TypeError:
            temp = None
        return self.round_temp(temp)

    def measure_temperature(self):
        """Measure CPU temperature.

        Returns
        -------
        centigrades : float
            Current system temperature in degrees of Celsius.
            If some problem occurs with reading system file, the None is
            provided.

        """
        self._temp_current = self._read_temperature(
            "/sys/class/thermal/thermal_zone0/temp"
        )
        self._logger.debug("Current temperature %s°C", self._temp_current)
        return self.round_temp(self._temp_current)

# -----------------------------------------------------------------------------
# Getters
# -----------------------------------------------------------------------------
    def get_temperature_limit(self):
        """Return CPU temperature limit.

        Returns
        -------
        centigrades : float
            Current system temperature limit in degrees of Celsius.

        """
        return self.round_temp(self._temp_limit)

    def get_temperature(self):
        """Return recently measured CPU temperature.

        Returns
        -------
        centigrades : float
            Recently measured system temperature in degrees of Celsius.
            Useful for repeating calling with ensured same value.

        """
        return self.round_temp(self._temp_current)
