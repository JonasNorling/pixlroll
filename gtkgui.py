#!/usr/bin/python
#
# Copyright 2014, Jonas Norling <jonas.norling@gmail.com>
#
# This software program is licensed under the GNU General Public License v2.
#

from __future__ import division
import gtk
import cairo
import colorsys

class PlotWidget(gtk.DrawingArea):
    def __init__(self, w, h):
        gtk.DrawingArea.__init__(self)
        self.plotsize = (w, h)
        self.size = (1000, 1000)
        self.bottommargin = 20
        self.legendsize = 10
        self.backgroundcolor = (0.0, 0.0, 0.0, 1)
        self.connect("expose-event", self.on_expose_event)
        self.connect("configure-event", self.on_configure_event)
        self.connect("realize", self.on_realize)
        self.plotbuffer = None
        self.ctx = None
        self.x = 0

        self.colormap = self.makeColormap()

    def makeColormap(self):
        c = {}
        for v in range(-128, 128):
            n = (v + 128) / 256.0 # n: 0..1
            if v >= -100 and v < -20:
                s = 1.0
            else:
                s = 0.0
            c[v] = colorsys.hsv_to_rgb(n - 0.1, s, n * 3)
        return c

    def on_realize(self, widget=None):
        self.realized = True
        winctx = self.window.cairo_create()
        
        if self.plotbuffer is None:
            self.plotbuffer = winctx.get_target().create_similar(cairo.CONTENT_COLOR_ALPHA,
                                                                 self.plotsize[0], self.plotsize[1])
            self.ctx = cairo.Context(self.plotbuffer)
            self.ctx.set_source_rgba(*self.backgroundcolor)
            self.ctx.paint()

    def on_configure_event(self, widget, event):
        self.size = (event.width, event.height)
        self.on_realize(widget)

    def on_expose_event(self, widget, event):
        """Blit out the backbuffer"""
        winctx = self.window.cairo_create()
        winctx.set_source_rgba(*self.backgroundcolor)
        winctx.paint()
        winctx.save()
        winctx.scale(self.size[0] / self.plotsize[0], (self.size[1]-self.bottommargin) / self.plotsize[1])
        winctx.set_source_surface(self.plotbuffer)
        winctx.paint()
        winctx.restore()

        # Draw a legend
        for v in range(-128, 128):
            x = v + 128
            w = self.size[0]/255.0
            winctx.rectangle(x * w, self.size[1]-self.legendsize, w + 1, self.legendsize)
            winctx.set_source_rgb(*self.colormap[v])
            winctx.fill()

    def addData(self, values):
        for v in values:
            self.ctx.rectangle(self.x, self.plotsize[1]-1, 1, 1)
            self.ctx.set_source_rgb(*self.colormap[v])
            self.ctx.fill()

            self.x += 1
            if self.x >= self.plotsize[0]:
                self.x = 0

                # Scroll contents
                self.ctx.fill()
                self.ctx.set_source_surface(self.plotbuffer, 0, -1)
                self.ctx.paint()
                self.ctx.rectangle(0, self.plotsize[1]-1, self.plotsize[0], 1)
                self.ctx.set_source_rgba(*self.backgroundcolor)

                # Update window when a new line has been drawn
                self.queue_draw()

class PlotWindow(gtk.Window):
    def __init__(self, plotWidget, w, h):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_default_size(w, h);
        self.connect("destroy", self.quit_callback)

        mainBox = gtk.HBox()
        self.add(mainBox)
        self.plot = plotWidget
        mainBox.pack_start(self.plot, True)

        self.show_all()

    def quit_callback(self, b):
        gtk.main_quit()


class Gui(object):
    def __init__(self, w, h):
        self.plotwidget = PlotWidget(w, h)
        self.plotwin = PlotWindow(self.plotwidget, w, h)
    
    def getPlotter(self):
        return self.plotwidget
    
    def run(self):
        self.plotwin.show_all()
    
        try:
            gtk.main()
        except KeyboardInterrupt:
            pass
