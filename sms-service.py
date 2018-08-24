import time
import thread
from time import sleep
import sim800 as modem
import weserv as ws
from parse import *

_POLLING_INTERVAL = 5

def msg_parsing(msg):
	text = msg
	format = '{hwid} {msg}'
	data_prs = parse(format,text)
	if data_prs is None:
		return None,None
	return data_prs['hwid'],data_prs['msg']

def msg_proc(msg=None):
	print msg
	hwid,message = msg_parsing(msg['msg'])
	print hwid
	print message
	hwDetail =  ws.getHwId(hwid)
	if hwDetail is None:
		print 'Unknown Msg & Harware'
		return False
	return ws.postMsg(str(msg['from']),hwDetail['Data'][0]['hw_id'],message)
	

def pooling_sms():
        msglist = modem.getUnreadSMS()
	print "get msg ..."
        if msglist is None:
                return False
        for msg in msglist:
                msg_proc(msg)
		print 'Form ' + msg['from'] + ' sent'

def get_task():
	taskList = ws.getMsgTask()
	if taskList is None:
		return False
	for ts in taskList['Data']:
		build_msg = 'From ' + ts['hw_id'] + '\n' + ts['msg']
		if modem.sendSMS(ts['mobile'],build_msg) is False:
			return False
		ws.postMsgDone(ts['id'])
	return True

def SMS_Handler( threadName):
        while True:
                pooling_sms()
                get_task()
                global _POLLING_INTERVAL
		sleep(_POLLING_INTERVAL)

def main():
        try:
                thread.start_new_thread(SMS_Handler, ("sms_hdlr", ) )
        except:
                print "Error: unable to start thread"

if __name__ == '__main__':
        while ws.checkConnection() is False:
		print 'Connecting to Server...'
		sleep(1)
	print 'Connected to server.'
	while modem.init() is False:
                print 'init failed'
		sleep(1)
	modem.sendSMS('081281012260', 'Sms Gway On')
        main()
        while True:
                pass

