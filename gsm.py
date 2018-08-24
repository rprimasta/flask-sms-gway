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

def internet_on():
	try:
        	urllib2.urlopen('http://digital.inovindojayaabadi.co.id/smsgway/?user=rezza&apikey=ahs7r8ljw73gbf83ojhgf&method=checkconnect', timeout=30)
		global inet_err
		inet_err = 0
        	return True
    	except urllib2.URLError as err:
        	return False

def wait_ok(timeout=5):
        response = ''
        t_timeout = time.time() + 60*timeout
        while response != 'OK\r\n':
                response =  ser.readline()
                if time.time() > t_timeout:
                        return False
                print response
        return True 

def checkConnection(retry = 5):
	inet_retry = 0
	while(internet_on()==False):
		global inet_err
                if (inet_retry >= retry and inet_err == 0):
                        err_msg = 'Err : Tidak dapat menggapai server. Pastikan perangkat terhubung dengan internet.'
                        print(err_msg)
                        global dev_phone
			sendSMS(dev_phone,err_msg)
			inet_err = 1
			return False
                inet_retry += 1
                sleep(1)
	return True

def setup():
	print('Periksa jaringan internet.')
	if (checkConnection(10000)==True):	
		print('Internet terhubung')
	#setting serial communication
	#waiting for ready 
	print('wait...')
	sleep(2)
	cmd = 'ATE0\r'
	ser.write(cmd.encode())
	wait_ok()
	#check the modem is connected
	cmd = 'AT\r'
	ser.write(cmd.encode())
	if wait_ok()==True:
		print('Modem Conected')
	else:
		print('Modem Not Connect')
	#initializing modem
	cmd = 'AT+CPIN?\r'
	print('Modem :' + cmd)
	ser.write(cmd.encode())
	wait_ok()
	cmd = 'AT+CMGF=1\r'
	print('Modem :' + cmd)
	ser.write(cmd.encode())
	wait_ok()
	cmd = 'AT+CNMI=2,0,0,0\r'
	print('Modem :' + cmd)
	ser.write(cmd.encode())
	wait_ok()
	cmd = 'AT+CMGD=1,2\r'
	print('Modem :' + cmd)
	ser.write(cmd.encode())
	wait_ok()
	
	#checkBalance()
	#print("Selesai")
	#while True:
	#	pass	

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
	

def sendSMS(number, text, timeout=5):
	cmd = 'AT+CMGS="'+number+'"\r'
	print('Modem :' + cmd)
	ser.write(cmd.encode())
	response = ''
	t_timeout = time.time() + 60*timeout
	while response != '>':
                response =  ser.read()
                if time.time() > t_timeout:
                        return False

	ser.write(text.encode())
	ser.write(chr(26))
	wait_ok(15)


def isUnread(timeout=5):
        response = ''
        content = ''
	msglist = []
        t_timeout = time.time() + 60*timeout
        while response != 'OK\r\n':
                response =  ser.readline()
                content += response
                if time.time() > t_timeout:
                        return False
	count = content.count('+CMGL')
	if(count!=0):
		formating = ''
		for x in range(0,count):
			formating += '\r\n+CMGL:{index_'+str(x)+'},{record_'+str(x)+'},"{from_'+str(x)+'}",{nc_'+str(x)+'},"{date_'+str(x)+'}"\r\n{msg_'+str(x)+'}\r\n' 
		formating += '\r\nOK\r\n'
		parsdat = parse(formating,content)
		
		for x in range(0,count):
			msg = {'from':'','date':'','msg':''}
			msg['from'] = parsdat['from_'+str(x)]
			msg['date'] = parsdat['date_'+str(x)]
			msg['msg'] = parsdat['msg_'+str(x)]
			stid = msg['msg'].find(' ')
			getid = msg['msg'][:stid]
			mesg = msg['msg'][1+stid:]
			hw_id = getid
			url = 'http://digital.inovindojayaabadi.co.id/smsgway/?user=rezza&apikey=ahs7r8ljw73gbf83ojhgf&method=gsmgetid&id=' + hw_id
			contents = urllib2.urlopen(url).read()
			if contents!='-1':
				json_res = json.loads(contents)
				print('Http[db] : Owner' + json_res['owner'])
				wsmg = mesg.replace(" ", "%20")
				wsmg = wsmg.replace("\r","%0D")
				wsmg = wsmg.replace("\n","%0A")
				wmobile = msg['from'].replace('+','')
				urlpost = 'http://digital.inovindojayaabadi.co.id/smsgway/?user=rezza&apikey=ahs7r8ljw73gbf83ojhgf&method=gsmpost&mobile='+wmobile+'&hw_id='+getid+'&msg=' + wsmg
				print('Http[request] :' + urlpost)
				resp = urllib2.urlopen(urlpost).read()
				if resp!='-1':
					#print(urlpost)
					sendSMS(msg['from'], 'Pesan sedang diproses.\r\nHwId:'+json_res['hw_id']+'\r\nOwner:'+json_res['owner'])
				else:
					sendSMS(msg['from'], 'Proses Gagal.\r\nHwId:'+json_res['hw_id']+'\r\nOwner:'+json_res['owner'])

			else:
				print('Http[db] : Hw_id tidak terdaftar !')	
		print('Modem : ' + formating)
		print(';;;;;;;;;;;... Decoding Message ...;;;;;;;;;;;;;;')
		print('Modem : ' + str(msglist))		
		rs = content.find('+CMGL')
		sh1 = content[rs:].find('\n')
		header = content[rs:sh1]
        	print('==========Message Count : ' + str(count) + '============')
        	print("".join("{:02x}".format(ord(c)) for c in content))
		print('========================ASCII===========================')
		print(content)
		print('=========...Read Message Complete...=============')
        	return True


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

def pooling_sms():
	cmd = 'AT+CMGL="REC UNREAD"\r'
	ser.write(cmd.encode())
	isUnread()

def send_task():
	if(checkConnection()!=False):
		try:
			url = 'http://digital.inovindojayaabadi.co.id/smsgway/?user=rezza&apikey=ahs7r8ljw73gbf83ojhgf&method=gsmgettask'
			contents = ''
			contents = urllib2.urlopen(url).read()
			if (contents != '-1'):
				json_res = json.loads(contents)
				for dt in json_res['Data']:
					sendSMS(dt['mobile'],dt['msg'])
					urlupdate = 'http://digital.inovindojayaabadi.co.id/smsgway/?user=rezza&apikey=ahs7r8ljw73gbf83ojhgf&method=smsdone&id=' + str(dt['id'])
					urllib2.urlopen(urlupdate).read()

		except:
			err_msg = "Check Task Error. Please check your internet connection !"		
		
	
def readSMS_Handler( threadName, modem):
	while True:
		pooling_sms()
		send_task()
		sleep(1)

def main():
	try:
   		thread.start_new_thread( readSMS_Handler, ("readsms_hdlr", ser, ) )
	except:
   		print "Error: unable to start thread"
	
if __name__ == '__main__':
	setup()
	main()
	while True:
		pass

ser.close()

