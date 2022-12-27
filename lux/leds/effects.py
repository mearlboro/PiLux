#!/usr/bin/python3

import importlib
import logging
import random
import time
from typing import Callable, List, Tuple

# initialise logging to file
import lux.tools.logger

# import abstract segment class
from lux.leds.segment import Segment

awb_modes = [
    "off",
    "auto",
    "sunlight",
    "cloudy",
    "shade",
    "tungsten",
    "fluorescent",
    "incandescent",
    "flash",
    "horizon",
    "greyworld"
]

effect_names = [
    "solid",
    "rainbow",
    "fft",
    "vu",
    "police",
]

def solid(segment,
		color: Tuple[int, int, int]
	) -> float:
    """
    Turn on all LEDS in the range in the headset
    """
    for i in segment.RANGE:
        segment.set_pixel(i, color)
    segment.commit_pixels()

    logging.info(f"Set effect SOLID with RGB color {color}")


def fadein_colour(segment,
        dt: float = 0.01, col: Tuple[int, int, int] = (0, 0, 0)
    ) -> None:
    """
    All leds in segment should fade in to the `col` param or, if that is
    not specified, to the `col` set in the constructor in `dt` second
    increments
    """
    logging.info(f"Fade into colour {col} for duration {dt * 256}")

    segment.all_off()
    if not (col[0] and col[1] and col[2]):
        col = segment.col
    r, g, b = col
    for j in range(100):
        for i in segment.RANGE:
            segment.set_pixel(i, (int(r * j/100), int(g * j/100), int(b * j/100)))
        segment.commit_pixels()
        if dt:
            time.sleep(dt)


def fadeout(segment, dt: float = 0.01) -> None:
    """
    All leds in segment should fade out from the current colour to black,
    going from full brightness to none in `dt` second increments
    """
    logging.info(f"Fade to black for duration {dt * 256}")

    for j in range(100):
        for i in segment.RANGE:
            r, g, b = segment.get_pixel(i)
            r = int(r * (100 - j) / 100)
            g = int(g * (100 - j) / 100)
            b = int(b * (100 - j) / 100)
            segment.set_pixel(i, (r, g, b))
        segment.commit_pixels()
        if dt:
            time.sleep(dt)


def breathe(segment,
        dt: float = 0.01, delay: float = 0, col: Tuple[int, int, int] = (0, 0, 0)
    ) -> None:
    """
    All leds in segment should fade in to colour specified in `col` param,
    or the `col` set in the constructor if that is not set, in `dt`
    second increents. Then, after `delay` seconds, fade out in `dt` second
    increments
    """
    logging.info(f"Begin breathing effect with {delay} delay")

    segment.crown_off()
    segment.crown_fadein_colour(dt, col)
    time.sleep(delay)
    segment.crown_fadeout(dt)
    time.sleep(delay)


def rainbow(segment, dt: float = 0.01) -> None:
    """
    All leds in segment cycle for `dt` seconds through the 256 possible
    colours, starting from consecutive colours
    """
    logging.info("Cycling through rainbow colours")

    for j in range(256):
        for i in segment.RANGE:
            col = (0, 0, 0)
            pos = ((i * 256 // segment.COUNT) + j) % 256
            if pos < 85:
                col = (pos * 3, 255 - pos * 3, 0)
            elif pos < 170:
                pos -= 85
                col = (255 - pos * 3, 0, pos * 3)
            else:
                pos -= 170
                col = (0, pos * 3, 255 - pos * 3)
            segment.set_pixel(i, col)
        segment.commit_pixels()
        time.sleep(dt)


def rainbow_repeat(segment,
        dt: float = 0.01, duration: float = 2
    ) -> None:
    """
    All leds in segment cycle for `dt` seconds through the 256 possible
    colours for a total time of `duration` seconds
    """
    logging.info("Begin rainbow cycle effect")

    n = int(duration / dt)

    for _ in range(n):
        rainbow()

