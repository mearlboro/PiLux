#!/usr/bin/python3

from abc import ABC
import importlib
import logging
import random
import time
from typing import Any, Callable, List, Tuple

# initialise logging to file
import lux.tools.logger

"""
Abstract class implementing the main behaviour of a segment of the LED strip
"""
class Segment(ABC):
    def __init__(self,
            segment: Tuple[int, int],
            reverse: bool,
            #effect: Callable[[Any], None]
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
        self.RANGE = list(range(*segment))
        if reverse:
            self.RANGE = reverse(self.RANGE)
        #self.effect = effect
        self.count = len(self.RANGE)

        logging.info(f"Initialisation complete for segment {segment} {'(reversed)' if reverse else ''}")
        #logging.info(f"with effect {effect.func_name}")


    def set_pixel(self, i: int, col: Tuple[int, int, int]) -> None:
        """
        Set pixel i to colour col
        """
        logging.info(f"Setting pixel {i} to colour {col}")


    def commit_pixels(self) -> None:
        """
        Set pixel i to colour col
        """
        logging.info(f"Committing range")


    def all_off(self) -> None:
        """
        Turn off all LEDs in the segment
        """
        (self.set_pixel(i, [0, 0, 0]) for i in self.segment)
        self.commit_pixels()

        logging.info('All off')

