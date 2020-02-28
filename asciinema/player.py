import os
import sys
import time

import asciinema.asciicast.events as ev
from asciinema.term import raw, read_blocking


class Player:

    def play(self, asciicast, idle_time_limit=None, speed=1.0):
        try:
            stdin = open('/dev/tty')
            with raw(stdin.fileno()):
                self._play(asciicast, idle_time_limit, speed, stdin)
        except Exception:
            self._play(asciicast, idle_time_limit, speed, None)

    def _play(self, asciicast, idle_time_limit, speed, stdin):
        idle_time_limit = idle_time_limit or asciicast.idle_time_limit

        stdout = asciicast.events()
        stdout = ev.to_relative_time(stdout)
        stdout = ev.cap_relative_time(stdout, idle_time_limit)
        stdout = ev.to_absolute_time(stdout)
        stdout = ev.adjust_speed(stdout, speed)

        base_time = time.time()
        ctrl_c = False
        paused = False
        pause_time = None

        for t, _type, text in stdout:
            delay = t - (time.time() - base_time)
            if _type == "i":
                while True:
                    # Wait for a keystroke from the user. FOREVER. Well, for a year.
                    data = read_blocking(stdin.fileno(), 365 * 24 * 60 * 60)
                    if 0x03 in data:  # ctrl-c
                        ctrl_c = True
                    elif "\r" in text and b"\r" not in data:
                        # If there's a newline in the file but none in the keyboard, wait for one.
                        continue
                    # Reset the delay so the character is printed right away.
                    base_time = time.time() - t
                    break  # Don't wait for any more characters.
                continue  # Don't print this character.

            while stdin and not ctrl_c and delay > 0:
                data = read_blocking(stdin.fileno(), delay)

                if 0x03 in data:  # ctrl-c
                    ctrl_c = True

                break

            if ctrl_c:
                break

            sys.stdout.write(text)
            sys.stdout.flush()
