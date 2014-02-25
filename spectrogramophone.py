#!/usr/bin/python
#
# Copyright 2014, Jonas Norling <jonas.norling@gmail.com>
#
# This software program is licensed under the GNU General Public License v2.
#

import optparse
import sys
from gtkgui import Gui
import gtk
import struct

description=\
"Spectrogramophone draws a scrolling spectrogram plot of realtime data"

blocksize = 0
plotter = None
typesize = 1
typestring = None

def readable(fd, condition):
    """Data is available in the FIFO"""
    data = fd.read(blocksize)
    count = len(data) / typesize
    values = struct.unpack(typestring % count, data)
    plotter.addData(values)
    return True

if __name__ == '__main__':
    # Parse command line
    parser = optparse.OptionParser(usage="Usage: %prog <FIFO or device>",
                                   description=description)
    parser.add_option("--width", dest="width", default="1000", type="int",
                      help="Plot width [pixels]", metavar="N")
    parser.add_option("--height", dest="height", default="600", type="int",
                      help="Plot height [pixels]", metavar="N")

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
    
    if options.type == "uint8":
        typestring = "@%dB"
    elif options.type == "int8":
        typestring = "@%db"
    else:
        parser.error("Unrecognized datatype")
    
    # Set up the GUI, register a watch on the FIFO, kickstart things
    gui = Gui(options.width, options.height)
    plotter = gui.getPlotter()
    gtk.input_add(infile, gtk.gdk.INPUT_READ, readable)
    gui.run()
