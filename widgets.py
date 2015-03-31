#!/usr/bin/python2
# -*- coding: utf-8 -*-

import cairo

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from expressions import Monomial
from expressions import Polynomial
from expressions import Equation
from expressions import Function

import globals as G


class Area(Gtk.DrawingArea):

    def __init__(self, function):
        Gtk.DrawingArea.__init__(self)

        if type(function) in [Monomial, Polynomial]:
            function = function.repr

        if type(function) == str:
            self.function = Function(function)

        self.context = None
        self.background_color = (1, 1, 1)
        self.axis_color = (0, 0, 0)
        self.grid_color = (0.8, 0.8, 0.8)
        self.line_color = (0, 0, 1)
        self.line_width = 2
        self.axis_width = 4
        self.grid_width = 1
        self.unit_space = 25
        self.font_size = self.unit_space / 2.0
        self.font_color = (0.4, 0.4, 0.4)
        self.point_color = (1, 0, 0)
        self.point_width = 5
        self.connect('draw', self.__draw_cb)

    def __draw_cb(self, widget, context):
        allocation = self.get_allocation()
        self.context = context
        self.width = allocation.width
        self.height = allocation.height

        self.render()

    def render(self):
        self.render_background()
        self.render_grid()
        self.render_axis()
        self.render_graph()

    def render_background(self):
        self.context.set_source_rgb(*self.background_color)
        self.context.rectangle(0, 0, self.width, self.height)
        self.context.fill()

    def render_grid(self):
        x = self.width / 2.0
        y = self.height / 2.0

        self.context.set_line_width(self.grid_width)

        _x = x + self.axis_width / 2.0
        n = 0
        while _x < self.width:
            _x += self.unit_space
            self.context.set_source_rgb(*self.grid_color)
            self.context.move_to(_x, 0)
            self.context.line_to(_x, self.height)

            self.context.set_source_rgb(*self.font_color)
            self.context.set_font_size(self.font_size)
            self.context.move_to(_x - self.unit_space, self.height / 2.0 + self.unit_space / 2.0)
            self.context.show_text(str(n))
            n += 1

        _x = x - self.axis_width / 2.0
        n = 0
        while _x > 0:
            self.context.set_source_rgb(*self.grid_color)
            _x -= self.unit_space
            self.context.move_to(_x, 0)
            self.context.line_to(_x, self.height)

            if n != 0:
                self.context.set_source_rgb(*self.font_color)
                self.context.set_font_size(self.font_size)
                self.context.move_to(_x + self.unit_space, self.height / 2.0 + self.unit_space / 2.0)
                self.context.show_text('-' + str(n))

            n += 1

        _y = y + self.axis_width / 2.0
        n = 0
        while _y < self.height:
            _y += self.unit_space
            self.context.move_to(0, _y)
            self.context.line_to(self.width, _y)

            if n != 0:
                self.context.set_source_rgb(*self.font_color)
                self.context.set_font_size(self.font_size)
                self.context.move_to(self.width / 2.0 + self.font_size / 3.0, _y - self.unit_space / 2.0)
                self.context.show_text('-' + str(n))

            n += 1

        _y = y - self.axis_width / 2.0
        n = 0
        while _y > 0:
            _y -= self.unit_space
            self.context.move_to(0, _y)
            self.context.line_to(self.width, _y)

            if n != 0:
                self.context.set_source_rgb(*self.font_color)
                self.context.set_font_size(self.font_size)
                self.context.move_to(self.width / 2.0 + self.font_size / 3.0, _y + self.unit_space * 3 / 2.0)
                self.context.show_text(str(n))

            n += 1

        self.context.stroke()

    def render_axis(self):
        self.context.set_source_rgb(*self.axis_color)
        self.context.set_line_width(self.axis_width)
        self.context.move_to(0, self.height / 2.0)
        self.context.line_to(self.width, self.height / 2.0)
        self.context.move_to(self.width / 2.0, 0)
        self.context.line_to(self.width / 2.0, self.height)
        self.context.stroke()

    def render_graph(self):
        if not self.function:
            return

        if self.function.degree == 1:
            # Draw a line
            # General expresion:
            #   ax + b
            max_x = 0
            max_y = 0
            min_x = 0
            min_y = 0
            for x in range(0, int(self.width / self.unit_space * 10.0)):
                x /= 10.0
                if x == 0:
                    self.draw_point(x, self.function(x))

                if x > max_x:
                    max_x = float(x)
                    max_y = float(self.function(x))

                if -x < min_x:
                    min_x = float(-x)
                    min_y = float(self.function(-x))

            self.context.set_source_rgb(*self.line_color)
            self.context.set_line_width(self.line_width)
            self.context.move_to(self.width / 2.0 + min_x * self.unit_space - self.grid_width / 2.0 - self.line_width / 2.0,
                                 self.height / 2.0 - min_y * self.unit_space - self.grid_width / 2.0)

            self.context.line_to(self.width / 2.0 + max_x * self.unit_space + self.line_width,
                                 self.height / 2.0 - max_y * self.unit_space)
            self.context.stroke()

        elif self.function.degree == 2:
            # Draw a parable
            # General expresion:
            #   ax^2 + bx + c
            monomials = self.function.polynomial.monomials
            a = int(monomials[2][0].sign + str(monomials[2][0].coefficient))
            b = int(monomials[1][0].sign + str(monomials[1][0].coefficient)) if 1 in monomials else 0
            c = int(monomials[0][0].sign + str(monomials[0][0].coefficient)) if 0 in monomials else 0

            # Vertex
            x = -(b / 2.0 * a)
            y = float(self.function(x))
            self.draw_point(x, y)

            #print(self.function(self.width / 2.0 / self.unit_space))
            x1 = 1.0
            y1 = float(self.function(x1))
            x2 = -1.0
            y2 = y1
            x3 = 2.0
            y3 = float(self.function(x3))
            x4 = -2.0
            y4 = y3

            # FIXME: NO FUNCIONAAAA, porque cairo acorta la distancia, sin pasar por todos los puntos especificados
            self.draw_point(x1, y1)
            self.draw_point(x2, y2)
            self.draw_point(x3, y3)
            self.draw_point(x4, y4)

            self.draw_curve(x3, y3, x, y, x4, y4)
            #self.draw_curve(x4, y4, x2, y2, x, y)
            #self.draw_curve(x3, y3, x1, y1, x, y)

    def draw_point(self, x, y):
        x = self.width / 2.0 + float(x) * self.unit_space - (self.point_width / 2.0 if float(x) < 0 else 0) + (self.point_width / 2.0 if float(x) > 0 else 0)
        y = self.height / 2.0 - float(y) * self.unit_space - (self.point_width / 2.0 if float(y) else 0)
        self.context.set_source_rgb(*self.point_color)
        self.context.arc(x, y, self.point_width, 0, 2 * G.PI)
        self.context.fill()

    def draw_curve(self, x1, y1, x2, y2, x3, y3):
        x1 = self.width / 2.0 + x1 * self.unit_space
        y1 = self.height / 2.0 - y1 * self.unit_space
        x2 = self.width / 2.0 + x2 * self.unit_space
        y2 = self.height / 2.0 - y2 * self.unit_space
        x3 = self.width / 2.0 + x3 * self.unit_space
        y3 = self.height / 2.0 - y3 * self.unit_space

        #print(x1, y1, x2, y2, x3, y3)
        self.context.curve_to(x1, y1, x2, y2, x3, y3)
        self.context.stroke()


