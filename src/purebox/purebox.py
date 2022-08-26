# Copyright (c) 2022 4ndrs <andres.degozaru@gmail.com>
# SPDX-License-Identifier: MIT
"""Utility to draw rectangles on programs using python-xlib to get the x, y,
width, height coordinates."""

import Xlib.display
from Xlib import X


class PureBox:
    """Object to draw the rectangle and store the coordinates."""

    def __init__(self, pid, /, x, y, **kwargs):
        """pid:        the pid of the application to draw on.
        x:          the starting x position.
        y:          the starting y position.

        Optional keyword arguments:
        stop_key:   the key to quit drawing, default is 'c'.
        modify_key: the key to modify the drawn rectangle, default is 'm'.
        line_color: color of the drawn lines, default is '0xFF1493'.
        line_width: width of the drawn lines, default is '3'."""
        self._display = None
        self._window = None
        self._src_window = None
        self._gc = None
        self._src_pid = pid
        self._x2, self._y2 = x, y
        self._const_x, self._const_y = x, y

        self.x, self.y = x, y
        self.width, self.height = None, None

        kwargs = {**kwargs}
        self._stop_key = ord(kwargs.get("stop_key", "c"))
        self._modify_key = ord(kwargs.get("modify", "m"))

        self._line_color = kwargs.get("line_color", 0xFF1493)
        self._line_width = kwargs.get("line_width", 3)

    def get_coordinates(self):
        """Returns the coordinates as tuple(x, y, width, height)"""
        return (self.x, self.y, self.width, self.height)

    def draw(self):
        """Starts the drawing of the rectangle."""
        self._display = Xlib.display.Display()  # use the default display

        root = self._display.screen().root
        self._src_window = self._find_window(self._src_pid, root)
        if self._src_window is None:
            raise PIDNotFoundError(
                f"Window with Process ID '{self._src_pid}' not found"
            )

        # convert to key codes with the current display
        self._stop_key = self._display.keysym_to_keycode(self._stop_key)
        self._modify_key = self._display.keysym_to_keycode(self._stop_key)

        root = self._display.screen().root
        self._src_window.geometry = self._src_window.get_geometry()
        self._window = root.create_window(
            self._src_window.geometry.x,
            self._src_window.geometry.y,
            self._src_window.geometry.width,
            self._src_window.geometry.height,
            self._src_window.geometry.border_width,
            self._src_window.geometry.depth,
            override_redirect=False,
            event_mask=X.ExposureMask
            | X.KeyPressMask
            | X.PointerMotionMask
            | X.ButtonPressMask,
        )

        self._window.set_wm_name("PureBox")
        self._window.set_wm_class("purebox", "PureBox")
        self._window.set_wm_transient_for(self._src_window)

        self._gc = self._window.create_gc(
            foreground=self._line_color,
            line_width=self._line_width,
        )

        try:
            self._window.map()

            while True:
                event = self._display.next_event()

                match event.type:
                    case X.Expose:
                        self._draw()
                    case X.KeyPress:
                        if event.detail == self._stop_key:
                            break
                        if event.detail == self._modify_key:
                            # Not implemented, does the same as stop_key
                            break
                    case X.ButtonPress:
                        break
                    case X.MotionNotify:
                        self._x2 = event.event_x
                        self._y2 = event.event_y
                        self._draw()

        finally:
            self._display.close()

    def _draw(self):
        """Updates the rectangle on the screen; ***internal use only.***
        Use the public draw() method to draw with your own instance."""
        self._window.copy_area(
            gc=self._gc,
            src_drawable=self._src_window,
            width=self._src_window.geometry.width,
            height=self._src_window.geometry.height,
            src_x=0,
            src_y=0,
            dst_x=0,
            dst_y=0,
        )

        if self.width is None or self.height is None:
            self.width, self.height = 0, 0
            self._window.rectangle(
                self._gc,
                self.x,
                self.y,
                self.width,
                self.height,
            )
            return None

        if self._x2 < self._const_x:
            self.x, self._x2 = self._x2, self._const_x
            self.x = min((self._x2, self.x))
            self.width = self._x2 - self.x
        else:
            self._x2 = max((self.x, self._x2))
            self.x = min((self.x, self._x2))
            self.width = self._x2 - self.x

        if self._y2 < self._const_y:
            self.y, self._y2 = self._y2, self._const_y
            self.y = min((self.y, self._y2))
            self.height = self._y2 - self.y
        else:
            self._y2 = max((self.y, self._y2))
            self.y = min((self.y, self._y2))
            self.height = self._y2 - self.y

        self._window.rectangle(
            self._gc,
            self.x,
            self.y,
            self.width,
            self.height,
        )
        return None

    def _find_window(self, pid, root):
        """Returns the window associated with pid using _NET_WM_PID. Returns
        None if not found."""
        net_wm_pid = self._display.intern_atom("_NET_WM_PID")
        net_client_list = self._display.intern_atom("_NET_CLIENT_LIST")

        window_ids = root.get_full_property(
            net_client_list, X.AnyPropertyType
        ).value

        for window_id in window_ids:
            window = self._display.create_resource_object("window", window_id)
            tmp_pid = window.get_full_property(
                net_wm_pid, X.AnyPropertyType
            ).value
            if not tmp_pid or tmp_pid[0] != pid:
                continue
            return window
        return None


class PIDNotFoundError(Exception):
    """Exception thrown when the PID provided was not found."""
