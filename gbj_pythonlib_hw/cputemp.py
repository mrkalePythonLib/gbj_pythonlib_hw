#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Module for measuring CPU (SoC) temperature."""
__version__ = "0.1.0"
__status__ = "Development"
__author__ = "Libor Gabaj"
__copyright__ = "Copyright 2018, " + __author__
__credits__ = []
__license__ = "MIT"
__maintainer__ = __author__
__email__ = "libor.gabaj@gmail.com"


import logging


###############################################################################
# Classes
###############################################################################
class CpuTemperature(object):
    """Creating a CPU temperature manager.

    - All temperature values are expressed in float centigrades.
    - The microprocesor's temperature sensor provides temperature resolution
      in millicentigrades, which is hardly the same measurement accuracy.
    """

    def __init__(self):
        """Initialize instance object - constructor."""
        self._logger = logging.getLogger(" ".join([__name__, __version__]))
        self._logger.debug("Instance of %s created", self.__class__.__name__)
        self._temp_limit = self._read_cputemp(
            "/sys/class/thermal/thermal_zone0/trip_point_0_temp"
            )
        self._logger.debug("Temperature limit %s°C", self._temp_limit)
        self.measure()

    def __str__(self):
        """Represent instance object as a string."""
        if self._temp_current is None:
            return "No temperature available."
        else:
            return "Temperature {}°C, Limit {}°C"\
                .format(self.get_temp(), self.get_limit())

    def _read_cputemp(self, system_path):
        """Read system file and interpret the concent as the temperature.

        Positional arguments:
        ---------------------
        system_path -- full path to a file with temperature.
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

    def temp2perc(self, temperature):
        """Convert centigrades to percentage of limit."""
        try:
            perc = temperature / self._temp_limit * 100
        except TypeError:
            perc = None
        return perc

    def perc2temp(self, percentage):
        """Convert percentage of limit to centigrades."""
        try:
            temp = percentage * self._temp_limit / 100
        except TypeError:
            temp = None
        return temp

    def measure(self):
        """Measure and return current CPU temperature in centigrades."""
        self._temp_current = self._read_cputemp(
            "/sys/class/thermal/thermal_zone0/temp"
        )
        self._logger.debug("Current temperature %s°C", self._temp_current)
        return self._temp_current

    def measure_perc(self):
        """Return current CPU temperature in percentage of limit."""
        return self.temp2perc(self.measure())

    def get_limit(self):
        """Return CPU temperature limit or read it."""
        return self._temp_limit

    def get_temp(self):
        """Return CPU temperature measured recently in centigrades."""
        return self._temp_current

    def get_temp_perc(self):
        """Return CPU temperature measured recently in percentage of limit."""
        return self.temp2perc(self.get_temp())
