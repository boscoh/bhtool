#!/usr/bin/env python3

"""Print shape of numpy .npy file"""

import numpy


def npread(files: tuple[str, ...]):
    for arg in files:
        m = numpy.load(arg)
        print("Numpy shape", m.shape)
