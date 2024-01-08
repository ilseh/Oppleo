import os as os
import logging
import netifaces
import platform
from cpuinfo import get_cpu_info
import psutil
import subprocess
import sys
import re

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

oppleoSystemConfig = OppleoSystemConfig()

class Raspberry(object):
    __logger = None
    """
    Raspberry Model
    """

    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(__name__))     


    def get_ip_info(self):
        self.__logger.debug("get_ip_info()")
        i_ids = netifaces.interfaces()
        r = {}
        for i_id in i_ids:
            i_addr = netifaces.ifaddresses(i_id)
            r[i_id] = {}
            if netifaces.AF_LINK in i_addr:      # Ethernet
                r[i_id]['LINK'] = i_addr[netifaces.AF_LINK]
            if netifaces.AF_INET in i_addr:      # IPv4
                r[i_id]['INET'] = i_addr[netifaces.AF_INET]
            if netifaces.AF_INET6 in i_addr:      # IPv6
                r[i_id]['INET6'] = i_addr[netifaces.AF_INET6]
        return r

    def get_processor_info(self):
        if platform.system() == "Windows":
            return str(platform.processor(), 'utf-8')
        elif platform.system() == "Darwin":
            return str(subprocess.check_output(['/usr/sbin/sysctl', "-n", "machdep.cpu.brand_string"]).strip(), 'utf-8')
        elif platform.system() == "Linux":
            return self.get_cpuinfo_entry('model name')
        return None

    def get_os(self):
        self.__logger.debug("get_os()")
        un = os.uname()
        osi = {}
        osi['nodename'] = un.nodename
        osi['sysname'] = un.sysname
        osi['version'] = un.version
        osi['machine'] = un.machine
        osi['release'] = un.release
        return osi

    def get_cpuinfo_entry(self, entry_name="Unknown"):
        self.__logger.debug("get_cpuinfo_entry() entry_name={}".format(entry_name))
        proc_list = self.get_cpuinfo()
        if proc_list is None:
            self.__logger.debug('proc_list = None, returning Unknown')
            return "Unknown"
        try:
            # cpuinfo returns an entry per processor, plus an entry for the model
            for proc_index in range(len(proc_list)):
                for proc_data_key in proc_list[proc_index]:
                    if entry_name == proc_data_key:
                        self.__logger.debug('Found entry {}, returning {}'.format(proc_data_key, proc_list[proc_index][proc_data_key]))
                        return proc_list[proc_index][proc_data_key]
        except TypeError:
            self.__logger.debug('Data is not iterable')

        self.__logger.debug('Returning Unknown')
        return "Unknown"

    def get_serial(self):
        self.__logger.debug("get_serial()")
        return self.get_cpuinfo_entry('Serial')

    def get_revision(self):
        self.__logger.debug("get_revision()")
        return self.get_cpuinfo_entry('Revision')

    def get_model(self):
        self.__logger.debug("get_model()")
        return self.get_cpuinfo_entry('Model')

    def get_cpuinfo(self):
        self.__logger.debug("get_cpuinfo()")
        cpu = {}
        i = 0
        cpu[i] = {}
        try:
            self.__logger.debug("Open /proc/cpuinfo to read...")
            f = open('/proc/cpuinfo','r')
            for line in f:
                self.__logger.debug("Line: {} ...".format(line))
                if line not in ['\n', '\r\n']:
                    line_parts = line.split(':')
                    cpu[i][line_parts[0].strip()] = line_parts[1].strip()
                else:
                    i += 1
                    cpu[i] = {}

            f.close()
        except:
            self.__logger.debug('Could not open /proc/cpuinfo to get cpu and raspberry revision info...')
            return None
        self.__logger.debug("Returning cpu: {}...".format(cpu))
        return cpu


    def get_cpu_percent(self):
        self.__logger.debug("get_cpu_percent()")
        return str(psutil.cpu_percent())

    def get_virtual_memory(self):
        self.__logger.debug("get_virtual_memory()")
        mem = {}
        vmem = psutil.virtual_memory()
        mem['available'] = vmem.available
        mem['total'] = vmem.total
        mem['percent'] = vmem.percent
        try:
            mem['totalFormatted'] = self.format_size( vmem.total )
        except:
            self.__logger.debug("totalFormatted could not be formatted")
        try:
            mem['availableFormatted'] = self.format_size( vmem.available )
        except:
            self.__logger.debug("availableFormatted could not be formatted")
        return mem

    def get_physical_memory(self):
        self.__logger.debug("get_physical_memory()")
        mem = {}
        try:
            f = open('/proc/meminfo','r')
            for line in f:
                line_parts = line.split(':')
                self.__logger.debug('{} = {}'.format(line_parts[0].strip(), line_parts[1].strip()))
                mem[line_parts[0].strip()] = line_parts[1].strip()
            f.close()
        except:
            self.__logger.debug('Could not open /proc/meminfo to get cpu and raspberry revision info...')
            return None
        # MemTotal
        try:
            mem['MemTotalFormatted'] = self.format_size( int(mem['MemTotal'].strip().split(' ')[0]) * 1000 )
        except:
            self.__logger.debug("MemTotalFormatted could not be formatted")
        # MemFree
        try:
            mem['MemFreeFormatted'] = self.format_size( int(mem['MemFree'].strip().split(' ')[0]) * 1000 )
        except:
            self.__logger.debug("MemFreeFormatted could not be formatted")
        # MemAvailable
        try:
            mem['MemAvailableFormatted'] = self.format_size( int(mem['MemAvailable'].strip().split(' ')[0]) * 1000 )
        except:
            self.__logger.debug("MemAvailableFormatted could not be formatted")
        self.__logger.debug("get_physical_memory() return {}".format(mem))
        return mem


    def format_size(self, val): # 18.983.407.616 - 18GB 18.983MB - 18.983.407KB - 18.983.407.616B
        self.__logger.debug("format_size()")
        f = {}
        f['size'] = val
        f['unit'] = "Bytes"
        if  f['size'] > 1024:
            f['size'] = round(  f['size'] / 102.4 ) /10
            f['unit'] = "KB"
        if f['size'] > 1024:
            f['size'] = round( f['size'] / 102.4 ) /10
            f['unit'] = "MB"
        if f['size'] > 1024:
            f['size'] = round( f['size'] / 102.4 ) /10
            f['unit'] = "GB"
        if f['size'] > 1024:
            f['size'] = round( f['size'] / 102.4 ) /10
            f['unit'] = "TB"
        return f 

    def get_disk(self):
        self.__logger.debug("get_disk()")
        dsk = {}
        du = psutil.disk_usage('/')
        dsk['free'] = self.format_size(du.free)
        dsk['used'] = self.format_size(du.used)
        dsk['total'] = self.format_size(du.total)
        dsk['percent'] = \
            du.percent
        return dsk


    def getPid(self) -> str:
        self.__logger.debug("getPid(): {}".format(str(os.getpid())))
        return str(os.getpid())

    def getPPid(self) -> str:
        self.__logger.debug("getPPid(): {}".format(str(os.getppid())))
        return str(os.getppid())

    def getPidStartTime(self, pid) -> str:
        self.__logger.debug("getPidStartTime()")
        result = subprocess.run("ps -o start= -p {}".format(pid), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        # print(result.stderr)
        return result.stdout.rstrip()

    def getPidElapsedTime(self, pid) -> str:
        self.__logger.debug("getPidElapsedTime()")
        result = subprocess.run("ps -o etime= -p {}".format(pid), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        # print(result.stderr)
        return result.stdout.rstrip()


    """
        uptime
        Returns a string describing the uptime of the platform
        Returns a string describing the uptime of this Oppleo instance
    """
    def uptime(self):
        self.__logger.debug("uptime()")
        ut = {}
        ut['sysstarttime'] = self.getPidStartTime(1)
        ut['sysuptime'] = self.getPidElapsedTime(1)
        ut['pidstarttime'] = self.getPidStartTime(self.getPid())
        ut['piduptime'] = self.getPidElapsedTime(self.getPid())
        return ut

    """
        OS info
        sysname - operating system name
        nodename - name of machine on network (implementation-defined)
        release - operating system release
        version - operating system version
        machine - hardware identifier
    """

    def getPlatformType(self):
        self.__logger.debug("getPlatformType(): ".format(sys.platform))
        if sys.platform == 'linux':
            return 'Linux'
        if sys.platform == 'darwin':
            return 'macOS'
        if sys.platform == 'win32':
            return 'Windows'
        if sys.platform == 'cygwin':
            return 'Windows/Cygwin'
        if sys.platform == 'aix':
            return 'AIX'
        return 'Unknown'


    # Check whether `name` is on PATH and marked as executable.
    def is_tool_available(self, name):
        # from whichcraft import which
        from shutil import which
        return which(name) is not None

    def hasSystemCtl(self) -> bool:
        return self.is_tool_available('systemctl')


    def systemCtlStatus(self):
        result = subprocess.run(["systemctl status Oppleo.service"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)

        ctl = {}
        ctl['status'] = "-"
        ctl['pid'] = "-"
        ctl['mem'] = "-"

        # Get the process status
        try:
            for line in result.stdout.split('\n'):
                if re.search('Active:', line):
                    ctl['status'] = line.split("Active:",1)[1].strip()
                    break
        except:
            pass

        # Get the process pid
        try:
            for line in result.stdout.split('\n'):
                if re.search('Main PID:', line):
                    ctl['pid'] = line.split("Main PID:",1)[1].split("(",1)[0].strip()
                    break
        except:
            pass

        # Get the memory usage
        try:
            for line in result.stdout.split('\n'):
                if re.search('Memory:', line):
                    ctl['mem'] = line.split("Memory:",1)[1].strip()
                    break
        except:
            pass
        
        return ctl


    def get_all(self):
        try:
            self.__logger.debug("get_all()")
        except Exception as e:
            pass
        data = {}
        data['ip'] = self.get_ip_info()
        data['revision'] = self.get_revision()
        data['os'] = self.get_os()
        data['platform'] = self.getPlatformType()
        data['proc'] = self.get_processor_info()
        data['cpu'] = self.get_cpuinfo()
        data['model'] = self.get_model()
        data['disk'] = self.get_disk()
        data['vmem'] = self.get_virtual_memory()
        data['pmem'] = self.get_physical_memory()
        
        data['uptime'] = self.uptime()
        data['platform'] = self.getPlatformType()
        data['proc_pid'] = self.getPid()
        data['parent_pid'] = self.getPPid()

        if self.hasSystemCtl():
            data['systemctl'] = self.systemCtlStatus()
        else:
            data['systemctl'] = 'No'
       
        return data
