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

from kivy.loader import Loader
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import *
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
DEFAULT_LOADING_IMAGE = os.path.join(EXP_PATH,'app','loading_apeture.png')
from kivy.loader import Loader
loadingImage = Loader.image(DEFAULT_LOADING_IMAGE)

class SocialHomeWidget(Widget):
    '''Manages Creen Widgets With Application Drawer'''

    app = None
    initialized = False

    def __init__(self, app, **kwargs):
        super(SocialHomeWidget,self).__init__(**kwargs)
        self.app = app
        self.app.bind(user_id = self.checkUidThenFire)
        self.setupMenuAndSubWidgets()
        self.bind(pos = self.update_rect,
                  size = self.update_rect)


    def initialize(self):
        self.setupAppPanel()

    def checkUidThenFire(self,instance,userId):
        if not self.initialized and userId:
            self.initialize()
            
    def edit_user_info(self,*args,**kwargs):
        print 'hey hey whats going on...(im getting edited)'

    def setupMenuAndSubWidgets(self):
        self.menu = NavigationDrawer()
        self.menu.anim_type = 'reveal_below_anim'
        self.add_widget( self.menu )

        self.maps = MapWidget()
        self.profiles = SwipingWidget(self.app)
        self.chat = MessageWidget(self.app)

    def setupAppPanel(self):
        #First Widget Added To Menu Is The Actual Menu
        self.menu_panel = BoxLayout(orientation='vertical')
        self.menu_panel.add_widget(ProfileButton(self.app.user_id,target_func = self.edit_user_info))
        self.menu.add_widget(self.menu_panel)

        #The Second Added Is For the Main Widget
        self.menuScreenManager = ScreenManager(transition=FadeTransition())
        self.menu.add_widget(self.menuScreenManager)

        #Different Views Are Added Here, Some could be hidden not listed here
        #ie... a user editing screen -> profile button
        self.addMenuScreenWidget('maps',self.maps)
        self.addMenuScreenWidget('profiles',self.profiles)
        self.addMenuScreenWidget('chat',self.chat)

        self.changeScreen('maps')

    def addMenuScreenWidget(self,name,new_widget):
        #Add Menu Button
        button = Button(text= name.capitalize() )
        self.menu_panel.add_widget(button)
        button.bind( on_press = lambda *args: self.changeScreen(name) )

        #Add The Widget Itself
        screen = Screen(name = name)
        screen.add_widget(new_widget)

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
    local_users = ListProperty(None)

    user_id = NumericProperty(None)
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
            reactor.callLater(1,self.update_client)

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
        self.bind(social_client = self.on_social_client)
        #Kickoff
        self.auth_handler()

        return self.loginScreenManager

    def on_connect(self, client):
        print "connected successfully!"
        self.social_client = client

    def on_social_client(self,instance, value):
        print 'updating social client'
        reactor.callLater(1,self.update_client)

    def update_client(self):
        print 'updating client'
        #Get Nearby
        d = defer.maybeDeferred(self.get_user_id)
        #Pass User Id
        d.addCallback(self.get_user_info)
        d.addCallback(self.get_friends)
        d.addCallback(self.get_local_users)

        pass

    def connectToServer(self):
        reactor.connectTCP(self.host, self.port, Social_ClientFactory(self))


    def get_user_id(self):
        if self.social_client and self.authenticated:
            d = self.social_client.perspective.callRemote('user_id')
            return d.addCallback( self._cb_assignUserId )
        else:
            return None

    def get_user_info(self, user_id=None):
        '''load user info, defaults to self, if self will update user_dict info'''

        if user_id:
            uid = user_id
        elif self.user_id:
            uid = self.user_id
        else:
            uid = None

        if self.social_client and self.authenticated and uid:
            d = self.social_client.perspective.callRemote('get_user_info', uid)
            d.addCallback(self._cb_jsonToDict)
            if self.user_id and uid == self.user_id:
                d.addCallback( self._cb_assignUserInfo )
            return d
        else:
            return None

    def get_local_users(self, *args):
        '''Yeild Users From Server'''
        print 'get local users from {}'.format(self.user_id)
        if self.social_client and self.authenticated:
            d = self.social_client.perspective.callRemote('nearby',100)
            return d.addCallback(self._cb_assignLocalUsers)
        else: #Shooting Blanks
            return []

    def get_friends(self, *args):
        '''Yeild Users From Server'''
        print 'get friends from {}'.format(self.user_id)
        if self.social_client and self.authenticated:
            d = self.social_client.perspective.callRemote('friend_ids')
            return d.addCallback(self._cb_assignFriends)
        else: #Shooting Blanks
            return []

    def _cb_jsonToDict(self, json_information):
        if json_information:
            return json.loads(json_information)


    def _cb_assignUserInfo(self,user_dict):
        print 'assigning user info {}'.format(user_dict)
        if user_dict:
            self.user_object = user_dict
            return self.user_object

    def _cb_assignUserId(self,userId):
        print 'assigning user id {}'.format(userId)
        if userId or userId == 0:
            self.user_id = userId
            return userId

    def _cb_assignLocalUsers(self,localUsersResponse):
        print 'assigning local users {}'.format( localUsersResponse )
        if localUsersResponse:
            self.local_users = localUsersResponse
            return self.local_users
        return []

    def _cb_assignFriends(self,friendsList):
        print 'assigning friends {}'.format( friendsList )
        if friendsList:
            self.friends = friendsList
            return self.friends
        return []




if __name__ == '__main__':
    app = SocialApp()
    app.run()