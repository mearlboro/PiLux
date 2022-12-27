#!/usr/bin/python3

from abc import ABC
import importlib
import logging
import random
import time
from typing import Any, Callable, List, Tuple

# hardware controllers
import Adafruit_WS2801 as LED
import Adafruit_GPIO.SPI as SPI
import RPi.GPIO as GPIO

# initialise logging to file
import lux.tools.logger

"""
Class implementing the behaviour of a segment of the LED strip on an actual
RaspberryPi using the WS2801 leds
"""
class WS2801Segment(Segment):
    def __init__(self,
            segment: Tuple[int, int],
            reverse: bool,
            effect: Callable[List[int]]
        ) -> None:
        """
        Initialise abstract class (also useful for mocking the segment on a dev
        environment)

        Params
        ------
        segment
            smallest and largest index of LEDs (largest not included) in the
            segment
        reverse
            True if the effect should be applied in reverse order
        effect
            function that takes a range of LEDs and applies an effect to them
        """
        super().__init__(segment, reverse, effect)

        self.pixels = LED.WS2801Pixels(segment[1], spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)
        logging.info('Initialisation of WS2801 LEDs complete')


    def set_pixel(self, i: int, col: Tuple[int, int, int]) -> None:
        """
        Set pixel i to colour col
        """
        self.pixels.set_pixel(i, LED.RGB_to_color(col))
        super().set_pixel()


    def commit_pixels(self) -> None:
        """
        Commit pixels that have been set since the last commit, causing the
        LEDs to actually change colour
        """
        self.pixels.show()
        super().commit_pixels()


    def all_off(self) -> None:
        """
        Turn off all LEDs in the segment
        """
        super().all_off()


