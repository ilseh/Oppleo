"""
https://hackernoon.com/implementing-2fa-how-time-based-one-time-password-actually-works-with-python-examples-cm1m3ywt
"""
import secrets
import base64

"""
    Generating the shared secret key

    The TOTP algorithm is defined on the IETF RFC 6238, where it says the shared key "should be chosen at random or using a 
    cryptographically strong pseudorandom generator properly seeded with a random value". This key must be encrypted to be 
    securely stored and should be decrypted only on two occasions: when validating a password that comes in and when exposing 
    itself to be copied by another device, that should keep it encrypted too. To generate it, we can use Python's secrets.
    Table 3: The Base 32 Alphabet

        Value Encoding  Value Encoding  Value Encoding  Value Encoding
            0 A             9 J            18 S            27 3
            1 B            10 K            19 T            28 4
            2 C            11 L            20 U            29 5
            3 D            12 M            21 V            30 6
            4 E            13 N            22 W            31 7
            5 F            14 O            23 X
            6 G            15 P            24 Y         (pad) =
            7 H            16 Q            25 Z
            8 I            17 R            26 2

https://stackoverflow.com/questions/50082075/totp-base32-vs-base64
The private key in TOTP should be a 20-byte (160-bit) secret.
""" 
def base32Encode(totpSecret:bytes):
    return base64.b32encode(totpSecret).decode('utf-8')

def base32Decode(totpBase32:str):
    return base64.b32decode(totpBase32)

def generateTotpSharedSecret() -> str:
    sharedSecret = secrets.token_bytes(nbytes=20)

    base32Token = base32Encode(sharedSecret)
    # if no padding return
    if '=' not in base32Token:
        return base32Token
    # if padding return try again (padding can cause issues)
    return generateTotpSharedSecret()


"""
    We could just return the HMAC hash, but the output is way too long for the user to type (even more when there are only 
    30 seconds to do this). For this reason, we use the dynamic truncation algorithm to get a sample of it, usually of six digits. 
    It was developed for the predecessor of TOTP, at RFC 4226 and consists of four steps:
        1. Convert the hash (base 16) into a binary string (base 2)
        2. Get the last four bits as an integer (base 10)
        3. Use this integer as an offset and get the next 32 bits of the binary string
        4. Convert this 32 bits to integer and get the last X digits, where X is the length you want to use
"""


"""
    It takes a Base32-encoded secret key and a counter as input. It returns a 6-digit HOTP value as output.
    https://github.com/susam/mintotp
""" 
import hmac
import struct
import time

def getHotp(shared_secret, counter, digits=6, digest='sha1') -> str:
    key = base64.b32decode(shared_secret.upper() + '=' * ((8 - len(shared_secret)) % 8))
    counter = struct.pack('>Q', counter)
    mac = hmac.new(key, counter, digest).digest()
    offset = mac[-1] & 0x0f
    binary = struct.unpack('>L', mac[offset:offset+4])[0] & 0x7fffffff
    return str(binary)[-digits:].zfill(digits)

def getTotp(shared_secret, time_step=30, digits=6, digest='sha1') -> str:
    return getHotp(shared_secret, int(time.time() / time_step), digits, digest)

def validateTotp(totp, shared_secret, time_step=30, digits=6, digest='sha1') -> bool:
    return totp == getTotp(shared_secret, time_step, digits, digest)


