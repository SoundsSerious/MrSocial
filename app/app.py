# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 21:23:44 2016

@author: Sup
"""
#Add Parent Directory For Common Server / App Interface
import sys
sys.path.append('../')

from kivy.support import install_twisted_reactor
install_twisted_reactor()

from zope.interface import implements, implementer, Interface

from twisted.internet import reactor
from twisted.protocols import basic
from twisted.cred import credentials
from twisted.internet.protocol import Protocol, ReconnectingClientFactory

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
from kivy.core.window import Window

from kivy.garden.navigationdrawer import NavigationDrawer

from config import *
from style import *
from maps import *
from login import *
from message import *
from profiles import *
from social_interface import *

iphone =  {'width':320 , 'height': 568}#320 x 568

SAMPLE_IMAGE = 'https://s-media-cache-ak0.pinimg.com/originals/ec/8e/8f/ec8e8f26ee298a6c852a7b7de37bd96b.jpg'


class SocialHomeWidget(Widget):
    '''Manages Creen Widgets With Application Drawer'''

    app = None

    def __init__(self, app):
        super(SocialHomeWidget,self).__init__()
        self.app = app
        self.setupMenu()
        self.setupAppPanel()

        self.bind(pos = self.update_rect,
                  size = self.update_rect)

    def setupMenu(self):
        self.menu = NavigationDrawer()
        self.menu.anim_type = 'reveal_below_anim'

        self.menu_panel = BoxLayout(orientation='vertical')
        self.menu_panel.add_widget(Label(text='User Profile'))
        self.menu.add_widget(self.menu_panel)
        self.add_widget( self.menu )

    def setupAppPanel(self):
        self.menuScreenManager = ScreenManager(transition=FadeTransition())
        self.menu.add_widget(self.menuScreenManager)

        self.addMenuScreenWidget('maps',MapWidget())
        self.addMenuScreenWidget('profiles',SwipingWidget(self.app))
        self.addMenuScreenWidget('chat',MessageWidget(self.app))

        self.changeScreen('maps')

    def addMenuScreenWidget(self,name,new_widget):
        #Add Menu Button
        button = Button(text= name.capitalize() )
        self.menu_panel.add_widget(button)
        button.bind( on_press = lambda *args: self.changeScreen(name) )

        #Add The Widget Itself
        screen = Screen(name = name)
        screen.add_widget(new_widget)

        setattr(self,name,new_widget)

        self.menuScreenManager.add_widget(screen)

    def changeScreen(self,screenName):
        self.menuScreenManager.current = screenName

    def update_rect(self,*args):
        self.menu.size = self.size




class SocialApp(App):

    host = HOME_URL
    port = SOCIAL_PORT

    authenticated = BooleanProperty(False)
    social_client = ObjectProperty(None)
    friends = ListProperty(None)
    projects = ListProperty(None)
    user_object = ObjectProperty(None)

    def build(self):
        self.connectToServer()
        sm = self.setupLoginScreen()

        return sm

    def auth_handler(self, *args):
        if self.authenticated == False:
            self.loginScreenManager.current = 'login'
        else:
            self.loginScreenManager.current = 'app'

    def setupLoginScreen(self):
        Window.size = (iphone['width'],iphone['height'])
        self.loginScreenManager = ScreenManager(transition=FadeTransition())

        self.loginScreen = Screen(name = 'login')
        self.login = Login(self, LOCAL_IMAGE)
        self.loginScreen.add_widget(self.login)

        self.appScreen = Screen(name = 'app')
        self.socialWidget = SocialHomeWidget(self)
        self.appScreen.add_widget(self.socialWidget)

        self.loginScreenManager.add_widget( self.loginScreen)
        self.loginScreenManager.add_widget( self.appScreen)

        self.loginScreenManager.current = 'login'
        self.bind(authenticated = self.auth_handler)
        #Kickoff
        self.auth_handler()

        return self.loginScreenManager

    def on_connect(self, client):
        print "connected successfully!"
        self.social_client = client

    def on_social_client(self,instance, value):
        self.update_client()

    def update_client(self):
        #Get User Info
        #Get Friends
        #Get Projects
        pass

    def connectToServer(self):
        reactor.connectTCP(self.host, self.port, Social_ClientFactory(self))

    @property
    def local_users(self):
        '''Yeild Users From Server'''
#        if self.social_client and self.authenticated:
#            users = self.social_client.get_local_users()
#            return users
#        else: #Shooting Blanks
#            return []


if __name__ == '__main__':
    app = SocialApp()
    app.run()