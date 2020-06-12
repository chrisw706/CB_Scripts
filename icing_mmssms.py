#Written by Chris Weber -----Ctrl_Klick Forensics
#chrisw706@gmail.com

# Parser for the SMS and MMS in the icing_mmssms.db

# These imports are not all needed yet to parse the DB, but I plan on updating to carve
# for addition messages that are not in the database later but still part of the file
# so I'm gonna leave then there for now, but comment them out so they do not load.

from physical import*
import SQLiteParser
from System.Convert import IsDBNull
import clr
clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import MessageBox
# import re
# from binascii import hexlify

#These are counters to give you a total
total_count = 0
smsadded_count = 0
duplicate_sms = 0
mmsadded_count = 0
duplicate_mms = 0


# Gets the phone number for the device.  We need this for adding to 
# MMS table	
for row in ds.Models[User]:
	if str(row.UserType.Value) == 'Owner':
		phoneNumber = row.Name.Value
	else:
		phoneNumber = ""

# The below section creates a list of already parsed sms messages so
# as we pull new messages out of the database it will not duplicate those in the sms table
# It's not a perfect deduplicator but it works better than nothing.

sms_list = []

for sms in ds.Models[SMS]:
	time = str(sms.TimeStamp.Value)
	body = sms.Body.Value
	try:
		party = (str(sms.Parties).split(' '))
	except:
		party = " "
	try:
		party = (party[1])[-10:]
	except:
		party = " "
	try:
		sms_list.append(time + " " + body+ " " + party)
	except:
		continue
		
# The below section creates a list of already parsed mms messages so
# as we pull new messages out of the database it will not duplicate those in the mms table
#This is not quite working yet. 

mms_list = []
for mms in ds.Models[MMS]:
	time = str(mms.TimeStamp.Value)
	#body = str(mms.Body.Value)
	#if body == "":
	#	body = " "
	if mms.To == phoneNumber:
		party = (str(a.From).split(' ')[0])[-10:]
	else:
		party = (str(mms.To))[-10:]
	mms_list.append(time + " " + party)


# This is the start of the database parser.  It searches throught the file system 
# and sets the variable file as the icing_mmssms.db.  There is a journal file also for this database
# so we need to make sure we are only parsing the database.  Later when this is written to 
# carve we can carve the journal file.
 		
filePath = '/Root/data/com.google.android.gms/databases/icing_mmssms.db'
#Searches through the partitions and looks for the icing_mmssms.db.  
for fs in ds.FileSystems:
	for file in fs.Search(filePath):
		if file.AbsolutePath.endswith('icing_mmssms.db'):
			db = SQLiteParser.Database.FromNode(file)


#Search through the phone and sets the path for the mmssms database so that we can 
#get the path of the mms attachment
filePath2 = '/Root/data/com.android.providers.telephony/databases/mmssms.db'

for fs in ds.FileSystems:
	for file in fs.Search(filePath2):
		if file.AbsolutePath.endswith('mmssms.db'):
			db2 = SQLiteParser.Database.FromNode(file)

			

