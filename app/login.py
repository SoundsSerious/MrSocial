# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 16:22:10 2016

@author: Cabin
"""

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FallOutTransition, \
                                    FadeTransition, RiseInTransition

from kivy.properties import *
from kivy.clock import Clock
from kivy.app import App

from config import *
from style import *
from maps import *
from social_interface import *

SAMPLE_IMAGE = 'https://s-media-cache-ak0.pinimg.com/originals/ec/8e/8f/ec8e8f26ee298a6c852a7b7de37bd96b.jpg'
LOCAL_IMAGE = os.path.join(EXP_PATH,'app','Login_Image.jpg')

class Login(Widget):

    _background_url = None
    _text_color = (0.722,0.315,0.1,1)
    def __init__(self,app, background_url = None):
        self.app = app
        super(Login,self).__init__()
        '''Get Background URL Image, Create Layout, and add login stuff'''
        self._background_url = background_url

        self._lay = FloatLayout(size_hint = (None, None))
        self._title = Label( text = 'EXPOSURE', \
                            color = self._text_color,
                            font_name= os.path.join(EXP_PATH,'hotel_font.ttf'),
                            valign = 'bottom', size_hint = (1,0.15),
                            pos_hint = {'center_x':0.5,'center_y':0.9},
                            font_size=80, bold=True)

        self._prompt = Label( text = 'ENTER YOUR EMAIL', \
                            color = self._text_color,
                            font_name= os.path.join(EXP_PATH,'hotel_font.ttf'),
                            valign = 'bottom', size_hint = (0.8,0.15),
                            pos_hint = {'center_x':0.5,'center_y':0.55},
                            font_size=25, bold=True, halign="center")
        self._image = Image( source = self._background_url , \
                                  size_hint = (None, None),
                                  pos_hint = {'center_x':0.5,'center_y':0.5},
                                  keep_ratio = True,
                                  allow_stretch = True,
                                  opacity = 0.5
                                 )

        self._login = TextInput(multiline = False,
                                pos_hint = {'center_x':0.5,'center_y':0.5},
                                size_hint = (0.8, 0.05))
        self._login.bind( on_text_validate = self.authenticate_login_value)


        self._lay.add_widget(self._image)
        self._lay.add_widget(self._login)
        self._lay.add_widget(self._prompt)
        self._lay.add_widget(self._title)
        self.add_widget(self._lay)

        self.bck_init = False

        self.bind(pos = self.update_rect,
                  size = self.update_rect)

    def authenticate_login_value(self,value):
        msg = self._login.text
        if msg and self.app.connection:
            self.app.social_client.attemptConnection(str(msg))
            self._login.text = ""

    def get_background_size(self):
        w,h = self.size
        iw,ih = self._image.get_norm_image_size()
        ratio = iw,ih
        dw,dh = max(0,w-iw),max(0,h-ih)
        rw,rh = dw/float(w),dh/float(h)
        inflate = 1+max(rw,rh)
        new_size = (iw*inflate,ih*inflate)
        if new_size[0]* new_size[1] > w * h:
            return new_size
        else:
            r = 1.2
            if h > w:
                r = (h / w)* 1.5 + 1
            return w*r,h*r

    def update_rect(self,*args):
        if not self.bck_init:
            for i in range(5):
                #Iteration On Startup...Kinda shitty..
                #better to create expanding image class
                self._image.size = self.get_background_size()
            self.bck_init = True
        self._image.size = sz =   self.get_background_size()
        self._lay.size = self.size
        self._lay.pos = self.pos

app = None
if __name__ == '__main__':
    global app

    Clock.max_iteration = 20

    class LoginApp(App):

        host = 'localhost'
        port = 17776

        authenticated = BooleanProperty(False)
        connection = ObjectProperty(None)

        def build(self):
            self.connectToServer()

            self.sm = ScreenManager(transition=FadeTransition())

            self.loginScreen = Screen(name = 'login')
            self.login = Login(self, LOCAL_IMAGE)
            self.loginScreen.add_widget(self.login)

            self.mapscreen = Screen(name = 'map')
            self.map = MapWidget()
            self.mapscreen.add_widget(self.map)

            self.sm.add_widget( self.loginScreen)
            self.sm.add_widget( self.mapscreen)

            self.sm.current = 'login'
            self.bind(authenticated = self.auth_handler)
            #Kickoff
            self.auth_handler()

            return self.sm

        def auth_handler(self, *args):
            if self.authenticated == False:
                self.sm.current = 'login'
            else:
                self.sm.current = 'map'


        def on_connect(self, connection):
            print "connected successfully!"
            #self.connection = connection

        def connectToServer(self):
            reactor.connectTCP(self.host, self.port, Social_ClientFactory(self))

    app = LoginApp()
    app.run()