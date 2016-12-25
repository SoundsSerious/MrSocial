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
from email_auth import *

sys.path.append(r'C:\Users\Sup\Dropbox\workspace\Exposure\app')
log.startLogging(sys.stdout)


def main():
    factory = ReconnectingPBClientFactory()
    reactor.connectTCP("localhost", 8800, factory)
    #def1 = factory.login(credentials.UsernamePassword("user1", "pass1"))
    def1 = factory.login(EmailAuth('kevin.russe11.0100@gmail.com'))

    def waitCalls(d):
        d.addCallback(printUserId)
        d.addCallback(printFriendId)
    reactor.callLater(0.5,waitCalls, def1)

    reactor.run()

def printResponse(value):
    print 'got {}'.format(value)

def printUserId(perspective):
    print "got perspective1 ref:", perspective
    print "asking it to foo(13)"
    d = perspective.callRemote("user_id")
    d.addCallback(printResponse)
    return perspective

def printFriendId(perspective):
    print perspective
    d = perspective.callRemote("friend_ids")
    d.addCallback(printResponse)
    return perspective
main()