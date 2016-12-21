from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.listview import ListView
from kivy.uix.carousel import Carousel
from kivy.adapters.listadapter import ListAdapter

from kivy.properties import *

from style import *

from config import *

path = EXP_PATH
class Profile(Widget):
    '''In Which We Display A User'''
    _user = None
    _image_url = None
    info = None
    name = None

    def __init__(self, user_id = 1,**kwargs):
        super(Profile,self).__init__(**kwargs)
        #Query Database
        with session_scope() as sesh:
            self._user = sesh.query( User ).get( user_id )
            #Persist Info
            if self._user.picture:
                self._image_url = self._user.picture.locate(store)
            else:
                self._image_url = ''
            print self._image_url
            #Persist Info
            if self._user.info:
                self.info = self._user.info
            else:
                self.info = 'No Info'
            #Persist Info
            if self._user.name:
                self.name = self._user.name
            else:
                self.name = 'Blank Guy'

            #Free From Session
            sesh.expunge( self._user )

        user_info = ListAdapter(data=self.info.split('\n'),\
                                cls = Label)

        #Define Layout
        self._layout = BoxLayout( orientation = 'vertical' )
        self._name = Label( text = self.name.upper(), \
                            font_name= os.path.join(EXP_PATH,'hotel_font.ttf'),
                            valign = 'bottom', size_hint = (1,0.15),
                            font_size=38, bold=True,)
        self._image = RoundedImage( source = self.imageLocation)
                                    #allow_stretch=True)
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

    @property
    def imageLocation(self):
        imgloc = os.path.join(EXP_PATH,'user_images')
        print imgloc
        detpath = self._image_url.replace(HOME_URL,imgloc)
        #detpath = detpath.replace('/','\\')
        return detpath.split('?',1)[0]


class SwipingWidget(Widget):

    canidates = ListProperty()

    def __init__(self, app):
        super(SwipingWidget,self).__init__()
        self.app = app

        self.swiper = Carousel(direction='right')
        #with session_scope() as sesh:
        #    count = sesh.query( User ).count()
        #
        #Get Users From Server
        self.canidates = []
        for user_json in self.app.local_users:
            self.canidates.append(user_json)
            profile = Profile(user_json)
            self.swiper.add_widget(profile)

        self.add_widget(self.swiper)
        self.bind(pos= self.update_rect,
                  size = self.update_rect)

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
            with session_scope() as sesh:
                count = sesh.query( User ).count()

            for ct in range(count):
                profile = Profile(user_id = ct + 1)
                swiper.add_widget(profile)

            from kivy.core.window import Window
            Window.size = (iphone['width'],iphone['height'])

            return swiper

    #setWindow(**iphone)
    profileApp = ProfilesApp()
    profileApp.run()