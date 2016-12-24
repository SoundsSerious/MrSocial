# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 20:07:18 2016

@author: Sup
"""

from twisted.spread import pb
from twisted.internet import reactor, defer
from twisted.python import util
from twisted.python import log
import sys
from pb_interface import *
from twisted.cred import credentials

sys.path.append(r'C:\Users\Sup\Dropbox\workspace\Exposure\app')
log.startLogging(sys.stdout)


def main():
    factory = ReconnectingPBClientFactory()
    reactor.connectTCP("localhost", 8800, factory)
    def1 = factory.login(credentials.UsernamePassword("user1", "pass1"))
    def1.addCallback(connected)
    reactor.run()

def connected(perspective):
    print "got perspective1 ref:", perspective
    print "asking it to foo(13)"
    perspective.callRemote("foo", 13)

main()