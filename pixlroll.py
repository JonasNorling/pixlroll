#!/usr/bin/python
#
# Copyright 2014, Jonas Norling <jonas.norling@gmail.com>
#
# This software program is licensed under the GNU General Public License v2.
#

from __future__ import division
import optparse
from gtkgui import Gui
from histogram import Histogram
import gtk
import struct
import colorsys

description=\
"Pixlroll draws a scrolling intensity plot of one-dimensional realtime data"

blocksize = 0
plotter = None
histogram = None
typesize = 1
typestring = None

def readable(fd, condition):
    """Data is available in the FIFO"""
    data = fd.read(blocksize)
    count = len(data) / typesize
    values = struct.unpack(typestring % count, data)
    plotter.addData(values)
    if histogram:
        histogram.addData(values)
    return True

def makeColormap(datarange, colormap):
    c = {}
    if colormap == "rssi":
        for v in range(datarange[0], datarange[1] + 1):
            n = (v - datarange[0]) / (datarange[1] - datarange[0]) # n: 0..1
            if v >= -100 and v < -20:
                s = 1.0
            else:
                s = 0.0
            c[v] = colorsys.hsv_to_rgb(n - 0.1, s, n * 3)
    elif colormap == "rainbow":
        for v in range(datarange[0], datarange[1] + 1):
            n = (v - datarange[0]) / (datarange[1] - datarange[0]) # n: 0..1
            c[v] = colorsys.hsv_to_rgb(n, 1.0, 0.5)
    return c

if __name__ == '__main__':
    # Parse command line
    parser = optparse.OptionParser(usage="Usage: %prog <FIFO or device>",
                                   description=description)
    parser.add_option("--width", dest="width", default="1000", type="int",
                      help="Plot width [pixels]", metavar="N")
    parser.add_option("--height", dest="height", default="600", type="int",
                      help="Plot height [pixels]", metavar="N")
    parser.add_option("--colormap", dest="colormap", metavar="NAME",
                      help="Color palette: rainbow, rssi", default="rainbow")
    parser.add_option("--histogram", dest="histogram", metavar="N", type="int",
                      help="Draw a cumulative histogram of last N data samples")
    parser.add_option("--timestamps", dest="timestamps", action="store_true",
                      help="Draw timestamps in the margin")

    group = optparse.OptionGroup(parser, "Sample options")
    group.add_option("--blocksize", dest="blocksize", default=1000, type="int",
                     help="Read block size [bytes]")
    group.add_option("--type", dest="type", default="int8",
                     help="Data type: int8 [default], uint8")
    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    # Start doing stuff

    if len(args) < 1:
        parser.error("Supply a FIFO or device filename")

    infile = open(args[0])
    blocksize = options.blocksize
    
    if options.histogram:
        histogram = Histogram(options.histogram)
    
    if options.type == "uint8":
        typestring = "@%dB"
        datarange = (0, 255)
    elif options.type == "int8":
        typestring = "@%db"
        datarange = (-128, 127)
    else:
        parser.error("Unrecognized datatype")
    
    # Set up the GUI, register a watch on the FIFO, kickstart things
    colormap = makeColormap(datarange, options.colormap)
    gui = Gui(options.width, options.height, colormap, datarange, histogram, options.timestamps)
    plotter = gui.getPlotter()
    gtk.input_add(infile, gtk.gdk.INPUT_READ, readable)
    gui.run()
