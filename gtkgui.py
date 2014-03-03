#!/usr/bin/python
#
# Copyright 2014, Jonas Norling <jonas.norling@gmail.com>
#
# This software program is licensed under the GNU General Public License v2.
#

from __future__ import division
import gtk
import cairo

class PlotWidget(gtk.DrawingArea):
    def __init__(self, w, h, colormap, datarange, histogram=None):
        gtk.DrawingArea.__init__(self)
        self.plotsize = (w, h)
        self.colormap = colormap
        self.datarange = datarange
        self.histogram = histogram
        self.size = (1000, 1000)
        self.legendsize = 20
        self.histogramsize = 200
        self.bottommargin = self.legendsize
        if histogram:
            self.bottommargin += self.histogramsize
        self.backgroundcolor = (0.0, 0.0, 0.0, 1)
        self.connect("expose-event", self.on_expose_event)
        self.connect("configure-event", self.on_configure_event)
        self.connect("realize", self.on_realize)
        self.plotbuffer = None
        self.ctx = None
        self.x = 0

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
        w = self.size[0] / (self.datarange[1] - self.datarange[0])
        tick = 10

        winctx.save()
        winctx.translate(0, self.size[1] - self.legendsize)
        textheight = 10
        legendheight = self.legendsize - textheight

        for v in range(*self.datarange):
            x = v - self.datarange[0]
            winctx.rectangle(x * w, textheight, w + 1, legendheight)
            winctx.set_source_rgb(*self.colormap[v])
            winctx.fill()

            if v % tick == 0:
                winctx.move_to(int(x * w + w/2), legendheight)
                winctx.line_to(int(x * w + w/2), legendheight * 1.5)
                winctx.set_source_rgb(1, 1, 1)

                text = "%d" % v
                extents = winctx.text_extents(text)
                winctx.move_to(int(x * w + w/2) - extents[2]/2, legendheight - 1)
                winctx.show_text(text)
                winctx.stroke()

        # Draw histogram
        if self.histogram:
            hist = self.histogram.calculate(self.datarange)
            
            winctx.set_source_rgba(0.6, 0.6, 1.0, 0.3)
            for v in range(0, 10):
                winctx.move_to(0, -0.1 * v * self.histogramsize)
                winctx.line_to(self.size[0], -0.1 * v * self.histogramsize)
            winctx.stroke()
            
            for v in range(*self.datarange):
                winctx.set_source_rgb(*self.colormap[v])
                x = v - self.datarange[0]
                winctx.rectangle(x * w, 0, w*0.8, - hist[x] * self.histogramsize)
                winctx.fill()

        winctx.restore()

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
                self.queue_draw_area(0, 0, self.size[0], self.size[1] - self.legendsize)

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
    def __init__(self, w, h, colormap, datarange, histogram=None):
        self.plotwidget = PlotWidget(w, h, colormap, datarange, histogram)
        self.plotwin = PlotWindow(self.plotwidget, w, h)
    
    def getPlotter(self):
        return self.plotwidget
    
    def run(self):
        self.plotwin.show_all()
    
        try:
            gtk.main()
        except KeyboardInterrupt:
            pass
