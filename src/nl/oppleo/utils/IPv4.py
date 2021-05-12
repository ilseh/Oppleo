from re import sub
import socket # , struct

"""
https://stackoverflow.com/questions/819355/how-can-i-check-if-an-ip-is-in-a-network-in-python
"""

class IPv4():
    """
        return a mask of n bits as a long integer
    """
    @staticmethod
    def __makeMask__(n:int):
        return ((0x2 << n-1) -1 << 32-n)
    #    return (2L<<n-1) - 1

    @staticmethod
    def __numMaskFromSubnet__(subnet:str=None):
        if not IPv4.validSubnet( subnet ):
            return 4294967295   # /32 or 0xFFFFFFFF 
        return IPv4.__makeMask__( int(subnet.split("/")[1]) )

    """
        convert decimal dotted quad string to long integer
    """
    @staticmethod
    def __dottedQuadToNum__(ip):
        return int.from_bytes(socket.inet_aton(ip), byteorder='big', signed=False )
        # return struct.unpack('!I',socket.inet_aton(ip))[0]

    """
        Convert a network address to a long integer
    """
    @staticmethod
    def __networkMask__(ip, bits):
        return IPv4.__dottedQuadToNum__(ip) & IPv4.__makeMask__(bits)

    @staticmethod
    def __numFromSubnet__(subnet:str=None) -> int:
        return IPv4.__dottedQuadToNum__(subnet.split("/")[0]) & IPv4.__makeMask__(int(subnet.split("/")[1]))


    @staticmethod
    def __isIPByte__(s:str):
        try: return str(int(s)) == s and 0 <= int(s) <= 255
        except: return False

    @staticmethod
    def __isIPByte32__(s:str):
        try: return str(int(s)) == s and int(s) == 32
        except: return False

    @staticmethod
    def validIP(ip:str=None) -> bool:
        return (ip is not None and 
                ip.count(".") == 3 and 
                all(IPv4.__isIPByte__(i) for i in ip.split(".")))

    @staticmethod
    def validSubnet(subnet:str=None) -> bool:
        return (subnet is not None and 
                subnet.count("/") == 1 and 
                all( IPv4.__isIPByte__(i) for i in subnet.split("/")[0].split(".") ) and
                IPv4.__isIPByte__(subnet.split("/")[1])
                )

    @staticmethod
    def isSingleIP(subnetOrIP:str=None) -> bool:
        return (subnetOrIP is not None and 
                 ( ( subnetOrIP.count("/") == 0 and IPv4.validIP(subnetOrIP) ) or
                   ( subnetOrIP.count("/") == 1 and IPv4.validIP(subnetOrIP.split("/")[0]) and IPv4.__isIPByte32__(subnetOrIP.split("/")[1]) )
                 )
               )

    @staticmethod
    def remove32Subnet(subnetOrIP:str=None) -> str:
        return subnetOrIP if ( not IPv4.validSubnet(subnetOrIP) or 
                               int(subnetOrIP.split("/")[1]) != 32 
                             ) else subnetOrIP.split("/")[0]

    """
        Make format comply to x.x.x.x/b 
    """
    @staticmethod
    def makeSubnet(ipOrSubnet:str=None):
        if ( ipOrSubnet is None or 
             ipOrSubnet.count("/") > 1 or
             ( ipOrSubnet.count("/") < 1 and not IPv4.validIP(ipOrSubnet) )
           ):
            return '0.0.0.0/32'
        if ipOrSubnet.count("/") < 1:
            ipOrSubnet += "/32"
        return ipOrSubnet


    """
        Checks if the remote address is from an IP idicated as external route
        Only works for IPv4
        ip     : x.x.x.x
        subnet : x.x.x.x or x.x.x.x/b
        x      : int 0-255
        b      : int 0-32
        bit mask optional, assumer /32 if omitted
    """
    @staticmethod
    def ipInSubnet(ip:str=None,
                   subnet:str=None, 
                   default:bool=True) -> bool:
        subnet = IPv4.makeSubnet(subnet)
        if (ip is None or not IPv4.validIP(ip)):  
            return default
        return IPv4.__dottedQuadToNum__( ip ) & IPv4.__numMaskFromSubnet__( subnet ) == IPv4.__numFromSubnet__( subnet )


    @staticmethod
    def ipInSubnetList(ip:str=None,
                   subnetList:list=None, 
                   default:bool=True) -> bool:
        if subnetList is None or not isinstance(subnetList, list):
            return default
        for subnet in subnetList:
            if IPv4.ipInSubnet(ip=ip, subnet=subnet, default=False):
                return True
        return False
 