"""
    https://pypi.org/project/qrcode/
    https://stackoverflow.com/questions/34520928/how-to-generate-a-qr-code-for-google-authenticator-that-correctly-shows-issuer-d

    Secret keys may be encoded in QR codes as a URI with the following format:

        otpauth://TYPE/LABEL?PARAMETERS

    example:
        otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&issuer=Example

    Types:  Valid types are hotp and totp, to distinguish whether the key will be used for counter-based HOTP or for TOTP.
    Label:  The label is used to identify which account a key is associated with. It contains an account name, which is a URI-encoded 
            string, optionally prefixed by an issuer string identifying the provider or service managing that account. This issuer 
            prefix can be used to prevent collisions between different accounts with different providers that might be identified using 
            the same account name, e.g. the user's email address.
            The issuer prefix and account name should be separated by a literal or url-encoded colon, and optional spaces may precede 
            the account name. Neither issuer nor account name may themselves contain a colon. Represented in ABNF according to RFC 5234:
                label = accountname / issuer (“:” / “%3A”) *”%20” accountname
            Valid values might include Example:alice@gmail.com, Provider1:Alice%20Smith or Big%20Corporation%3A%20alice%40bigco.com.
            We recommend using both an issuer label prefix and an issuer parameter, described below.
    Secret: The secret parameter is an arbitrary key value encoded in Base32 according to RFC 3548. The padding specified in RFC 3548 
            section 2.2 is not required and should be omitted. REQUIRED
    Issuer: The issuer parameter is a string value indicating the provider or service this account is associated with, URL-encoded 
            according to RFC 3986. If the issuer parameter is absent, issuer information may be taken from the issuer prefix of the 
            label. If both issuer parameter and issuer label prefix are present, they should be equal. STRONGLY RECOMMENDED
    Algorithm: The algorithm may have the values: 
                SHA1 (Default)
                SHA256
                SHA512
            Currently, the algorithm parameter is ignored by the Google Authenticator implementations. OPTIONAL
    Digits: The digits parameter may have the values 6 or 8, and determines how long of a one-time passcode to display to the user. 
            The default is 6.
    Counter: if type is hotp: The counter parameter is required when provisioning a key for use with HOTP. It will set the initial 
            counter value.
    Period: only if type is totp: The period parameter defines a period that a TOTP code will be valid for, in seconds. The default 
            value is 30.

Valid values corresponding to the label prefix examples above would be: issuer=Example, issuer=Provider1, and issuer=Big%20Corporation.

Older Google Authenticator implementations ignore the issuer parameter and rely upon the issuer label prefix to disambiguate accounts. Newer implementations will use the issuer parameter for internal disambiguation, it will not be displayed to the user. We recommend using both issuer label prefix and issuer parameter together to safely support both old and new Google Authenticator versions.
"""
import qrcode
from urllib import parse

def keyUri(type:str='totp',
           label:str=None, 
           secret:str=None,
           issuer:str=None,
           accountname:str=None,
           algorithm:str=None,
           digits:int=6,
           counter:int=0,
           period:int=30):
    if not isinstance(type, str):
        return None
    type = type.lower()

    if type == 'hotp':
        uri = 'otpauth://hotp/'
    else:
        # Default
        type = 'totp'
        uri = 'otpauth://totp/'
    if label is None:
        if accountname is None:
            # Need at least a label or accountname
            return None
        # Use issuer optionally with account name
        if issuer is None:
            # Use the accountname as label
            uri = uri + parse.quote(accountname, safe='')
        else: 
            # Use issuer as prefix with account name (with encoded :)
            uri = uri + parse.quote(issuer + ':' + accountname, safe='')
    else:
        # Use the label provided. URI encode label
        uri = uri + parse.quote(label, safe='')

    if secret is None:
        # Required
        return None
    uri = uri + '?' + 'secret=' + secret

    if issuer is not None:
        # Optional
        uri = uri + '&' + 'issuer=' + parse.quote(issuer, safe='')

    # TODO For now the algorithm parameter is ignored

    if digits is not None and isinstance(digits, int):
        # Optional
        uri = uri + '&' + 'digits=' + str(digits)

    if (counter is None or not isinstance(counter, int)) and type == 'hotp':
        # Counter required for hotp
        return None        
    if counter is not None and isinstance(counter, int) and type == 'hotp':
        # Optional
        uri = uri + '&' + 'counter=' + str(counter)

    if period is not None and isinstance(period, int) and type == 'totp':
        # Optional, only for totp
        uri = uri + '&' + 'period=' + str(period)

    return uri

def makeQR(data:str=None, fill_color:str="black", back_color:str="white"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    return img

""" 
    Encrypt/ decrypt the secret for storage in a database
    https://gist.github.com/XD-DENG/07c733e6555a10c01762
"""
from Crypto.Cipher import AES
from Crypto import Random
import hashlib

def pad(s):
    return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)

def unpad(s):
    return s[:-ord(s[len(s)-1:])]

def encryptAES(key:str=None, plainData:str=None):
    if key is None or plainData is None:
        return None
    paddedPlainData = pad(plainData)
    iv = Random.new().read(AES.block_size)
    KeyBytes:bytes = hashlib.sha256(key.encode()).digest()
    cipher = AES.new(KeyBytes, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(paddedPlainData.encode())).decode('utf-8')

def decryptAES(key:str=None, encData:str=None):
    if key is None or encData is None:
        return None
    b64EncData = base64.b64decode(encData)
    iv = b64EncData[:AES.block_size]
    KeyBytes:bytes = hashlib.sha256(key.encode()).digest()
    cipher = AES.new(KeyBytes, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(b64EncData[AES.block_size:])).decode('utf-8')


"""
TODO add 
    pip install Pillow
    pip install qrcode
    not -> pip install Crypto
        "no module named Crypto" Exception
    pip install pycryptodome
"""
