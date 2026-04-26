# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!C:\Users\Jakesdev1991\Downloads\tokamak\igor_env\Scripts\python.exe
#
# Copyright (C) 2012 W. Trevor King <wking@tremily.us>
#
# This file is part of igor.
#
# igor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# igor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with igor.  If not, see <http://www.gnu.org/licenses/>.

"IBW -> ASCII conversion"

import pprint

import numpy

from igor.binarywave import load
from igor.script import Script


class WaveScript (Script):
    def _run(self, args):
        wave = load(args.infile)
        numpy.savetxt(
            args.outfile, wave['wave']['wData'], fmt='%g', delimiter='\t')
        self.plot_wave(args, wave)
        if args.verbose > 0:
            wave['wave'].pop('wData')
            pprint.pprint(wave)


s = WaveScript(description=__doc__)
s.run()