class Entry(Gtk.ScrolledWindow):

    __gsignals__ = {
        'activate': (GObject.SIGNAL_RUN_FIRST, None, []),
        'changed': (GObject.SIGNAL_RUN_FIRST, None, []),
    }

    __gtype_name__ = 'Entry'

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.__view = Gtk.TextView()
        self.__buffer = self.__view.get_buffer()

        self.set_size_request(-1, 45)
        self.add_events(Gdk.EventMask.KEY_RELEASE_MASK)
        self.connect('key-release-event', self.__key_release_event_cb)
        self.__buffer.connect('changed', self.__changed_cb)

        self.add(self.__view)

    def __key_release_event_cb(self, textview, event):
        if event.keyval == 65293:  # 65293 = Enter
            self.backspace()
            self.emit('activate')
            return False

    def __changed_cb(self, buffer):
        self.emit('changed')

    def set_text(self, texto):
        self.__buffer.set_text(texto)

    def get_text(self):
        start, end = self.__buffer.get_bounds()
        return self.__buffer.get_text(start, end, 0)

    def insert_at_cursor(self, text):
        insert_parenthesis = False
        if text.endswith('()'):
            text = text[:-1]
            insert_parenthesis = True

        self.__buffer.insert_at_cursor(text)

        if insert_parenthesis:
            pos = self.__buffer.get_property('cursor-position')
            text = self.get_text()
            text = text[:pos] + ')' + text[pos:]
            self.set_text(text)
            textiter = self.__buffer.get_iter_at_offset(pos)
            self.__buffer.place_cursor(textiter)

    def backspace(self):
        pos = self.__buffer.get_property('cursor-position')
        textiter = self.__buffer.get_iter_at_offset(pos)
        self.__buffer.backspace(textiter, True, True)


