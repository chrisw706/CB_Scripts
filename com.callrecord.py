# 2018

#Written by Chris Weber -----Ctrl_Klick Forensics
#chrisw706@gmail.com
#
# Written to be used with Cellebrite Physical Analyzer
#
# This script parses the callrecorder app and creates an HTML report with link to audio files.

from physical import *
from System.Convert import IsDBNull
import SQLiteParser
import clr, os
clr.AddReference("System.Drawing")
clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import *
from System.Drawing import Point
import time

time = time.strftime(".%m-%d-%Y.%H-%M")
listofNumbers =[]
report_info = []
newRecord = []

def report_creator():

	Save_Location = os.path.expanduser('~')
	
	HTMLReport = open(Save_Location +'\\Documents\My Reports\\CallRecorder'+time+'\\CallRecorder.html', 'wb')      
	HTMLReport.write('''<html>\n''')
	HTMLReport.write('''<body style ="background-color:#B6B8BD;">\n''')
	HTMLReport.write('''<head>\n''')
	HTMLReport.write('''<style>\n''')
	HTMLReport.write('''header {\n''')
	HTMLReport.write('''border: 3px solid black;\n''')
	HTMLReport.write('''    padding: 1em;\n''')
	HTMLReport.write('''    color:Black;\n''')
	HTMLReport.write('''    text-align: Left;\n''')
	HTMLReport.write('''    line-height: 0;\n''')
	HTMLReport.write('''	background: #284FB2;\n''')
	HTMLReport.write('''}\n''')
	HTMLReport.write('''table {\n''')
	HTMLReport.write('''    font-family: arial, sans-serif;\n''')
	HTMLReport.write('''    border: "3" px solid #dddddd;\n''')
	HTMLReport.write('''    width: 100%;\n''')
	HTMLReport.write('''}\n''')
	HTMLReport.write('''\n''')
	HTMLReport.write('''td, th {\n''')
	HTMLReport.write('''    border: "3" px solid #dddddd;\n''')
	HTMLReport.write('''    text-align: left;\n''')
	HTMLReport.write('''    padding: 8px;\n''')
	HTMLReport.write('''}\n''')
	HTMLReport.write('''\n''')
	HTMLReport.write('''tr:nth-child(odd) {\n''')
	HTMLReport.write('''    background-color: #dddddd;\n''')
	HTMLReport.write('''}\n''')
	HTMLReport.write('''</style>\n''')
	HTMLReport.write('''</head>\n''')
	HTMLReport.write('''<body>\n''')
	HTMLReport.write('''<header>\n''')
	HTMLReport.write('''<h4>Investigator:     '''+report_info[0][0]+'''</h4>\n''')
	HTMLReport.write('''<h4>Agency:           '''+report_info[0][1]+'''</h4>\n''')
	HTMLReport.write('''<h4>Case Number:      '''+report_info[0][2]+'''</h4>\n''')
	HTMLReport.write('''<h4>Evidence Item:    '''+report_info[0][3]+'''</h4>\n''')
	HTMLReport.write('''<h4>Application:      '''+report_info[0][4]+'''</h4>\n''')
	HTMLReport.write('''<h4>Database Name:    '''+report_info[0][5]+'''</h4>\n''')
	HTMLReport.write('''</header>\n''')
	HTMLReport.write('''<h2>Summary of Recorded Phone Calls</h2>\n''')
	HTMLReport.write('''<table border="3" style="width:100%"><tr><th>Contact Name</th><th>Phone Number</th><th>Creation Time</th><th>File Path</th><th>File Name</th></tr>\n''')        
	for item in newRecord:
		HTMLReport.write('''<tr><td>'''+item[0]+'''</td><td>'''+item[1]+'''</td><td>''' +item[2]+ '''</td><td>''' +item[3]+ '''</td><td><a href = "Audio/'''+item[4]+ '''" TARGET = "_blank">''' +item[5]+ '''</a></td></tr>\n''')
	HTMLReport.write('''</table>''')
	HTMLReport.write('''</Body></html>\n''')
	HTMLReport.close()
	os.startfile(Save_Location +'\\Documents\My Reports\\CallRecorder'+time+'\\CallRecorder.html')

