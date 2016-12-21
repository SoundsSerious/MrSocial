# -*- coding: utf-8 -*-
"""
Created on Tue Dec  6 19:03:09 2016

@author: Cabin
"""

from kivy.support import install_twisted_reactor
install_twisted_reactor()

from zope.interface import implements, implementer, Interface

from twisted.internet import reactor
from twisted.protocols import basic
from twisted.cred import credentials
from twisted.internet.protocol import Protocol, ReconnectingClientFactory

from interfaces import *

@implementer(IEmailStorage)
class EmailAuth(object):

    def __init__(self, email):
        self.email = email


class Social_Client(basic.LineReceiver):

    app = None

    def __init__(self,factory):
        self.factory = factory

    @property
    def app(self):
        return self.factory.app

    def attemptConnection(self, email):
        self.sendLine( 'AUTH: {}'.format(email) )

    def connectionMade(self):
        self.factory.app.on_connect(self)

    def lineReceived(self,line):
        print line
        if line.startswith('AUTH:'):
            authArg = line.replace('AUTH:','').split(',')[0].strip()
            print authArg
            if authArg == 'SUCCESS':
                self.factory.app.authenticated = True
            elif authArg == 'BAD_EMAIL:':
                pass

class Social_ClientFactory(ReconnectingClientFactory):

    app = None

    protocol = Social_Client

    def __init__(self, app):
        self.app = app

    def startedConnecting(self, connector):
        print 'started connecitng!'

    def buildProtocol(self, addr):
        self.resetDelay()
        p = self.protocol(self)
        self.app.connection = p
        return p

    def clientConnectionLost(self, connector, reason):
        print 'lost connection',reason
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print 'failed connection',reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector,reason)