class ButtonBase(Gtk.DrawingArea):

    __gsignals__ = {
        'clicked': (GObject.SIGNAL_RUN_FIRST, None, []),
    }

    def __init__(self, label):
        Gtk.DrawingArea.__init__(self)

        self.context = None
        self.limit = 0
        self.processes = {}  # {(x, y): progress}
        self.width = 0
        self.height = 0
        self.label = label
        self.label_size = 30
        self.label_font = 'Bold'
        self.label_color = (1, 1, 1)
        self.effect_color = (0.5, 0.5, 0.5)
        self.mouse_in_color = (0.075, 0.075, 0.075)
        self.mouse_out_color = (0.3, 0.3, 0.3)
        self.insensitive_color = (0.5, 0.5, 0.5)
        self.background_color = self.mouse_out_color
        self.__mouse_in = False

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.ENTER_NOTIFY_MASK |
                        Gdk.EventMask.LEAVE_NOTIFY_MASK)

        self.connect('draw', self.__draw_cb)
        self.connect('button-release-event', self.__button_release_event_cb)
        self.connect('enter-notify-event', self.__enter_notify_event_cb)
        self.connect('leave-notify-event', self.__leave_notify_event_cb)

    def __draw_cb(self, area, context):
        allocation = self.get_allocation()
        self.context = context
        self.width = allocation.width
        self.height = allocation.height

        self.limit = max(self.width, self.height)
        self.label_size = min(self.width, self.height) / 2.0

        self.context.set_source_rgb(*self.background_color)
        self.context.rectangle(0, 0, self.width, self.height)
        self.context.fill()

        self.__render()

    def __button_release_event_cb(self, area, event):
        if event.button == 1:
            self.processes[(event.x, event.y)] = 0
            self.emit('clicked')

    def __enter_notify_event_cb(self, area, event):
        self.background_color = self.mouse_in_color
        self.__mouse_in = True
        self.__render()

    def __leave_notify_event_cb(self, area, event):
        self.background_color = self.mouse_out_color
        self.__mouse_in = False
        self.__render()

    def remove_processes(self, lista):
        if not lista:
            return

        backup = self.processes
        self.processes = {}

        for coords, progress in backup.items():
            if not coords in lista:
                self.processes[coords] = progress

    def __render(self):
        if not self.context:
            return

        if self.label:
            self.context.set_font_size(self.label_size)
            self.context.select_font_face(self.label_font,
                                          cairo.FONT_SLANT_NORMAL,
                                          cairo.FONT_WEIGHT_NORMAL)

            w = self.context.text_extents(self.label)[2]
            h = self.context.text_extents(self.label)[3]
            x = (self.width - w) / 2.0
            y = (self.height + h) / 2.0

            self.context.move_to(x, y)
            self.context.set_source_rgb(*self.label_color)
            self.context.show_text(self.label)

        processes_to_remove = []
        for coords, progress in self.processes.items():
            transparency = 1.0 - (1.0 / self.limit * progress)
            color = self.effect_color + (transparency,)
            self.context.set_source_rgba(*color)
            self.context.arc(coords[0], coords[1], progress, 0, 2 * G.PI)
            self.context.fill()

            self.processes[coords] = progress + 5

            if self.processes[coords] >= self.limit:
                processes_to_remove.append(coords)

        self.remove_processes(processes_to_remove)

        GObject.idle_add(self.queue_draw)


class ButtonSimple(ButtonBase):

    def __init__(self, etiqueta):
        ButtonBase.__init__(self, etiqueta)

        self.label_size = 30
        self.label_color = (1, 1, 1)
        self.effect_color = (0.6, 0.6, 0.6)
        self.mouse_in_color = (0.4, 0.4, 0.4)
        self.mouse_out_color = (
            0.2980392156862745, 0.2980392156862745, 0.2980392156862745)
        self.background_color = self.mouse_out_color


class ButtonOperator(ButtonBase):

    def __init__(self, etiqueta):
        ButtonBase.__init__(self, etiqueta)

        self.label_color = (1, 1, 1)
        self.effect_color = (1.0, 1.0, 1.0)
        self.mouse_in_color = (0.2, 0.3, 0.8)
        self.mouse_out_color = (0.38, 0.52, 1.0)
        self.background_color = self.mouse_out_color


class ButtonSpecial(ButtonBase):

    def __init__(self, etiqueta):
        ButtonBase.__init__(self, etiqueta)

        self.label_color = (1, 1, 1)
        self.effect_color = (1.0, 1.0, 1.0)
        self.mouse_in_color = (0.4, 1.0, 0.8)
        self.mouse_out_color = (
            0.25098039215686274, 0.7411764705882353, 0.6196078431372549)
        self.insensitive_color = (0.35, 0.84, 0.72)
        self.background_color = self.mouse_out_color























"""
class Calculator(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.entry = Gtk.Entry()
        self.entry.connect('changed', self.__text_changed_cb)
        self.pack_start(self.entry, False, False, 2)

    def __text_changed_cb(self, entry):
        print(self.entry.get_text())


win = Gtk.Window()
calc = Calculator()
#area = Area('f(x) = 3x^2')

win.connect('destroy', Gtk.main_quit)

win.add(calc)
win.show_all()

Gtk.main()
"""