for record in db.ReadTableRecords('mmssms'):
	
	total_count += 1

	
	# This if statment checks to see in the messgage is an sms or mms.
	# If it is an sms it will parse it.  If it is not it will skip it and go to the mms part of the code.
	
	if record['msg_type'].Value == 'sms':
		
		pa = Party()
		sms = SMS()
		
		# Parses the TimeStamp
		sms.TimeStamp.Value = TimeStamp.FromUnixTime(int(record['date'].Value)/1000)
		
		# Parses the Body of the Message
		if IsDBNull(record['body'].Value):
			sms.Body.Value = ""
		else:
			sms.Body.Value = record['body'].Value
		
		# Parses the other recipient of the conversation
		if IsDBNull(record['address'].Value):
			pa.Identifier.Value = ""
		else:
			pa.Identifier.Value = str(record['address'].Value)
		
		numValue = pa.Identifier.Value[-10:]
		
		# This is what does the second part of the deduplicator.
		# It foramts the messages in the database to the same format as the
		# parts we pulled out earlier.
		dd = str(sms.TimeStamp.Value) + " " + sms.Body.Value + " " + numValue
		
		# This is the third part of the deduplicator it does the actuall comparing the
		# the list of messages.
		if dd in sms_list:
			duplicate_sms += 1
			continue

		else:
			smsadded_count += 1
			sms_list.append(dd)
			
			if record['type'].Value == 1:
				pa.Role.Value = PartyRole.From
				sms.Folder.Value = "Inbox"			
			elif record['type'].Value == 2 or record['type'].Value == 4 or record['type'].Value == 6:
				pa.Role.Value = PartyRole.To
				sms.Folder.Value = "Sent"
			elif record['type'].Value == 3:
				pa.Role.Value = PartyRole.To
				sms.Folder.Value = "Draft"
			else:
				sms.Folder.Value = "Unknown"
						
			sms.Source.Value = "com.google.android.gms/databases/icing_mmssms.db"
			
			# I'm putting deleted state as unknown because the deduplicator is not perfect
			# If the message is not a duplicate in the SMS table then it has been deleted.  
			# If it is duplicate the it is not deleted.
			sms.Deleted = DeletedState.Unknown
			
			  
			sms.Parties.Add(pa)
			ds.Models.Add(sms)
		
		
	elif record['msg_type'].Value == 'mms':
				
		mms = MMS()
		to = Party()
		fr = Party()
		att = Attachment()
		pic_path = 'No Attachment'
		
		
		
		if IsDBNull(record['body'].Value):
			pass
		else:
			mms.Body.Value = record['body'].Value
				
		# Parses the other recipient of the conversation
		if IsDBNull(record['address'].Value):
			pass
		else:	
			numValue = str(record['address'].Value)

		if IsDBNull(record['subject'].Value):
			pass
		else:
			mms.Subject.Value = record['subject'].Value
			
			#Adding the telephone numbers in the To and From colums
		if record['type'].Value == 1:
			fr.Identifier.Value = str(record['address'].Value)
			mms.From.Value = fr
			mms.Folder.Value = "Inbox"
			to.Identifier.Value = phoneNumber
			mms.To.Add(to)
		elif record['type'].Value == 2 or record['type'].Value == 4 or record['type'].Value == 6:
			fr.Identifier.Value = phoneNumber
			mms.From.Value = fr
			mms.Folder.Value = "Sent"
			to.Identifier.Value = str(record['address'].Value)
			mms.To.Add(to)
		elif record['type'].Value == 3:
			fr.Identifier.Value = phoneNumber
			mms.From.Value = fr
			mms.Folder.Value = "Draft"
			to.Identifier.Value = str(record['address'].Value)
			mms.To.Add(to)
		else:
			mms.Folder.Value = "Unknown"
						
		mms.Source.Value = "com.google.android.gms/databases/icing_mmssms.db"
			
			# I'm putting deleted state as unknown because the deduplicator is not perfect
			# If the message is not a duplicate in the SMS table then it has been deleted.  
			# If it is duplicate the it is not deleted.
		mms.Deleted = DeletedState.Unknown
			
		#  This gets the attachment number from the icing .db2
		

		if IsDBNull(record['media_uri'].Value):
			pass
		else:
			attPath = record['media_uri'].Value
			icingPartId = attPath.split('/')[-1]
			print icingPartId 
			
			for record in db2.ReadTableRecords('part'):
				if  icingPartId == str(record['_id'].Value):
					pic_path = record['_data'].Value
				else:
					pass
					
		# This gets the file and adds the picture to the attachment window
		# and the attchment file name
		
		if pic_path != "No Attachment":
			pic_path = pic_path.split('/', 4)[-1]
			pic_path = "/Root/data/"+pic_path
			for fs in ds.FileSystems:
				for file in fs.Search(pic_path):
					pic_file = file.Data				
					att.Data.Source = pic_file
					att.Filename.Value = pic_path.split('/')[-1]
					mms.Attachments.Add(att)
		
		# Adds the mms to the data store
		mmsadded_count += 0
		ds.Models.Add(mms)
			
			
			
			
MessageBox.Show('Total Messages in Database:  ' + str(total_count)+'\nTotal SMS added to table: ' + str(smsadded_count) + '\nTotal Duplicate SMS not added to table: ' + str(duplicate_sms)+ '\nTotal MMS Messages added to table: '+ str(mmsadded_count ) +'\nTotal Duplicate MMS not added to table: Not working yet') #+ str(duplicate_mms)) 
