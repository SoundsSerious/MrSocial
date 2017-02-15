import kivy
kivy.require('1.4.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.floatlayout import *
from kivy.graphics import *
from kivy.graphics.vertex_instructions import *

from config import *

Builder.load_string(
'''
<-ShutterButton>
    canvas:
        Clear

<-CameraView>:
    canvas:
        Color:
            rgb:  self.color
        Rectangle:
            texture: self.texture
            size: self.size
            pos: self.center[0] - self.size[0]/2.0,self.center[1] - self.size[1]/2.0
        ''')

class CameraView(Camera):
    _radius = [20]

    def __init__(self,**kwargs):
        super(CameraView,self).__init__(**kwargs)
        self.play = True


class ShutterButton(Button):
    '''In which we define behavior for a shoot instance drop'''

    _icon_size = (30,30)
    _img_size = (25,25)

    def __init__(self, **kwargs):
        super(ShutterButton,self).__init__(size = self._icon_size,**kwargs)
        with self.canvas:
            Color(1,1,1)

            self._ring = Ellipse(pos = self.pos,size=self._icon_size)
            self._apeture = Rectangle(pos = self.img_pos, \
                                      size= self._img_size,\
                                      source = os.path.join(EXP_PATH,'tiny_apeture.png'))

        self.bind(pos = self.update_canvas,
                  size = self.update_canvas)

    @property
    def img_pos(self):
        mrg = ((self._icon_size[0] - self._img_size[0])/2,
               (self._icon_size[1] - self._img_size[1])/2)
        return (self.pos[0] + mrg[0],self.pos[1] + mrg[1])



    def update_canvas(self,*args):
        self._ring.pos = self.pos
        self._apeture.pos = self.img_pos




class MyApp(App):
          # Function to take a screenshot
          def doscreenshot(self,*largs):
                Window.screenshot(name='screenshot%(counter)04d.jpg')

          def build(self):

                camwidget = FloatLayout()  #Create a camera Widget
                cam=CameraView(resolution=(640,480), size_hint=(1,1))
                camwidget.add_widget(cam)

                button=ShutterButton(pos_hint = {'x':0.5,'y':0},size_hint=(0.12,0.12))
                button.bind(on_press=self.doscreenshot)
                camwidget.add_widget(button)    #Add button to Camera Widget

                return camwidget


if __name__ == '__main__':
    MyApp().run()