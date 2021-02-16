import os
from datetime import time
import subprocess
import sys
import socket
import re
from smb.SMBConnection import SMBConnection
from nmb.NetBIOS import NetBIOS

SMB_PORT = 445
NETBIOS_PORT = 137
NETBIOS_TIMEOUT = 1.5
CONNECT_TIMEOUT = 3
SEARCH_TIMEOUT = 30
UPLOAD_TIMEOUT = 30

class SMBClient:
    def __init__(self, serverOrIP:str=None, username:str=None, password:str=None, service_name:str=None):
        if self.isIP4(serverOrIP): 
            self._ip = serverOrIP
            self._servername = ''
        else:
            self._servername = serverOrIP
            self._ip = None if serverOrIP is None else self.__resolve__(serverOrIP)
        self._username = username
        self._password = password
        self._port = SMB_PORT
        self._service_name = service_name   # service_name is the share
        self._server = None
        self._host = self.__get_localhost__()


    def isIP4(self, serverOrIP):
        # If no valid IP4 adres, try to obtain it
        validation = "^()|((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}$"
        return ( serverOrIP != None and               
                 len(serverOrIP) > 0 and              
                 isinstance(serverOrIP, str) and      
                 serverOrIP.count('.') == 3 and        
                 re.match(validation, serverOrIP)
                )


    def __resolve__(self, server:str):  # str | None
        # If no valid IP adres, try to obtain it
        # First as netBIOS on LAN
        nb = NetBIOS(broadcast=True, listen_port=0)
        # Send a query on the network and hopes that if machine matching the name will reply with its IP address.
        res = nb.queryName(server, ip='', port=NETBIOS_PORT, timeout=NETBIOS_TIMEOUT)
        if isinstance(res, list) and len(res) > 0 and isinstance(res[0], str) and self.isIP4(res[0]):
            return res[0]
        # Try to DNS resolve
        try:
            return socket.gethostbyname(server)
        except socket.gaierror as sge:
            # Nope, didn't work
            return None

    """
        returns con successful (bool) and a dict (json) with details
        catch values using 
            *r = self.connect()
        or 
            connected, details = self.connect()
        os simply
            connected = self.connect()[0]
    """
    def connect(self):
        """ Connect and authenticate to the SMB share. """
        self._server = SMBConnection(username=self._username,
                                     password=self._password,
                                     my_name=self._host,
                                     remote_name=self._servername,
                                     use_ntlm_v2=True)
        connectSuccess = False
        connectionRefused = False
        resolved = self._ip is not None
        if not resolved:
            return connectSuccess, {'resolved': resolved, 'connectionRefused': connectionRefused }
        try:
            connectSuccess = self._server.connect(self._ip, port=self._port, timeout=CONNECT_TIMEOUT)
        except ConnectionRefusedError as cre:
            connectionRefused = True
        except Exception as e:
            pass
        return connectSuccess, dict({'resolved': resolved, 'connectionRefused': connectionRefused })


    def close(self):
        if self._server is not None:
            self._server.close()

    """
        service_name (string/unicode) – the name of the shared folder for the path
        path (string/unicode) – path relative to the service_name where we are interested to learn about its files/sub-folders.
        search (integer) – integer value made up from a bitwise-OR of SMB_FILE_ATTRIBUTE_xxx bits (see smb_constants.py).
        pattern (string/unicode) – the filter to apply to the results before returning to the client.
    """
    def list(self, serviceName:str=None, smbPath:str='/', pattern:str='*', search:int=65591, timeout:int=SEARCH_TIMEOUT):
        return self._server.listPath(service_name=serviceName if serviceName is not None else self._service_name, 
                                     path=smbPath, 
                                     search=search, 
                                     pattern=pattern, 
                                     timeout=timeout
                                    )

    """
        Retrieve a list of shared resources on remote server.
        Returns:	A list of smb.base.SharedDevice instances describing the shared resource
    """
    def listShares(self, timeout:int=SEARCH_TIMEOUT):
        if self._server is not None:
            return self._server.listShares(timeout=timeout)
        return None


    def download(self, service_name:str=None, local_path:str=None, remote_path:str=None, files:list=[]):
        """ Download files from the remote share. """
        for file in files:
            with open(os.path.join(local_path, file) if local_path is not None else file, 'rb') as file_obj:
                self._server.retrieveFile(service_name=self._service_name,
                                          path=os.path.join(remote_path, file) if remote_path is not None else file,
                                          file_obj=file_obj
                                          )

    def upload(self, service_name:str=None, local_path:str=None, remote_path:str=None, files:list=[], timeout:int=UPLOAD_TIMEOUT):
        """ Upload files to the remote share. """
        try:
            for file in files:
                with open(os.path.join(local_path, file) if local_path is not None else file, 'rb') as file_obj:
                    self._server.storeFile(service_name=service_name if service_name is not None else self._service_name,
                                           path=os.path.join(remote_path, file) if remote_path is not None else file,
                                           file_obj=file_obj,
                                           timeout=timeout
                                           )
        except Exception as e:
            pass


    def __get_localhost__(self):
        return subprocess.check_output('hostname', shell=True).decode(sys.stdout.encoding).strip()
