'''
Written By Chris Weber, chrisw706@gmail.com

It will parse the LG Tmobile voicemail folder and add any voicemails in that folder to the voicemail model
in Cellebrite DataStore.
This script was created using a some lines for a code created by Ronnie Faircloth. 
Ronnie wrote a script to do this same thing, but for the purpose of learning I wrote
another one.
'''
from physical import *
import SQLiteParser, datetime
from System import TimeSpan



class lgVM(object):
	def __init__(self, node,dirpath):
		self.node = node
		self.dirpath = dirpath
		self.db = None
		self.nameDict = {}
		self.messagesid = {}
		self.attachment = {}
		self.models = []
		
	def parse(self):
		self.db = SQLiteParser.Database.FromNode(self.node)
		if self.db is None:
			return []
		self.senders()
		self.messages()
		self.attachments()
		self.buildvoicemail()
		return self.models

	def senders(self):
		for myNames in self.db['senders']:
			self.nameDict[myNames['sender_id'].Value] = myNames['sender_name'].Value
	
	def messages(self):
		for row in self.db['messages']:
			self.messagesid[row['id'].Value] = (row['date'].Value,row['sender_list'].Value,row['length'].Value)
	
	def attachments(self):
		for row in self.db['attachments']:
			self.attachment[row['id'].Value] = (row['message_id'].Value,row['content_uri'].Value)
	
	def duration(self,time):
		mins, secs = divmod(time,60)
		hours, mins = divmod(mins,60)
		return TimeSpan(hours,mins,secs)
	
	def getvm(self,path):
		filepath = path.split('/',3)[3].replace('%40','@')
		filepath = filepath.split('/')
		vmpath = self.dirpath+"/"+filepath[0]+'_att'+"/"+filepath[1]
		print vmpath
		for fs in ds.FileSystems:
			for f in fs.Search(vmpath):
				return f
		
	
	def buildvoicemail(self):
		for rec in self.attachment:
			vm = Voicemail()
			pa = Party()
			vm.Deleted = DeletedState.Intact
			vm.Timestamp.Value = TimeStamp.FromUnixTime(int(self.messagesid.get((self.attachment.get(rec)[0]))[0])/1000)
			mins,secs = divmod(self.messagesid.get((self.attachment.get(rec)[0]))[2],60)
			hours, mins = divmod(mins,60)
			vm.Duration.Value = self.duration(self.messagesid.get((self.attachment.get(rec)[0]))[2])
			vm.Name.Value = self.nameDict.get(self.messagesid.get((self.attachment.get(rec)[0]))[1])
			pa.Identifier.Value = self.messagesid.get((self.attachment.get(rec)[0]))[1]
			vm.From.Value = pa
			path = self.getvm((self.attachment.get(rec)[1]))
			vm.Recording.Value = path
			self.models.append(vm)
		
		
path = "/data/com.metropcs.service.vvm/databases"

for fs in ds.FileSystems:
	for folder in fs.Search(path):
		for f in folder:
			if f.AbsolutePath.endswith("@vms.eng.t-mobile.com.db"):
				node = f

results = lgVM(node,path).parse()
ds.Models.AddRange(results)

	