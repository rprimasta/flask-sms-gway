import json
import urllib2
import time 
import thread 
from time import sleep 
import serial
from parse import *

#debuging purpose & declare global variable here !	
dev_phone = "+6281281012260"
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=5)
inet_err = 0

def wait_ok(timeout=5):
        response = ''
        t_timeout = time.time() + 60*timeout
        while response != 'OK\r\n':
                response =  ser.readline()
                if time.time() > t_timeout:
                        return False
                print response
        return True 

def sendCmd(cmd='',waitOk=False,timeOut=5):
	ser.write(cmd.encode())
	if waitOk is True: 
		return wait_ok(timeOut)
	else:
		return True;

def checkModem():
	cmd = 'AT\r'
        ser.write(cmd.encode())
        if wait_ok()==True:
                return True
        else:
                return False

def init():
	if checkModem() is False:
		return False
	if sendCmd(cmd='AT+CPIN?\r',waitOk=True) is False:
		return False
	if sendCmd(cmd='AT+CMGF=1\r',waitOk=True) is False:
		return False
	if sendCmd(cmd='AT+CNMI=2,0,0,0\r',waitOk=True) is False:
		return False
	deleteRead()
	#if sendCmd(cmd='AT+CMGD=1,2\r',waitOk=False) is False:
	#	return False
	sleep(3)	
	return True


def deleteRead():
	print 'Deleting Read Messages'
	if sendCmd(cmd='AT+CMGD=1,2\r',waitOk=True) is False:
                return False
	print 'Read Messages Deleted'
	return True
	

def checkBalance(timeout=5):
	status = 0
	while status==0:
		cmd = 'AT+CUSD=1,"*888\x23"\r'
        	print('Modem :' + cmd)
        	ser.write(cmd.encode())
		wait_ok()
		response = ''
        	t_timeout = time.time() + 60*timeout
        	while response[:5] != '+CUSD':
                	response =  ser.readline()
			print(response)
                	if time.time() > t_timeout:
                        	return False

		format = '+CUSD:{status},{msg}'
		result = parse(format,response)
		status = int(result['status'])
		if(status==1):
			st_bl = result['msg'].find('Rp.')
			sp_bl = response[st_bl+3:].find(' ')
			print(sp_bl)
		
		sleep(0.5)
		ser.reset_input_buffer()
	return True
	
def sendCTRLZ():
	ser.write(chr(26))

def sendSMS(number, text, timeout=5):
	print 'sms mode...'
	sendCmd(cmd = 'AT+CMGS="'+number+'"\r')
	response = ''
	print 'get response'
	t_timeout = time.time() + 60*timeout
	while response != '>':
                response =  ser.read()
		print response
                if time.time() > t_timeout:
                        return False
	print('Writting')
	sendCmd(cmd=text,waitOk=False)
	print text
	sendCTRLZ()
	print 'sending'	
	wait_ok(15)
	print 'berhasil'
	return True


def getUnreadSMS(timeout=5):
        content = ''
	msglist = []
        t_timeout = time.time() + 60*timeout
	sendCmd(cmd = 'AT+CMGL="REC UNREAD"\r')

        response = ''
        while response != 'OK\r\n':
                response =  ser.readline()
                content += response
                if time.time() > t_timeout:
                        return None

	count = content.count('+CMGL') - 1
	if count>0:
		formating = 'AT+CMGL="REC UNREAD"\r'
		for x in range(0,count):
			formating += '\r\n+CMGL:{index_'+str(x)+'},{record_'+str(x)+'},"{from_'+str(x)+'}",{nc_'+str(x)+'},"{date_'+str(x)+'}"\r\n{msg_'+str(x)+'}\r\n' 
		formating += '\r\nOK\r\n'

		parsdat = parse(formating,content)
#		print '--------------------------------------'
#		print "".join("{:02x}".format(ord(c)) for c in formating)
#		print '======================================'
#		print "".join("{:02x}".format(ord(c)) for c in content)
#		print '---------------Result-----------------'
#		print parsdat
		if parsdat is None:
			return None

		for x in range(0,count):
			msg = {'from':'','date':'','msg':''}
			msg['from'] = parsdat['from_'+str(x)]
			msg['date'] = parsdat['date_'+str(x)]
			msg['msg'] = parsdat['msg_'+str(x)]
			msglist.append(msg)
		#print msglist
		deleteRead()
		return msglist
	else:
		return None
		###############################################################

def notif_available(str):
	if(str[:5] == '+CMTI'):
		return True
	else:
		return False

def notif_decode(str):
	content = str[7:]
	split = content.split(',')
	print('S1 : ' + split[0]) #storage
	print('S2 : ' + split[1]) #index
	return (split[0],int(split[1]))

def read_sms(index):
	cmd = 'AT+CMGR=' + str(index) + '\r'
	print(cmd)
	ser.write(cmd.encode())
	wait_ok()

def read_sms_by(cmd_str):
	cmd = 'AT+CMGL="' + cmd_str + '"\r'
	print(cmd)
	ser.write(cmd.encode())
	wait_ok()

def close():
	ser.close()

