from typing import Union, List
from logging import getLogger
import threading

from datetime import datetime

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig

from nl.oppleo.models.User import User
from nl.oppleo.models.WebAuthNCredentialModel import WebAuthNCredentialModel

from webauthn import generate_registration_options, generate_authentication_options
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    PublicKeyCredentialCreationOptions,
    RegistrationCredential,
    PublicKeyCredentialRequestOptions,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    AuthenticationCredential,
    PublicKeyCredentialRequestOptions
)
from webauthn.helpers import (
    generate_challenge, 
    bytes_to_base64url, 
    base64url_to_bytes, 
    byteslike_to_bytes, 
    parse_client_data_json, 
    parse_registration_credential_json, 
    decode_credential_public_key
)


oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()

OPTIONS_VALIDATION_IN_MINUTES:int = 15

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class StoredCredentialCreationOptions(object):

    __logger = None
    publicKeyCredentialCreationOptions:Union[PublicKeyCredentialCreationOptions, None] = None
    user:Union[User, None] = None
    created:datetime = datetime.now()

    def __init__(self, publicKeyCredentialCreationOptions:Union[PublicKeyCredentialCreationOptions, None]=None, user:Union[User, None]=None):
        self.__logger = getLogger(self.__class__.__module__)
        self.__logger.debug('Initializing StoredCredentialCreationOptions...')

        if publicKeyCredentialCreationOptions is None:
            raise ValueError("publicKeyCredentialCreationOptions missing (None)") 
        if user is None:
            raise ValueError("user missing (None)") 

        self.publicKeyCredentialCreationOptions = publicKeyCredentialCreationOptions
        self.user = user
        self.created = datetime.now()


class StoredCredentialRequestOptions(object):

    __logger = None
    publicKeyCredentialRequestOptions:Union[PublicKeyCredentialRequestOptions, None] = None
    username:Union[str, None] = None
    created:datetime = datetime.now()

    def __init__(self, publicKeyCredentialRequestOptions:Union[PublicKeyCredentialRequestOptions, None]=None, username:Union[str, None]=None):
        self.__logger = getLogger(self.__class__.__module__)
        self.__logger.debug('Initializing StoredCredentialRequestOptions...')

        if publicKeyCredentialRequestOptions is None:
            raise ValueError("publicKeyCredentialRequestOptions missing (None)") 
        if username is None:
            self.__logger.debug('Username None - probably trying discoverable.')

        self.publicKeyCredentialRequestOptions = publicKeyCredentialRequestOptions
        self.username = username
        self.created = datetime.now()



