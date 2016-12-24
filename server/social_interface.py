# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 12:22:08 2016

@author: Sup
"""

#!/usr/bin/env python

import zope

from zope.interface import implements, implementer, Interface
from twisted.cred import portal, checkers, credentials, error as credError
from twisted.internet import defer, reactor, protocol, threads
from twisted.protocols import basic

from twisted.cred.portal import IRealm

from email_auth import *
from model import *
from interfaces import *

LAT,LONG = 26.7153, -80.053

class Social_Server(basic.LineReceiver):
    '''In Which We Communicate With The User'''

    _authenticated = False
    portal = None
    avatar = None

    def __init__(self, portal):
        self.portal = portal

    def connectionMade(self):
        self.sendLine('Welcome To Email Auth')

    def authenticate(self, email):
        d = defer.maybeDeferred(self.registerEmail, email)
        d.addCallback(self._cbAuth, email)
        d.addErrback(self._cbAuthFail)
        return d

    def _cbAuth(self, ial, error):
        interface, avatar, logout = ial
        self.sendLine('AUTH:SUCCESS, {}'.format(avatar.user))
        self._authenticated = True

    def _cbAuthFail(self, error):
        r = error.trap(credError.UnhandledCredentials)
        if r == credError.UnhandledCredentials:
            self.sendLine('AUTH:BAD_EMAIL')

    def registerEmail(self, email):
        if self.portal is not None:
            self.avatar = self.portal.login(EmailAuth(email),None,IEmailStorage)
            return self.avatar
        raise credError.UnauthorizedLogin()

    def echo(self,line):
        print line
        self.sendLine('AUTH\'d:'+line)

    def lineReceived(self, line):
        print line
        if self._authenticated:
            #Check Other Protocols
            self.echo(line)
        else: #Wait For Auth Attempt
            if line.startswith('AUTH:'):
                email = line.replace('AUTH:','').strip()
                print 'Got Email: {}'.format(email)
                self.authenticate( email )

@implementer(ISocial)
class Social_Interface(ITwistedData):

    _user_id = None
    _user_obj = None
    _friends = None
    _projects = None

    def __init__(self,userId):
        self._user_id = userId
        reactor.callLater(0, self.db_assignSelfFromDatabase)
        reactor.callLater(0, self.db_get_friends)

    @ITwistedData.sqlalchemy_method
    def db_assignSelfFromDatabase(self,session):
        user = session.query(User).filter(User.email == self._user_id).first()
        if user:
            if user.locations:
                loc = user.current_location
                print 'user at {}'.format(loc.pt_txt)
            if user.user_mode < SECURITY_MODES['uninitalized']:
                session.expunge(user)
                self.user = user.id
            else:
                print 'user not initalized'
            reactor.callLater(0,self.user.print_info)

    @ITwistedData.sqlalchemy_method
    def db_get_friends(self, session):
        '''Get Local Users Via GEO information'''
        if self.user:
            user = session.query(User.id == self.user.id)
            for friend in user.all_friends:
                print friend.name

    @ITwistedData.sqlalchemy_method
    def db_get_nearby(self,session, distance = 10):
        user = session.query(User).filter(User.id == self.user).first()
        if user:
            loc = user.current_location
            nearby = loc.get_usersid_within(distance) #miles
            if nearby:
                pepes = session.query(User).filter(User).filter(User.id.in_(nearby) ).all()
                return [user.asjson for user in pepes]


    @ITwistedData.sqlalchemy_method
    def db_update(self, session):
        '''Updates User Interface Attributes (...From Database)'''
        pass

    @property
    def user(self):
        return self._user_obj

    @user.setter
    def user(self, user_pk):
        '''On User Assignment Update'''
        self._user_obj = user_pk
        self.db_update()

    @property
    def friends(self):
        return self._friends

    @property
    def projects(self):
        return self._projects

    def get_friends(self):
        '''Return Friend Objects Associated With The User'''
        pass

    def get_projects(self):
        '''Return Projects Objects Associated With The User'''
        pass



    def logout(self):
        '''Logs The User Out'''
        print '|{:<30}| Loging Out...'.format(self.user)
        pass



class Social_AppRealm(object):
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *cred_interfaces):
        if IEmailStorage in cred_interfaces:
            avatar = Social_Interface(avatarId)
            return IEmailStorage, avatar, avatar.logout
        else:
            raise NotImplementedError("no interface")

class Social_Factory(object,protocol.Factory):

    protocol = Social_Server

    def __init__(self, portal):
        self.portal = portal

    def buildProtocol(self, addr):
        p = self.protocol(self.portal)
        p.factory = self
        return p

class Social_Component(Social_Factory):

    def __init__(self):
        self.realm = Social_AppRealm()
        self.checker = EmailChecker()
        self.portal = portal.Portal(self.realm , [self.checker])
        super(Social_Component,self).__init__(self.portal)

if __name__ == "__main__":
    print 'Running'
    realm = Social_AppRealm()

    checker = EmailChecker()
    p = portal.Portal(realm, [checker])

    reactor.listenTCP(SOCIAL_PORT, Social_Factory(p) )
    reactor.run()