from __future__ import division
import gtk
import cairo

class PlotWidget(gtk.DrawingArea):
    def __init__(self, w, h):
        gtk.DrawingArea.__init__(self)
        self.plotsize = (w, h)
        self.size = (1000, 1000)
        self.backgroundcolor = (0.3, 0.3, 0.3, 1)
        self.connect("expose-event", self.on_expose_event)
        self.connect("configure-event", self.on_configure_event)
        self.connect("realize", self.on_realize)
        self.plotbuffer = None
        self.ctx = None
        self.x = 0
        self.y = 0

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
        winctx.save()
        winctx.scale(self.size[0] / self.plotsize[0], self.size[1] / self.plotsize[1])
        winctx.set_source_surface(self.plotbuffer)
        winctx.paint()
        winctx.restore()

    def getColor(self, v):
        g = (128+v) / 128.0
        r = 0
        b = 0
        if v >= -100:
            r = 0.3
        if v > -96:
            r = 0.6
        if v > -70:
            b = 0.5
        return (r, g, b)

    def addData(self, values):
        for v in values:
            self.ctx.rectangle(self.x, self.y, 1, 1)
            self.ctx.set_source_rgb(*self.getColor(v))
            self.ctx.fill()

            self.x += 1
            if self.x >= self.plotsize[0]:
                self.x = 0

                # FIXME: Scroll contents
                #self.ctx.set_source_surface(self.plotbuffer)
                #self.ctx.paint()
                self.y += 1
                self.y %= self.plotsize[1]
                self.ctx.rectangle(0, self.y, self.plotsize[0], 10)
                self.ctx.set_source_rgba(*self.backgroundcolor)
                self.ctx.fill()
        
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
