# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 12:22:08 2016

@author: Sup
"""

#!/usr/bin/env python

import zope

from zope.interface import implements, implementer, Interface

from twisted.internet import defer, reactor, protocol, threads
from twisted.protocols import basic
from twisted.python.components import registerAdapter
from twisted.cred.portal import Portal
from twisted.cred import checkers, portal
from twisted.cred.portal import IRealm
from twisted.cred import portal, checkers, credentials, error as credError
from twisted.cred.credentials import IUsernameHashedPassword, Anonymous
from twisted.spread.pb import *
from twisted.spread.interfaces import IJellyable, IUnjellyable
from twisted.spread.jelly import jelly, unjelly, globalSecurity

from email_auth import *
from model import *
from interfaces import *

LAT,LONG = 26.7153, -80.053

from twisted.spread import pb
from twisted.internet import reactor

@implementer(ISocial)
class Social_Interface(Avatar):

    _user_obj = None
    _friends = None
    _projects = None

    def __init__(self,userEmail):
        if userEmail:
            self.initialize( userEmail )
        elif userEmail == False:
            #Public Interface
            pass

    def initialize(self, email):
        d = defer.maybeDeferred(self.db_assignSelfFromDatabase, email)
        return d

    def perspective_friend_ids(self):
        print 'getting friend ids'
        if self.user:
            d = defer.maybeDeferred(self.db_get_friends_ids)
            return d
        else:
            return None

    def perspective_user_id(self):
        print 'perspective id'
        if self.user:
            print 'getting user id {}'.format(self.user.id)
            return self.user.email
        else:
            return None

    @ITwistedData.sqlalchemy_method
    def db_assignSelfFromDatabase(self,session, userEmail):
        user = session.query(User).filter(User.email == userEmail).first()
        if user:
            print 'got user {}'.format(user.email)
            if user.locations:
                loc = user.current_location
                print 'user at {}'.format(loc.pt_txt)
            if user.user_mode < SECURITY_MODES['uninitalized']:
                session.expunge(user)
                self.user = user
                reactor.callLater(0,self.user.print_info)
            else:
                print 'user not initalized'


    @ITwistedData.sqlalchemy_method
    def db_get_friends_ids(self, session):
        '''Get Local Users Via GEO information'''
        if self.user:
            user = session.query(User).filter(User.id == self.user.id).first()
            friends = user.all_friends
            return list([friend.id for friend in friends])

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
    def user(self, userObj):
        '''On User Assignment Update'''
        self._user_obj = userObj
        reactor.callLater(self.db_update)

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

class PBSocialServerFactory(protocol.ServerFactory):
    """
    Server factory for perspective broker.

    Login is done using a Portal object, whose realm is expected to return
    avatars implementing IPerspective. The credential checkers in the portal
    should accept IUsernameHashedPassword or IUsernameMD5Password.

    Alternatively, any object providing or adaptable to L{IPBRoot} can be
    used instead of a portal to provide the root object of the PB server.
    """

    unsafeTracebacks = False

    # object broker factory
    protocol = Broker

    def __init__(self, root, unsafeTracebacks=False, security=globalSecurity):
        """
        @param root: factory providing the root Referenceable used by the broker.
        @type root: object providing or adaptable to L{IPBRoot}.

        @param unsafeTracebacks: if set, tracebacks for exceptions will be sent
            over the wire.
        @type unsafeTracebacks: C{bool}

        @param security: security options used by the broker, default to
            C{globalSecurity}.
        @type security: L{twisted.spread.jelly.SecurityOptions}
        """
        self.root = SocialRoot(root)
        self.unsafeTracebacks = unsafeTracebacks
        self.security = security


    def buildProtocol(self, addr):
        """
        Return a Broker attached to the factory (as the service provider).
        """
        proto = self.protocol(isClient=False, security=self.security)
        proto.factory = self
        proto.setNameForLocal("root", self.root.rootObject(proto))
        return proto

    def clientConnectionMade(self, protocol):
        # XXX does this method make any sense?
        pass

class Social_AppRealm(object):
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IPerspective not in interfaces:
            raise NotImplementedError("no interface")
        else:
            #EmailStorage returns cred, Others Return A Username Or Something
            if IEmailStorage in interfaces:
                avatar = Social_Interface(avatarId)
                return IPerspective, avatar, avatar.logout
            else:
                avatar = Social_Interface(False)#Public Interface Call
                return IPerspective, avatar, avatar.logout

@implementer(IPBRoot)
class SocialRoot:
    """Root object, used to login to portal."""

    def __init__(self, portal):
        self.portal = portal

    def rootObject(self, broker):
        return SocialPortalWrapper(self.portal, broker)


class _JellyableAvatarMixin:
    """
    Helper class for code which deals with avatars which PB must be capable of
    sending to a peer.
    """
    def _cbLogin(self, (interface, avatar, logout)):
        """
        Ensure that the avatar to be returned to the client is jellyable and
        set up disconnection notification to call the realm's logout object.
        """
        print 'logging in {}'.format(avatar)
        if not IJellyable.providedBy(avatar):
            avatar = AsReferenceable(avatar, "perspective")

        puid = avatar.processUniqueID()

        # only call logout once, whether the connection is dropped (disconnect)
        # or a logout occurs (cleanup), and be careful to drop the reference to
        # it in either case
        logout = [ logout ]
        def maybeLogout():
            if not logout:
                return
            fn = logout[0]
            del logout[0]
            fn()
        self.broker._localCleanup[puid] = maybeLogout
        self.broker.notifyOnDisconnect(maybeLogout)

        return avatar



class SocialPortalWrapper(Referenceable, _JellyableAvatarMixin):
    """
    Root Referenceable object, used to login to portal.
    """

    def __init__(self, portal, broker):
        self.portal = portal
        self.broker = broker


    def remote_login(self, username):
        """
        Start of username/password login.
        """
        c = challenge()
        return c, _PortalAuthChallenger(self.portal, self.broker, username, c)


    def remote_loginAnonymous(self, mind):
        """
        Attempt an anonymous login.

        @param mind: An object to use as the mind parameter to the portal login
            call (possibly None).

        @rtype: L{Deferred}
        @return: A Deferred which will be called back with an avatar when login
            succeeds or which will be errbacked if login fails somehow.
        """
        d = self.portal.login(Anonymous(), mind, IPerspective)
        d.addCallback(self._cbLogin)
        return d

    def remote_loginEmail(self, email, client):
        print 'client: {}'.format(client)
        print 'remote email {}'.format( email )
        d = self.portal.login( EmailAuth(email), client, IPerspective, IEmailStorage)
        d.addCallback(self._cbLogin)
        return d

if __name__ == "__main__":


    emailChecker = EmailChecker()
    dummyUserChecker = checkers.InMemoryUsernamePasswordDatabaseDontUse(user1="pass1",
                                                                        user2="pass2")
    p = portal.Portal(Social_AppRealm(),[emailChecker,dummyUserChecker])

    reactor.listenTCP(8800, PBSocialServerFactory(p))
    reactor.run()