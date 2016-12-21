# -*- coding: utf-8 -*-
"""
Created on Sat Sep 17 22:54:02 2016

@author: Sup

'''#Default KV Image Definition
<Image,AsyncImage>:
    canvas:
        Color:
            rgba: self.color
        Rectangle:
            texture: self.texture
            size: self.norm_image_size
            pos: self.center_x - self.norm_image_size[0] / 2., self.center_y - self.norm_image_size[1] / 2.

#RoundedLabel
        Color:
            rgba:  self.background_color
        RoundedRectangle:
            size: self.texture_size
            pos: self.center[0] - self.texture_size[0]/2.0,self.center[1] - self.texture_size[1]/2.0
            radius: self._radius
        Color:
            rgba:  self.font_color
        Rectangle:
            texture: self.texture
            size: self.texture_size
            pos: self.center[0] - self.texture_size[0]/2.0,self.center[1] - self.texture_size[1]/2.0
            radius: self._radius
'''
"""

from __future__ import absolute_import

from kivy.app import App
from kivy.uix.button import *
from kivy.uix.label import *
from kivy.uix.widget import *
from kivy.uix.boxlayout import *
from kivy.uix.floatlayout import *
from kivy.graphics import *
from kivy.graphics.texture import *
from kivy.graphics.vertex_instructions import *
from kivy.uix.behaviors import *
from kivy.uix.image import *
from kivy.uix.effectwidget import *
from kivy.core.text import Label as CoreLabel

from kivy.garden.mapview import MapView
from kivy.core.window import Window
from kivy.graphics.opengl import glFinish
from time import time

from config import *
#Window.size = (300, 100)

# -*- coding: utf-8 -*-
from kivy.lang import Builder

TEXTURE = 'kiwi.jpg'
YELLOW = (1, .7, 0)
ORANGE = (1, .45, 0)
RED = (1, 0, 0)
WHITE = (1, 1, 1)

class Theme(object):
    '''In Which We Color Our Application'''
    pass


class Style(object):
    font_size = 100
    font_color = (1,1,1)

class RadialGradientStyleist(Style):
    '''In Which We Color Objects With A Radial Gradient'''

    _color1 = (1, 1, 0)
    _color2 = (1, 0, 0)
    _tex_size = (64, 64)
    _shader = '''
        $HEADER$
        uniform vec3 border_color;
        uniform vec3 center_color;
        void main (void) {
            float d = clamp(distance(tex_coord0, vec2(0.5, 0.5)), 0., 1.);
            gl_FragColor = vec4(mix(center_color, border_color, d), 1);
        }
        '''

    @property
    def radial_gradient(self):

        fbo = Fbo(size=self._tex_size)
        fbo.shader.fs = self._shader

        # use the shader on the entire surface
        fbo['border_color'] = map(float, self._color1)
        fbo['center_color'] = map(float, self._color2)
        with fbo:
            Color(1, 1, 1)
            Rectangle(size=self._tex_size)
        fbo.draw()

        return fbo.texture

    def __call__(self):
        return self.radial_gradient

class StyleUnit(object):
    '''In Which We Color Objects'''

    _styleist = None
    _style = None
    def initalizeStyle(self):
        if self._styleist:
            glFinish()
            self._style = self._styleist()
            glFinish()

