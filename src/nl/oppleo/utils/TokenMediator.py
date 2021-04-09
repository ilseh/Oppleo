import logging
import threading
import time
import os
from base64 import b64encode

"""
When using a token based api, the token has to be refreshed at some point. In a multi-threaded environment the token can be in use
in multiple locations. When the refresh happens the use can be denied at any point.
To regulate the token use and refresh this mediator class is used.

The token mediator singleton is instantiated in this file. include the instantiated object (tokenMediator) for direct use.

Checkout
--------
Checkout any token, including the Tesla security tokens. If checkout fails, check if the token is still valid using the validate()
function. If the token is invalid, reread the object from the database.

Refresh
-------
Checkout a token. Check if refresh is required, and refresh it if needed. Register (checkout) the refreshed token and invalidate the 
old token. After use 

checkout(token)
 -> return Key string: access granted, now in use
 -> return None: access denied (already in use or not valid)

release(token, key)
 -> return True: token was registered and the key matches, token is released for use.
 -> return False: token is unknown or not in use

validate(token)
 -> return True: unknown token, or registered and not invalidated
 -> return False: invalidated token, obtain a new one through the regular means (reload object from database)

invalidate(token, key)
 -> return True: valid token now not valid anymore (key matches, token known and in use)
 -> return False: token not known, of key failed

"""

class TokenObj:
    code = None
    inUse:bool = False
    valid:bool = True
    ref = None
    key = None

    def __init__(self, code, inUse:bool=False, ref=None, key=None, valid:bool=True):
        self.__logger = logging.getLogger('nl.oppleo.utils.TokenObj')
        self.code = code
        self.inUse = inUse
        self.valid = valid
        self.ref = ref
        self.key = key


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TokenMediator:
    __logger = None
    __lock = None
    __tokens = {}
    __KEY_SIZE = 24

    def __init__(self):
        self.__logger = logging.getLogger('nl.oppleo.utils.TokenMediator')
        self.__lock = threading.Lock()

    def generateKey(self):
        return b64encode(os.urandom(self.__KEY_SIZE)).decode('utf-8')

    """
        checkout(token)
        -> return Key string: access granted, now in use
        -> return None: access denied (already in use or not valid)
    """ 
    # TODO add timeout
    def checkout(self, token, ref=None, wait=False) -> str | None:
        while True:
            with self.__lock:
                if token not in self.__tokens:
                    self.__tokens[token] = TokenObj(code=token, ref=ref, inUse=True, key=self.generateKey(), valid=True)
                    return self.__tokens[token].key
                if not self.__tokens[token].valid:
                    # Not valid
                    self.__logger.debug('Checkout reequest for invalid token (token={}, ref={})'.format(token, ref))
                    return None 
                if self.__tokens[token].inUse:
                    if not wait:
                        return None
                else:
                    self.__tokens[token].inUse = True
                    return None
            time.sleep(.1)

    """
        release(token, key)
        -> return True: token was registered and the key matches, token is released for use.
        -> return False: token is unknown or not in use
        NOTE: doesnot check for invalid token
    """ 
    def release(self, token, key) -> bool:
        with self.__lock:
            if token not in self.__tokens:
                self.__logger.warn('Request to release unregistered token (token={}, key={})'.format(token, key))
                return False
            if self.__tokens[token].key != key:
                self.__logger.warn('Request to release token with invalid key (token={}, key={})'.format(token, key))
                return False
            self.__tokens[token].inUse = False
            self.__logger.debug('Token released (token={}, key={})'.format(token, key))
            return True

    """
        validate(token)
        -> return True: unknown token, or registered and not invalidated
        -> return False: invalidated token, obtain a new one through the regular means (reload object from database)
    """
    def validate(self, token):
        with self.__lock:
            if token not in self.__tokens:
                # Unknown
                self.__logger.debug('Validation request for unknown token (token={}, ref={})'.format(token))
                return False
            self.__logger.debug('Validation request for token (token={}, valid={})'.format(token, self.__tokens[token].valid))
            return self.__tokens[token].valid

    """
    invalidate(token, key)
     -> return True: valid token now not valid anymore (key matches, token known and in use)
    -> return False: token not known, of key failed
    """
    def invalidate(self, token, key):
        with self.__lock:
            if token not in self.__tokens:
                self.__logger.debug('Request to invalidate unregistered token (token={}, key={})'.format(token, key))
                return False
            if self.__tokens[token].key != key:
                self.__logger.debug('Request to invalidate token with invalid key (token={}, key={})'.format(token, key))
                return False
            self.__tokens[token].valid = False
            self.__tokens[token].inUse = False
            self.__logger.debug('Request to invalidate token with key (token={}, key={}) granted'.format(token, key))
            return True


tokenMediator = TokenMediator()
