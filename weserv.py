import json
from pprint import pprint
import urllib2
import urllib
_SERVER = 'sv01.inovindojayaabadi.co.id'
_PATH = '/smsgway/'
_USER = 'gway01'
_API = 'c0313293fe51555d7a677ee81d7e6163'
_URI = 'http://'+_SERVER+_PATH+'?user='+_USER+'&apikey='+_API+'&'

# Sek koneksi dari smsgway ke server
def checkConnection():
        f = {
                'method' : 'checkconnect'
        }

        encoded = urllib.urlencode(f)

	try:
		global _URI
		fullpath = _URI + encoded
#                print(fullpath)
		resp = urllib2.urlopen(fullpath)
		html = resp.read()
		jobj = json.loads(html)
		try:
                        jobj = json.loads(html)
                        if(jobj['Status'] is 0):
                                return True
                        else:
                                return False
                except:
                        return False
        except urllib2.URLError as err:
                return False

#mengambil data hw dari server berdasarkan hwid
def getHwId(hwid=''):
	if(hwid==''): return;
	f = {
                'method' : 'gsmgetid',
		'hw_id' : hwid
        }

        encoded = urllib.urlencode(f)
	try:
		global _URI
                fullpath = _URI + encoded
		resp = urllib2.urlopen(fullpath)
		html = resp.read()
		try:
			jobj = json.loads(html)
                	if(jobj['Status'] is 0):
                		return jobj
                	else:
                	        return None
		except:
			return None
        except urllib2.URLError as err:
                return None

#mengirim incoming sms ke ke webservice untuk disimpan di database
def postMsg(mobile='',hwid='',msg=''):
	if(mobile==''): return False
	if(hwid==''): return False
	if(msg==''): return False
	f = { 
		'method' : 'gsmpost', 
		'mobile' : mobile,
		'hw_id' : hwid,
		'msg' : msg
	}

        encoded = urllib.urlencode(f)

	try:
                global _URI
                fullpath = _URI + encoded
		resp = urllib2.urlopen(fullpath)
                html = resp.read()
                try:
                        jobj = json.loads(html)
                        if(jobj['Status'] is 0):
                                return True
                        else:
                                return False
                except:
                        return False
        except urllib2.URLError as err:
                return False


def getMsgTask():
        f = {
                'method' : 'gsmgettask'
        }

        encoded = urllib.urlencode(f)
        try:
                global _URI
                fullpath = _URI + encoded
                resp = urllib2.urlopen(fullpath)
                html = resp.read()
                try:
                        jobj = json.loads(html)
                        if(jobj['Status'] is 0):
                                return jobj
                        else:
                                return None
                except:
                        return None
        except urllib2.URLError as err:
                return None

def postMsgDone(msgId=-1):
	if(msgId<0): return False
        f = {
                'method' : 'smsdone',
                'msg_id' : msgId
        }

        encoded = urllib.urlencode(f)

        try:
                global _URI
                fullpath = _URI + encoded
                resp = urllib2.urlopen(fullpath)
                html = resp.read()
                try:
                        jobj = json.loads(html)
                        if(jobj['Status'] is 0):
                                return True
                        else:
                                return False
                except:
                        return False
        except urllib2.URLError as err:
                return False
	

#print(gsmPost('081281012260','sgi1720','halo@diamana/kamu'))
#print(checkConnection())
#test = getHwId('sgi1720')
#if(test is not None):
#print(test)
#print(getGsmTask())
#print(postMsgDone(6))
