#!/usr/bin/env python3
import socket


def sendcmd(host,port,cmd,*args):
    
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



#retcode,res = sendcmd("localhost",9007,"onearg_test","toto")
#print("+ retcode %d\n res %s" % (retcode,res))
#retcode,res = sendcmd("localhost",9007,"onearg","toto")
#print("+ retcode %d\n res %s" % (retcode,res))
