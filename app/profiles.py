from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.listview import ListView
from kivy.uix.carousel import Carousel
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.image import *
from kivy.uix.button import *
#from kivy.uix.behaviors.button import ButtonBehavior

import json

from kivy.properties import *

from style import *

from config import *

path = EXP_PATH

class ProfileDataLoadingWidget(Widget):
    '''Profile Loading Functionality'''

    user_dict = ObjectProperty(None)
    images = ListProperty(None)
    info = StringProperty(None)
    name = StringProperty(None)

    def __init__(self, user_id,**kwargs):
        super(ProfileDataLoadingWidget,self).__init__(**kwargs)
        #Remote Call Server, Defer Creation Of Widgets
        app = App.get_running_app()
        d = app.social_client.perspective.callRemote('get_user_info',user_id)
        d.addCallback(self.createFromJson)
        d.addCallback(self.initialize)


    def createFromJson(self,user_json):
        self.user_dict = json.loads(user_json)
        self.images = self.user_dict['images']
        self.info = self.user_dict['info']
        self.name = self.user_dict['name']

    def initialize(self,*args):
        pass


class ProfileView(ProfileDataLoadingWidget):


    def initialize(self,*args):

        user_info = ListAdapter(data= self.info.split('\n'),\
                                cls = Label)
        #Define Layout
        self._layout = BoxLayout( orientation = 'vertical' )
        self._name = Label( text = self.name.upper(), \
                            font_name= os.path.join(EXP_PATH,'hotel_font.ttf'),
                            valign = 'bottom', size_hint = (1,0.15),
                            font_size=38, bold=True,)
        #self._image = RoundedImage( source = image_url)
        #                            #allow_stretch=True)
        self._image = RoundedWebImage(source = self.images[0])
        self._info = ListView( adapter = user_info, size_hint = (1,0.6) )

        self._layout.add_widget(self._name)
        self._layout.add_widget(self._image)
        self._layout.add_widget(self._info)

        self.add_widget(self._layout)

        self.bind(pos = self.update_rect,
                  size = self.update_rect)

    def update_rect(self,*args):
        self._layout.pos = self.pos
        self._layout.size = self.size

class ProfileButton(ButtonBehavior,Widget):

    def __init__(self, user_id,**kwargs):
        self.target_func = kwargs.pop('target_func', lambda: None)
        self.bind(on_press = self.target_func)
        
        Widget.__init__(self,**kwargs)
        ButtonBehavior.__init__(self,**kwargs)
        #ProfileDataLoadingWidget.__init__(self,user_id,**kwargs)
        app = App.get_running_app()
        print 'got app {}'.format(app)
        d = app.social_client.perspective.callRemote('get_user_info',user_id)
        d.addCallback(self.createFromJson)
        d.addCallback(self.initialize)


    def createFromJson(self,user_json):
        self.user_dict = json.loads(user_json)
        self.images = self.user_dict['images']
        self.info = self.user_dict['info']
        self.name = self.user_dict['name']
        
        
        
        

    def on_press(self):
        print 'calling target_func'
        self.target_func()

    def initialize(self,*args):
        #Define Layout
        self._layout = BoxLayout( orientation = 'vertical' )
        self._name = Label( text = self.name.upper(), \
                            font_name= os.path.join(EXP_PATH,'hotel_font.ttf'),
                            valign = 'bottom', size_hint = (1,0.25),
                            font_size=25, bold=True,)
        self._image = CircleWebImage(source = self.images[0])

        self._layout.add_widget(self._name)
        self._layout.add_widget(self._image)

        self.add_widget(self._layout)

        self.bind(pos = self.update_rect,
                  size = self.update_rect)

    def update_rect(self,*args):
        self._layout.pos = self.pos
        self._layout.size = self.size





class SwipingWidget(Widget):

    canidates = ListProperty(None)

    def __init__(self, app):
        super(SwipingWidget,self).__init__()
        self.app = app

        self.swiper = Carousel(direction='right')

        self.add_widget(self.swiper)

        self.app.bind(local_users = self.updateNearby)
        self.bind(pos= self.update_rect,
                  size = self.update_rect)

    def updateNearby(self,instance,values):
        if values:
            self.canidates = []
            for user_id in values:
                self.canidates.append(user_id)
                profile = ProfileView(user_id)
                self.swiper.add_widget(profile)

    def update_rect(self,*args):
        self.swiper.size = self.size


if __name__ == '__main__':
    from kivy.config import Config
    iphone =  {'width':320 , 'height': 568}#320 x 568

    def setWindow(width,height):
        print 'Setting Window'
        Config.set('graphics', 'width', str(width))
        Config.set('graphics', 'height', str(height))

    class ProfilesApp(App):

        def build(self):
            swiper = Carousel(direction='right')

            profile = ProfileButton(user_id = 1)
            swiper.add_widget(profile)
            from kivy.core.window import Window
            Window.size = (iphone['width'],iphone['height'])

            return swiper

    #setWindow(**iphone)
    profileApp = ProfilesApp()
    profileApp.run()