class RoundedButton(ButtonBehavior,Widget,StyleUnit):
    '''In which we make a damn button with rounded corners'''

    _style = None
    _radius = [20]
    _label = None
    _tex_tex = None
    _text = ''
    _styleist = RadialGradientStyleist

    def __init__(self, text = '',**kwargs):
        super(ButtonBehavior,self).__init__(**kwargs)
        super(Widget,self).__init__(**kwargs)
        self._text = text
        self.initalizeStyle()
        #Draw Rounded Rectangle
        with self.canvas:
            Color(1, 1, 1)
            self.rect = RoundedRectangle(size = self.size ,pos=self.center, \
                                    radius=self._radius,texture=self._style())

            self.drawText()


        self.bind(pos = self.update_rect,
                  size = self.update_rect)

    def drawText(self):
        if self._text:
            print self.size
            self._label = CoreLabel( text=self._text,\
                                font_size = self.size[1],\
                                color = self._styleist.font_color)
            self._label.refresh()
            tex_tex = self._label.texture
            tex_size= list(tex_tex.size)

            if self._tex_tex is None:
            #self.canvas.remove(self._tex_tex)
                self._tex_tex = Rectangle( texture=tex_tex, size = tex_size)
            else:
                self._tex_tex.size = self.size

    def update_rect(self,*args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.drawText()


Builder.load_string(
'''
<-RoundedImage>:
    canvas:
        Color:
            rgb:  self.color
        StencilPush
        RoundedRectangle:
            size: self.norm_image_size
            pos: self.center[0] - self.norm_image_size[0]/2.0,self.center[1] - self.norm_image_size[1]/2.0
            radius: self._radius
        StencilUse
        Rectangle:
            texture: self.texture
            size: self.norm_image_size
            pos: self.center[0] - self.norm_image_size[0]/2.0,self.center[1] - self.norm_image_size[1]/2.0
        StencilUnUse
        RoundedRectangle:
            size: self.norm_image_size
            pos: self.center[0] - self.norm_image_size[0]/2.0,self.center[1] - self.norm_image_size[1]/2.0
            radius: self._radius
        StencilPop

<-RoundedLabel>:
        ''')

#
class RoundedImage(Image):

    _radius_pct = 0.5
    _radius = [20]

    def __init__(self,**kwargs):
        super(RoundedImage,self).__init__(**kwargs)
        self.bind(size = self.radius_cmd)
        #self.bind(pos = self.center_image)

    def center_image(self, *args):
        print 'centering'
        x,y = self.center
        self.pos =   x - self.norm_image_size[0]/2.0,\
                    y - self.norm_image_size[1]/2.0

    def radius_cmd(self,*args):
        #if self.height:
        self._radius = [self.height * self._radius_pct]
        #else:
        #    return [10]


class RoundedLabel(Label):
    _radius_pct = 0.8
    _radius = [10]
    maxrad = 10

    _font_color = None
    _background_color = None

    _max_width = 300

    def __init__(self,**kwargs):
        super(RoundedLabel,self).__init__(size_hint=(1,1),**kwargs)

        #Get Some Inputs
        self._max_width = kwargs.get('max_width',300)
        self._background_color = kwargs.get('background_color',(0,0.2,0.4,1))
        self._font_color = kwargs.get('font_color',(0.8,1,1,1))

        #Set Some Defaults
        self.size_hint_y =  None
        self.text_size = self._max_width, None
        self.height =  self.texture_size[1]

        #Canvas FTW
        with self.canvas:
            Color(*self._background_color)
            self.rect = RoundedRectangle(size = self.box_size,pos= self.box_pos,\
                                        radius = self._radius)
            Color(*self._font_color)
            self.text_rect = Rectangle( texture = self.texture, size = self.texture_size,\
                                   pos = self.txt_pos)

        #callbacks, to be binded
        self.bind(pos = self.update_rect,
                  size = self.update_rect)

        self.update_rect()

    @property
    def justified_x(self):
        if self.halign == 'right':
            val =  self.width - (self.texture_size[0]+self._radius[0])
        elif self.halign == 'center':
            val  =  0
        elif self.halign == 'left':
            val =  2
        return val

    @property
    def box_size(self):
        return self.texture_size[0] + self._radius[0]- 2,\
                  self.texture_size[1] + self._radius[0] -2

    @property
    def box_pos(self):
        val =  self.justified_x  ,\
                 self.center[1] - self.texture_size[1]/2.0
        return val

    @property
    def txt_pos(self):
        val = self.justified_x  + self._radius[0]/2.0,\
                 self.center[1] - self.texture_size[1]/2.0 + self._radius[0]/2.0
        return val

    def update_rect(self,*args):
        self.texture_update()
        self.height =  self.texture_size[1] + self._radius[0]
        rad = self.texture_size[1] * self._radius_pct
        if rad > self.maxrad:
            self.rect.radius = [self.maxrad]
        else:
            self.rect.radius = [rad]
        self.rect.size = self.box_size
        self.rect.pos =  self.box_pos

        self.text_rect.pos = self.txt_pos
        self.text_size = self._max_width , None
        self.text_rect.size = self.texture_size
        self.text_rect.texture = self.texture
        #print self.size, self.pos, self
        #print self.text_rect.size, self.text_rect.pos,self.txt_pos,self.texture_size,  repr(self.text)
        #print self.rect.size, self.rect.pos, self.box_pos, self.box_size, repr(self.text)

app = None
if __name__ == '__main__':
    import os
    global app
    class KivyApp(App):
        def build(self):
            tex = 'Some Text '*10+'\n'
            tex *= 5
            lay = BoxLayout(orientation='vertical')
            lay.add_widget(RoundedLabel(text = 'Hey Hey How Are You?',halign='right',\
                                        background_color = (1,1,1,0.8),\
                                        font_color = (0,0.2,0.5)))
            lay.add_widget(RoundedLabel(text = 'Hey Hey How Are You?',halign='left',\
                                        background_color = (1,1,1,0.8),\
                                        font_color = (0,0.2,0.5)))
            lay.add_widget(RoundedLabel(text = 'Hey Hey How Are You?',halign='left',\
                            background_color = (1,1,1,0.8),\
                            font_color = (0,0.2,0.5)))
            return lay

    app = KivyApp()
    app.run()

