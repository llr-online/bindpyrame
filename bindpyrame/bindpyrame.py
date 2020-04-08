#!/usr/bin/env python3
VERSION="0.1"
import socket

#=================================================================================================
def sendcmd(host,port,cmd,*args):
    """
    simple function to bind to pyrame by sending xml command and decoding the answer.

    Typical use:
        retcode,res = sendcmd("localhost",9007,"onearg_test","toto")
        print("+ retcode %d\n res %s" % (retcode,res))

       retcode,res = sendcmd("localhost",9007,"onearg","toto")
       print("+ retcode %d\n res %s" % (retcode,res))

    """
    command="<cmd name=\"%s\">" % cmd
    for i in args:
        command+= "<param>%s</param>" % i
    command+="</cmd>\n"

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = socket.gethostbyname(host)
        
        s.connect((ip,port))
        s.send(command.encode('utf-8'))
        data=""
        while True:
            
            a = s.recv(1).decode('utf-8')
            data +=a 
            if a=="\n":
                break
        

        b=data.split("=")[1]
        retcode = b.split(">")[0]
        rawmsg = b.split(">")[1]
        rawmsg2=rawmsg.split("[")[2]
        msg=rawmsg2.split("]")[0]
        return int(retcode.replace('"','')),msg
    
    except Exception as e:
        print(str(e))
        return 0,str(e)


#=================================================================================================
#  
#=================================================================================================
import logging
logging.basicConfig(level=logging.DEBUG)
import socket
PYRAMEPORTFILE="/opt/pyrame/ports.txt"

"""
This module is a proxy for calling pyrame without creating a pyrame module.

For example:

import pyrame_proxy 

# connect to module running at port 9512 here yo_gs200 (in fact 
p=pyrame_proxy.pyrame_proxy('localhost',9512) 





"""



def Port2Name(filename):
    logging.info("in setPort2Name")
    port2name = {}
    with open(filename) as p:
        for l in p.readlines():
            # getting the line and removing comments
            d = l.strip().split("#")[0] 
            if d:
                # splitting the line and getting the module name and port
                m,p = d.split('=') 
                port2name[int(p)] = m.lower().replace("_port", "")

    return port2name

#=================================================================================================
class pyrame_proxy(object):
    """
    class to proxy pyrame call
    """
#--------------------------------------------------------------------------------------------------------
    def __init__(self,host,port,pyrame_ports_filename=PYRAMEPORTFILE):
        """
        init function to store and initialize variables
        """
        logging.info("in __init__")
        # internal variable
        self._api = {}
        
        self._args_list = []
        self._args_default = {} 

        # set variable
        self._port2name = Port2Name(pyrame_ports_filename)
        self.module_name = self._port2name.get(int(port))
        if not self.module_name:
            print("available ports are %s" % (", ".join(map(str,self._port2name.items()))))
            return #0,("port %d not found" % int(port))

        self._host = host
        self._port = port

        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = socket.gethostbyname(self._host)
        try:
            self._s.connect((ip,self._port))
        except ConnectionRefusedError as e:
            raise Exception(0,"cannot connect to the port %d of the module %s !!\nCheck if it is up" %
                            (port,self.module_name))
        
        # get the api
        retcode,res = self.__sendcmd("getapi")
        args_list=[]
        for f in res.split(";")[:-1]:
            n,a = f.split(":")
            self._api[n.replace("_"+self.module_name,"")]=a.split(",")
            args_list.extend(a.split(","))
        self._args_list = list(set(args_list))
        for i in self._args_list:
            self._args_default[i] = None
                             
#--------------------------------------------------------------------------------------------------------
    def listFunctions(self):
        print("available functions are:\n")
        for n,a in self._api.items():
            print("\t%s( %s )" % (n,", ".join(a)))
#--------------------------------------------------------------------------------------------------------
    def listAllArgs(self):
        print("available args are:\n%s" %  ", ".join(self._args_list))        
#--------------------------------------------------------------------------------------------------------
    def listArgsDefault(self):
        print("Default value for arguments:\n")
        for n,a in self._args_default.items():
            print("\t%-20s :  %s " % (n,str(a)))
#--------------------------------------------------------------------------------------------------------
    def setArgs(self,a,d):
        if a in self._args_default:
            self._args_default[a]=d
#--------------------------------------------------------------------------------------------------------
    def getArgs(self,a):
        if a in self._args_default:
            return(self._args_default[a])
        else:
            return None
#--------------------------------------------------------------------------------------------------------
    # NOTE this maybe used to create a getter setter for the ditionnary
    #def __getattribute__(self, name):
    #    print("got attribute %s" % name)
    #    return object.__getattribute__(self, name)
#--------------------------------------------------------------------------------------------------------
    def __getattr__(self, name):
        """
        this special method is called when the function is not defined in the class and so we use this
        to proxy the call to the pyrame module
        """
        #logging.info("in __getattr__ with attr: %s " % name)
        def method(*args):
            ret = 0
            res = "Unknown function"
            
            #logging.debug("calling self.__sendcmd with %s %s" % (name,str(args)))
            #logging.debug("%s in %s " % (name,str(name in self._api.keys())))
            if name in self._args_default.keys():
                print("we should have a key")
            
            if name in list(self._api.keys()):
                logging.debug("known function expecting args %s" % self._api[name])
                nargs=[]
                oldargs=list(args)
                oldargs.reverse()
                for a in self._api[name]:
                    if self._args_default[a]:
                        nargs.append(self._args_default[a])
                    else:
                        if oldargs:
                            nargs.append(oldargs.pop())
                        else:
                            return 0,"Wrong number of arguments"
                try:
                    return self.__sendcmd(name,*nargs)        
                except Exception:
                    return 0,"Unknown Error when calling function %s with %s" % (name,str(args))
            return 0,"Unknown function"
            
        return method
        
#--------------------------------------------------------------------------------------------------------
    def __sendcmd(self,cmd,*args):

        logging.info("in __sendcmd with cmd: %s and args %s  " % (cmd,str(args)))
        
        # creating the xml line
        command="<cmd name=\"%s_%s\">" % (cmd,self.module_name)
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
            return int(retcode.replace('"','')),msg
    
        except Exception as e:
            print(str(e))
            return 0,str(e)
#=================================================================================================