class WebAuthNCredentialOptionsStore(object, metaclass=Singleton):

    __logger = None
    __threadLock = None
 
    __storedCredentialsCreationOptions:List = []
    __storedCredentialsRequestOptions:List = []

    def __init__(self):
        self.__logger = getLogger(self.__class__.__module__)
        self.__logger.debug('Initializing WebAuthNCredentialOptionsStore...')
        self.__threadLock = threading.Lock()


    def generate_registration_options(self, 
                                      relyingPartyId:Union[str, None]=None, 
                                      user:Union[User, None]=None) -> PublicKeyCredentialCreationOptions:
        global oppleoConfig

        if user is None:
            self.__logger.debug('generate_registration_options called with no User (None)...')
            raise ValueError("user missing (None)") 

        publicKeyCredentialCreationOptions:PublicKeyCredentialCreationOptions = generate_registration_options(
                rp_name     = oppleoConfig.chargerNameText,
                rp_id       = str(relyingPartyId),
                # Random number linked to the user
                # user_id     = bytes(webAuthUserID, 'utf-8'),
                user_id     = user.webAuthUserIDBytes,
                user_name   = str(user.username),
                # Require the user to verify their identity to the authenticator
                authenticator_selection = AuthenticatorSelectionCriteria(
                    user_verification       = UserVerificationRequirement.REQUIRED,
                    # Make the key discoverable (and stored on Yubikey)
                    # https://developers.yubico.com/WebAuthn/WebAuthn_Developer_Guide/Resident_Keys.html
                    resident_key            = ResidentKeyRequirement.PREFERRED,
                ),
                exclude_credentials = WebAuthNCredentialModel.getRegisteredCredentials(credential_owner=user.username)
            )
        
        self.__storedCredentialsCreationOptions.append(
            StoredCredentialCreationOptions(
                publicKeyCredentialCreationOptions=publicKeyCredentialCreationOptions,
                user=user
            )
        )

        return publicKeyCredentialCreationOptions


    def generate_authentication_options(self, 
                                        relyingPartyId:Union[str, None]=None, 
                                        username:Union[str, None]=None) -> PublicKeyCredentialRequestOptions:
        global oppleoConfig

        allow_credentials = []
        if username is not None:
            allow_credentials = WebAuthNCredentialModel.getRegisteredCredentials(credential_owner=username)

        publicKeyCredentialRequestOptions:PublicKeyCredentialRequestOptions = generate_authentication_options(
            rp_id = str(relyingPartyId),
            allow_credentials=allow_credentials,
            user_verification=UserVerificationRequirement.REQUIRED,
        )

        self.__storedCredentialsRequestOptions.append(
            StoredCredentialRequestOptions(
                publicKeyCredentialRequestOptions=publicKeyCredentialRequestOptions,
                username=username
            )
        )

        return publicKeyCredentialRequestOptions


    def retrieve_valid_registration_challenge(self,
                                    registrationCredential:Union[RegistrationCredential, None]=None,
                                    user:Union[User, None]=None
                                ) -> Union[bytes, None]:

        if user is None:
            self.__logger.debug('generate_registration_options called with no User (None)...')
            raise ValueError("user missing (None)") 

        if registrationCredential is None:
            self.__logger.debug('generate_registration_options called with no registrationCredential (None)...')
            raise ValueError("registrationCredential missing (None)") 

        submittedChallenge = parse_client_data_json(registrationCredential.response.client_data_json).challenge.decode("utf-8")

        # Remove expired options
        self.__remove_expired()
        # Find the stored credential options (determine if the challenge was issued)
        for storedCredentialsCreationOptions in self.__storedCredentialsCreationOptions:
            # Recognize 
            issuedChallenge = bytes_to_base64url(storedCredentialsCreationOptions.publicKeyCredentialCreationOptions.challenge)
            # Challenge found?
            if (submittedChallenge == issuedChallenge):
                self.__logger.debug('challenge found and valid')
                return bytes(bytes_to_base64url(storedCredentialsCreationOptions.publicKeyCredentialCreationOptions.challenge), 'utf-8')
        # If none found, return None
        self.__logger.debug('Challenge not found (possibly expired)')


    """
        returns a tuple[ bytes, WebAuthNCredentialModel ]
    """
    def retrieve_valid_authentication_challenge(self,
                                    authenticationCredential:Union[AuthenticationCredential, None]=None,
                                    username:Union[str, None]=None
                                ):

        if authenticationCredential is None:
            self.__logger.debug('generate_registration_options called with no authenticationCredential (None)...')
            raise ValueError("authenticationCredential missing (None)") 

        submittedChallenge = parse_client_data_json(authenticationCredential.response.client_data_json).challenge.decode("utf-8")
        issuedChallenge:Union[bytes, None] = None
        # Remove expired options
        self.__remove_expired()
        # Find the stored credential options (determine if the challenge was issued)
        for storedCredentialsRequestOptions in self.__storedCredentialsRequestOptions:
            # Recognize 
            requestChallenge = bytes_to_base64url(storedCredentialsRequestOptions.publicKeyCredentialRequestOptions.challenge)
            # Challenge found?
            if (submittedChallenge == requestChallenge):
                self.__logger.debug('Challenge found and valid')
                issuedChallenge = bytes(bytes_to_base64url(storedCredentialsRequestOptions.publicKeyCredentialRequestOptions.challenge), 'utf-8')
        
        if issuedChallenge is None:
            # If none found, return None
            self.__logger.debug('Challenge not found (possibly expired)')
            raise KeyError("Challenge not found") 

        registeredCredential = WebAuthNCredentialModel.getRegisteredCredential(credential_id=authenticationCredential.id, username=username)
        return issuedChallenge, registeredCredential


    def invalidate(self, challenge:Union[bytes, None]=None):
        self.__logger.debug('invalidate()')

        if challenge is None:
            self.__logger.debug('invalidate called with no challenge (None)...')
            raise ValueError("challenge missing (None)") 

        # Remove expired options
        self.__remove_expired()

        # Remove used option
        with self.__threadLock:
            self.__storedCredentialsCreationOptions = [
                    storedCredentialsCreationOptions 
                        for storedCredentialsCreationOptions in self.__storedCredentialsCreationOptions if not bytes_to_base64url(storedCredentialsCreationOptions.publicKeyCredentialCreationOptions.challenge) == challenge
                ]
            self.__storedCredentialsRequestOptions = [
                    storedCredentialRequestOptions 
                        for storedCredentialRequestOptions in self.__storedCredentialsRequestOptions if not bytes_to_base64url(storedCredentialRequestOptions.publicKeyCredentialRequestOptions.challenge) == challenge
                ]


    def __remove_expired(self):
        self.__logger.debug('__remove_expired')

        with self.__threadLock:
            self.__storedCredentialsCreationOptions = [
                    storedCredentialsCreationOptions 
                        for storedCredentialsCreationOptions in self.__storedCredentialsCreationOptions if not self.__is_expired_c(storedCredentialsCreationOptions)
                ]
            self.__storedCredentialsRequestOptions = [
                    storedCredentialRequestOptions 
                        for storedCredentialRequestOptions in self.__storedCredentialsRequestOptions if not self.__is_expired_r(storedCredentialRequestOptions)
                ]
            
    def __is_expired_c(self, storedCredentialCreationOptions:Union[StoredCredentialCreationOptions, None]=None) -> bool:
        if storedCredentialCreationOptions is None or storedCredentialCreationOptions.created is None:
            return False
        return (int((datetime.now() - storedCredentialCreationOptions.created).total_seconds() / 60.0) > OPTIONS_VALIDATION_IN_MINUTES)

    def __is_expired_r(self, storedCredentialRequestOptions:Union[StoredCredentialRequestOptions, None]=None) -> bool:
        if storedCredentialRequestOptions is None or storedCredentialRequestOptions.created is None:
            return False
        return (int((datetime.now() - storedCredentialRequestOptions.created).total_seconds() / 60.0) > OPTIONS_VALIDATION_IN_MINUTES)