def appParser():
	path = '/apps/com.callrecord.auto/db/call_recorder'

  
	for fs in ds.FileSystems:
		for file in fs.Search(path):
			if file.AbsolutePath.endswith('call_recorder'):
				db = SQLiteParser.Database.FromNode(file)
	
	Save_Location = os.path.expanduser('~')
	os.makedirs(Save_Location+'\\Documents\My Reports\\CallRecorder'+time+'\\Audio')
	

	
	for record in db.ReadTableRecords('call_table'):
		
		if IsDBNull(record['phone'].Value):
			baseNumber = " "
		else:
			baseNumber = str(record['phone'].Value)
		
		if baseNumber == " ":
			pass
			
		elif baseNumber[-10:] in listofNumbers[0] or listofNumbers[0][0] == "":
			
			if IsDBNull(record['name'].Value):
				ContactName = ""
			else:
				ContactName = str(record['name'].Value)
				
			if IsDBNull(record['phone'].Value):
				phoneNumber = " "
			else:
				phoneNumber = str(record['phone'].Value)
						
			if IsDBNull(record['created_at'].Value):
				createtime = ""
			else:
				createtime = str(record['created_at'].Value)
				
			if IsDBNull(record['link'].Value):
				audioPath = ""
			else:
				audioPath = str(record['link'].Value)
				
			if IsDBNull(record['file_name'].Value):
				fName = ""
			else:
				fName = str(record['file_name'].Value)
				
			if fName.startswith('*'):
				mediafile = "&_42;"+fName[1:]
				audioPath = '/sdcard/Recorders/'+mediafile
				newmediafilename = "_" + fName[1:]
			else:
				mediafile = fName
				audioPath = '/sdcard/Recorders/'+mediafile
				newmediafilename = fName
				
			newRecord.append([ContactName,phoneNumber,createtime,audioPath,newmediafilename,fName])
				
			for fs2 in ds.FileSystems:
				for file2 in fs2.Search(audioPath):
					if file2.AbsolutePath.endswith(mediafile):
						picfile = file2.read()
						image = open(Save_Location +'\\Documents\My Reports\\CallRecorder'+time+'\\Audio\\' + newmediafilename, 'wb')
						image.write(picfile)
						image.close()
			
		else:
			pass

	report_creator()


def update(sender,event):

	investigator = text1.Text
	agency = text2.Text
	caseNumber = text3.Text
	evidenceNumber = text4.Text
	appName = "Call Recorder"
	database = "com.callrecorder.auto"
	listofNumbers.append((text5.Text).split(',' or " "))
	report_info.append([investigator,agency,caseNumber,evidenceNumber,appName,database])
	form.Close()
	appParser()
	
	
form = Form(Text="Custom Report Creater - Python in Cellebrite PA")
form.Width = 600
form.Height = 300


label1 = Label(Text="Enter Investigator Name:")
label1.Location = Point(10,23)
label1.Width = 180
text1 = TextBox()
text1.Location = Point(250,20)
text1.Width = 290
text1.Text = ""

label2 = Label(Text="Enter Agency:")
label2.Location = Point(10,53)
label2.Width = 180
text2 = TextBox()
text2.Location = Point(250,50)
text2.Width = 290
text2.Text = ""

label3 = Label(Text="Enter Case Number:")
label3.Location = Point(10,83)
label3.Width = 180
text3 = TextBox()
text3.Location = Point(250,80)
text3.Width = 290
text3.Text = ""


label4 = Label(Text="Enter Evidence Item #:")
label4.Location = Point(10,113)
label4.Width = 180
text4 = TextBox()
text4.Location = Point(250,110)
text4.Width = 290
text4.Text = ""

label5 = Label(Text="Enter Recorded Phone Number(s):\nEach Number need to be seperated\nby a comma or leave blank \nto export all.")
label5.Location = Point(10,147)
label5.Width = 230
label5.Height = 70

text5 = TextBox()
text5.Location = Point(250,140)
text5.Width = 290
text5.Height = 70
text5.Multiline = True
text5.WordWrap = True
text5.ScrollBars = ScrollBars.Vertical
text5.Text = ""

button1 = Button()
button1.Text = 'Create Report'
button1.Location = Point(250,220)
button1.Click += update

AcceptButton = button1

form.Controls.Add(label1)
form.Controls.Add(text1)
form.Controls.Add(label2)
form.Controls.Add(text2)	
form.Controls.Add(label3)
form.Controls.Add(text3)
form.Controls.Add(label4)
form.Controls.Add(text4)
form.Controls.Add(label5)
form.Controls.Add(text5)
form.Controls.Add(button1)	

Application.Run(form)




	



