#!/usr/bin/env python3
# Copyright (c) 2022 4ndrs <andres.degozaru@gmail.com>
"""Utility to draw a box on top of a window and get the box's coordinates."""
import sys

from . import PureBox, PIDNotFoundError


def main():
    """Draws a box on the specified pid and prints the coordinates to the screen.
    Needs 3 arguments when executing: pid, starting x, and y.
    Output format: x, y, w, h"""
    if len(sys.argv) < 3:
        print("Not enough inputs")
        sys.exit(1)

    pid = int(sys.argv[1])
    x = int(sys.argv[2])
    y = int(sys.argv[3])

    if len(sys.argv) > 4:
        real_width = int(sys.argv[4])
        real_height = int(sys.argv[5])
        box = PureBox(
            pid, x, y, real_width=real_width, real_height=real_height
        )
    else:
        box = PureBox(pid, x, y)

    try:
        box.draw()
    except PIDNotFoundError:
        print(f"PID {pid} not found")
        sys.exit(2)

    for i, num in enumerate(box.get_coordinates()):
        print(num, end="")
        if i < 3:
            print(", ", end="")
