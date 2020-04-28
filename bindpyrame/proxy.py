#!/usr/bin/env python3
"""
This module is a proxy for calling pyrame without creating a pyrame module.

For example::

     import bindpyrame

     # connect to the module running at port 9007 here cmd_test
     p = bindpyrame.pyrame_proxy('localhost',9007)

     # listFunctions() show the prototype of the the available functions from the module
     p.listFunctions()

"""



import socket
import logging
logging.basicConfig(level=logging.DEBUG)

PYRAMEPORTFILE = "/opt/pyrame/ports.txt"
VERSION = "0.1"

def port_2_name(filename):
    """

    Utility function to load the port to name association stored in filename

    Parameters
    ----------
    filename : str
         the path containing the port to name association for pyrame

    Returns
    -------
    dict
         the dict contains the port to name association

    """
    logging.info("in setPort2Name")
    port2name = {}
    with open(filename) as p:
        for line in p.readlines():
            # getting the line and removing comments
            d = line.strip().split("#")[0]
            if d:
                # splitting the line and getting the module name and port
                m, p = d.split('=')
                port2name[int(p)] = m.lower().replace("_port", "")

    return port2name

# =================================================================================================
class PyrameProxy(object):

    comment="""

    class to proxy pyrame calls

    :param host: the host where pyrame is running
    :type host: a string
    :param port: the port of the module
    :type port: an integer
    :param pyrame_ports_filename: the file containing the association between ports and modules
    :type pyrame_ports_filename: a path
    """
# --------------------------------------------------------------------------------------------------------

    def __init__(self, host, port, pyrame_ports_filename=PYRAMEPORTFILE):
        comment="""
        Class constructor needs:

        """
        logging.info("in __init__")
        # internal variable
        self._api = {}
        
        self._args_list = []
        self._args_default = {} 

        # set variable
        self._port2name = port_2_name(pyrame_ports_filename)
        self.module_name = self._port2name.get(int(port))
        if not self.module_name:
            print("available ports are %s" % (", ".join(map(str,self._port2name.items()))))
            return #0,("port %d not found" % int(port))

        self._host = host
        self._port = port

        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            ip = socket.gethostbyname(self._host)
            self._s.connect((ip, self._port))
        except socket.error as e:
            raise Exception(0, "can't connect to the port %d of the module %s \nError: %s\nCheck if it is up" %
                              (port, self.module_name,str(e)))
        
        # get the api
        retcode, res = self.__sendcmd("getapi")
        args_list = []
        for f in res.split(";")[:-1]:
            n, a = f.split(":")
            self._api[n.replace("_"+self.module_name, "")] = a.split(",")
            args_list.extend(a.split(","))
        self._args_list = list(set(args_list))
        for i in self._args_list:
            self._args_default[i] = None
                             
# --------------------------------------------------------------------------------------------------------

    def print_list_functions(self):
        comment="""

        :return:
        """
        logging.info("in list_functions")

        print("available functions are:\n")
        for n, a in self._api.items():
            print("\t%s( %s )" % (n, ", ".join(a)))

# --------------------------------------------------------------------------------------------------------

    def print_list_all_args(self):
        logging.info("in list_all_args")
        print("available args are:\n%s" % ", ".join(self._args_list))
# --------------------------------------------------------------------------------------------------------

    def print_list_args_default(self):
        logging.info("in list_args_default")

        print("Default value for arguments:\n")
        for n, a in self._args_default.items():
            print("\t%-20s :  %s " % (n, str(a)))
# --------------------------------------------------------------------------------------------------------

    def set_args(self, argName, value):
        comment="""
        Set the value of args that is given to a function

        Parameters
        ----------
        argName : str
        value : str

        Returns
        -------

        """

        logging.info("in set_args with args %s %s" % (argName, value))

        if argName in self._args_default:
            self._args_default[argName] = value
# --------------------------------------------------------------------------------------------------------

    def get_arg(self, argName):
        comment="""
        get the value for the arg of name
        :param argName:
        :return: the value of the arguments
        """
        logging.info("in get_arg with arg %s" % a)

        if a in self._args_default:
            return self._args_default[a]
        else:
            return None
# --------------------------------------------------------------------------------------------------------
    # NOTE this maybe used to create a getter setter for the ditionnary
    #def __getattribute__(self, name):
    #    print("got attribute %s" % name)
    #    return object.__getattribute__(self, name)
# --------------------------------------------------------------------------------------------------------

    def __getattr__(self, name):
        # logging.info("in __getattr__ with attr: %s " % name)
        def method(*args):
            ret = 0
            res = "Unknown function"
            
            # logging.debug("calling self.__sendcmd with %s %s" % (name,str(args)))
            # logging.debug("%s in %s " % (name,str(name in self._api.keys())))
            if name in self._args_default.keys():
                print("we should have a key")
            
            if name in list(self._api.keys()):
                logging.debug("known function expecting args %s" % self._api[name])
                nargs = []
                oldargs = list(args)
                oldargs.reverse()
                for a in self._api[name]:
                    if self._args_default[a]:
                        nargs.append(self._args_default[a])
                    else:
                        if oldargs:
                            nargs.append(oldargs.pop())
                        else:
                            return 0, "Wrong number of arguments"
                try:
                    return self.__sendcmd(name,*nargs)        
                except Exception:
                    return 0, "Unknown Error when calling function %s with %s" % (name,str(args))
            return 0, "Unknown function"
            
        return method
        
# --------------------------------------------------------------------------------------------------------
    def __sendcmd(self,cmd,*args):

        logging.info("in __sendcmd with cmd: %s and args %s  " % (cmd,str(args)))

        # creating the xml line
        command = "<cmd name=\"%s_%s\">" % (cmd,self.module_name)
        for i in args:
            command += "<param>%s</param>" % i
        command += "</cmd>\n"

        try:
            logging.debug("sending command: %s" % command)
            self._s.send(command.encode('utf-8'))
    
            data = self._s.recv(1024).decode('utf-8')
            while data[-1] != '\n':
                data += self._s.recv(1024).decode('utf-8')
            
            # typical result
            # <res retcode="__RETCODE__"><![CDATA[__DATA__]]></res>
            # We want to extract >RETCODE< and >DATA<

            logging.debug("received : %s (%d bytes)" % (data,len(data)))
            
            b = data.split("=")[1]
            retcode = b.split(">")[0]
            msg = b.split(">")[1].split("[")[2].split("]")[0]
            return int(retcode.replace('"', '')), msg
    
        except Exception as e:
            print(str(e))
            return 0, str(e)
# =================================================================================================
