from physical import *

import time
import tempfile
import calendar

import clr
clr.AddReference('Microsoft.Office.Interop.Excel')
from Microsoft.Office.Interop.Excel import ApplicationClass


def create_cord(lat,long):
    l = Location()
    c = Coordinate()
    c.Deleted = DeletedState.Intact
    c.Longitude.Value = long
    c.Latitude.Value = lat
    l.Position.Value = c
    l.Deleted = DeletedState.Intact
    return l

def split_waypoints(url):
    
    locs = []
    string = url.split('/dir/')[1].replace('@','').replace(',15z','')
    cords = [[cor for cor in item.split(',')] for item in string.split('/')]
    
    for item in cords:
        loc = create_cord(float(item[0]),float(item[1]))
        locs.append(loc)
    
    return locs

fs = ds.FileSystems[0]
node = fs['renishaleblanc96@icloud.com_14-11-54_SW (1) - ORIGINAL.xlsx']
data = node.read()
tempf = tempfile.NamedTemporaryFile()
tempf.write(data)

excel = ApplicationClass()
ex = excel.Workbooks.Open(tempf.name)
ws = ex.Worksheets[4]
rows = ws.Range['A2','DM22']

for item in range(1,ws.Rows.Count+1):
    # Instantiate Class
    j = Journey()
    j.Name.Value = rows.Cells(item,1).text
    j.Deleted = DeletedState.Intact
    
    #Start and End time
    j.StartTime.Value = TimeStamp.FromUnixTime(calendar.timegm(time.strptime(rows.Cells(item,4).text, "%Y-%m-%dT%H:%M:%SZ"))+25200)
    j.EndTime.Value = TimeStamp.FromUnixTime(calendar.timegm(time.strptime(rows.Cells(item,8).text, "%Y-%m-%dT%H:%M:%SZ"))+25200)
    j.FromPoint.Value = create_cord(float(rows.Cells(item,6).text),float(rows.Cells(item,7).text))
    j.ToPoint.Value = create_cord(float(rows.Cells(item,10).text),float(rows.Cells(item,11).text))
    
    #call function to split waypoints
    points = split_waypoints(rows.Cells(item,20).text)
    #Adds all the waypoints to the Joirney
    j.WayPoints.AddRange(points)
    j.WayPointCount = len(points)
    #Add the Journey to DataStore
    ds.Models.Add(j)
    
#Close the file
tempf.close()

