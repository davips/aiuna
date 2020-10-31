#  Copyright (c) 2020. Davi Pereira dos Santos
#  This file is part of the aiuna project.
#  Please respect the license - more about this in the section (*) below.
#
#  aiuna is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  aiuna is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with aiuna.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is a crime and is unethical regarding the effort and
#  time spent here.
#  Relevant employers or funding agencies will be notified accordingly.


import os
import signal
from contextlib import contextmanager

import time


class withTiming:
    @staticmethod
    def cpu():
        """CPU time.

        Returns
        -------
            Sum of all SO times except wall time.
        """
        #  return time.process_time()  # Does not include children processes.
        t = os.times()
        return t[0] + t[1] + t[2] + t[3]

    @staticmethod
    def time(f):
        start = withTiming.cpu()
        ret = f()
        end = withTiming.cpu()
        return end - start, ret

    @staticmethod
    def clock():
        """Wall clock time.

        Returns
        -------
            Ellapsed time.
        """
        return time.monotonic()

    @staticmethod
    @contextmanager
    def time_limit(seconds=None):
        if seconds is None:
            yield
        else:
            def signal_handler(signum, frame):
                raise TimeoutException("Timed out!")

            signal.signal(signal.SIGALRM, signal_handler)
            signal.alarm(seconds)
            try:
                yield
            finally:
                signal.alarm(0)


class TimeoutException(Exception):
    pass
