# 2016
#
# Written to be used with Cellebrite Physical Analyzer
#
# This script adds the Clean Master Call Log and SMS Backup to the Call History and SMS History tables in Cellebrite PA.



from physical import *
import SQLiteParser
from System import TimeSpan
import clr
clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import MessageBox


#search for file -- different phones will have different partition orders

for fs in ds.FileSystems:
	for f in fs.Search('/Root/data/com.cleanmaster.security/databases/cm_backup_sdk_base.db'):
		if f.AbsolutePath.endswith('cm_backup_sdk_base.db'):
			db = SQLiteParser.Database.FromNode(f)


def contacts():


	tableName = "contacts"
	name_col = 'givenname'
	num_col = 'phone'
	email_col = 'email'


	contacts_count = 0


	for record in db.ReadTableRecords(tableName):
		cont = Contact()
		ph = PhoneNumber()
		em = EmailAddress()

		cont.Source.Value = "CleanMaster App"
		cont.Deleted = DeletedState.Unknown #just going with Unknown since these are only found in the CM App
		cont.Name.Value = record[name_col].Value
		if cont.Name.Value != '': #if I don't check for zero-length, the next line will fail on a few records
			cont.Name.Source = MemoryRange(record[name_col].Source[0])        

		
		ph.Value.Value =  record[num_col].Value[:-3]
		
		if ph.Value.Value != '': #if I don't check for zero-length, the next line will fail on a few records
			ph.Deleted = DeletedState.Unknown
			ph.Category.Value = 'Phone'            
			ph.Value.Source = MemoryRange(record[num_col].Source[0])
		
		
		em.Value.Value = record[email_col].Value[:-5]
		if em.Value.Value != '': #Same as above
			em.Deleted = DeletedState.Unknown  #Same as Above
			em.Category.Value = 'Email'            
			em.Value.Source = MemoryRange(record[email_col].Source[0])


		cont.Entries.Add(ph)
		cont.Entries.Add(em)
		ds.Models.Add(cont)
		contacts_count += 1
	MessageBox.Show('Added ' + str(contacts_count) + ' contact records from the CleanMaster App.', 'Records added from CleanMaster App DB.')
	
def calllog():  #Still working on this part of the script


	tableName = "calllog"
	name_col = '_name'
	num_col = 'number'
	type_col = '_type'
	dur_col = 'duration'
	ts_col = '_date'

	
	call_count = 0
			

	for record in db.ReadTableRecords(tableName):
		pa = Party()
		ca = Call()
		ca.Source.Value = "CleanMaster App"
		ca.Deleted = DeletedState.Unknown #just going with Unknown since these are only found in the CM App

		if record[num_col].Value != '':
			pa.Identifier.Value = record[num_col].Value
			pa.Identifier.Source = MemoryRange(record[num_col].Source[0])
		else:
			pa.Identifier.Value = ''

		pa.Name.Value = record[name_col].Value
		if pa.Name.Value != '': #if I don't check for zero-length, the next line will fail on a few records
			pa.Name.Source = MemoryRange(record[name_col].Source[0])
		
		if record[type_col].Value == '1':
			pa.Role.Value = PartyRole.From
			ca.Type.Value = CallType.Incoming
		elif record[type_col].Value == '2':
			pa.Role.Value = PartyRole.To
			ca.Type.Value = CallType.Outgoing
		elif record['_type'].Value == '3':
			pa.Role.Value = PartyRole.From
			ca.Type.Value = CallType.Missed
		pa.Role.Source = MemoryRange(record['_type'].Source[0])
		
		ca.Duration.Value = TimeSpan (0, 0, int(record['duration'].Value))
		ca.Duration.Source = MemoryRange(record['duration'].Source[0])
		
		ca.TimeStamp.Value = TimeStamp.FromUnixTime(int(record['_date'].Value) / 1000)
		ca.TimeStamp.Source = MemoryRange(record['_date'].Source[0])

		ca.Parties.Add(pa)
		ds.Models.Add(ca)
		call_count += 1
	MessageBox.Show('Added ' + str(call_count) + ' call records from the CleanMaster App.', 'Records added from CleanMaster App DB.')
	

def sms():

				
	tableName = "sms"
	name_col = '_name'
	num_col = 'address'
	type_col = '_type'
	msg_col = 'body'
	ts_col = '_date'
			
	sms_count = 0	

	for record in db.ReadTableRecords(tableName):
		pa = Party()
		sms = SMS()
		sms.Source.Value = "CleanMaster App"
		sms.Deleted = DeletedState.Unknown #just going with Unknown since these are only found in the CM App
		sms.Body.Value = record[msg_col].Value
		sms.TimeStamp.Value = TimeStamp.FromUnixTime(int(record[ts_col].Value) / 1000)
		pa.Identifier.Value = record[num_col].Value		
		
		pa.Name.Value = record[name_col].Value
		if pa.Name.Value != '': #if I don't check for zero-length, the next line will fail on a few records
			pa.Name.Source = MemoryRange(record[name_col].Source[0])
		
		if record[type_col] == 1:
			pa.Role.Value = PartyRole.From
			sms.Folder.Value = 'Inbox'
		elif record[type_col] == 2:
			pa.Role.Value = PartyRole.To
			sms.Folder.Value = 'Sent'
		else:
			pa.Role.Value = PartyRole.General
			sms.Folder.Value = 'Unknown'	
			
		sms.Parties.Add(pa)
		ds.Models.Add(sms)
		sms_count += 1
	MessageBox.Show('Added ' + str(sms_count) + ' sms records from the CleanMaster App.', 'Records added from CleanMaster App DB.')

sms()
calllog()
contacts()

