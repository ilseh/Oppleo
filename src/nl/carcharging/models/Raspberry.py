import os as os
import logging
import netifaces
from cpuinfo import get_cpu_info
import psutil

class Raspberry():
    """
    Raspberry Model
    """

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.models.Raspberry')
        self.logger.debug('Initializing Raspberry without data')


    def get_ip_info(self):
        self.logger.("get_ip_info()")
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

    def get_os(self):
        self.logger.("get_os()")
        return os.uname()

    def get_hardware(self):
        self.logger.("get_hardware()")
        hw = {}
        for key, value in get_cpu_info().items():
            hw[key] = value
        return hw

    def get_model_old(self):
        self.logger.("get_model_old()")
        data = self.get_hardware()
        for entry in data:
            if "Model" in entry:
                return entry["Model"]
        return "Unknown"

    def get_cpuinfo_entry(self, entry_name="Unknown"):
        self.logger.("get_cpuinfo_entry()")
        data = self.get_cpuinfo()
        if data is None:
            return "Unknown"
        try:
            for entry in data:
                if entry_name in entry:
                    return entry[entry_name]
        except TypeError:
            logger.debug('Data is not iterable')

        return "Unknown"

    def get_serial(self):
        self.logger.("get_serial()")
        return self.get_cpuinfo_entry('Serial')

    def get_revision(self):
        self.logger.("get_revision()")
        return self.get_cpuinfo_entry('Revision')

    def get_model(self):
        self.logger.("get_model()")
        return self.get_cpuinfo_entry('Model')

    def get_cpuinfo(self):
        self.logger.("get_cpuinfo()")
        cpu = {}
        i = 0
        cpu[i] = {}
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
                if line not in ['\n', '\r\n']:
                    line_parts = line.split(':')
                    cpu[i][line_parts[0].strip()] = line_parts[1].strip()
                else:
                    i += 1
                    cpu[i] = {}

            f.close()
        except:
            self.logger.debug('Could not open /proc/cpuinfo to get cpu and raspberry revision info...')
            return None
        return cpu

    def get_revision_old(self):
        self.logger.("get_revision_old()")
        # Extract board revision from cpuinfo file
        myrevision = "0000"
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
                if line[0:8]=='Revision':
                    length=len(line)
                    myrevision = line[11:length-1]
            f.close()   
        except:
            myrevision = "0000"
        
        return myrevision

    def get_cpu_percent(self):
        self.logger.("get_cpu_percent()")
        return str(psutil.cpu_percent())

    def get_virtual_memory(self):
        self.logger.("get_virtual_memory()")
        mem = {}
        vmem = psutil.virtual_memory()
        mem['available'] = round(
            vmem.available /1024.0 /1024.0,
            1
        )
        mem['total'] = round(
            vmem.total /1024.0 /1024.0,
            1
        )
        mem['percent'] = \
            vmem.percent
        return mem

    def get_physical_memory(self):
        self.logger.("get_physical_memory()")
        mem = {}
        i = 0
        mem[i] = {}
        try:
            f = open('/proc/meminfo','r')
            for line in f:
                if line not in ['\n', '\r\n']:
                    line_parts = line.split(':')
                    mem[i][line_parts[0].strip()] = line_parts[1].strip()
                else:
                    i += 1
                    mem[i] = {}

            f.close()
        except:
            self.logger.debug('Could not open /proc/meminfo to get cpu and raspberry revision info...')
            return None
        return mem

    def format_size(self, val): # 18.983.407.616 - 18GB 18.983MB - 18.983.407KB - 18.983.407.616B
        self.logger.("format_size()")
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
        self.logger.("get_disk()")
        dsk = {}
        du = psutil.disk_usage('/')
        dsk['free'] = self.format_size(du.free)
        dsk['used'] = self.format_size(du.used)
        dsk['total'] = self.format_size(du.total)
        dsk['percent'] = \
            du.percent
        return dsk

    def get_all(self):
        self.logger.("get_all()")
        data = {}
        data['ip'] = self.get_ip_info()
        data['revision'] = self.get_revision()
        data['os'] = self.get_os()
        data['hardware'] = self.get_hardware()
        data['model'] = self.get_model()
        data['disk'] = self.get_disk()
        data['vmem'] = self.get_virtual_memory()
        data['pmem'] = self.get_physical_memory()
        return data
