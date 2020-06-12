from physical import *
from FileFormatParsers.KTree import KTreeFactory, KNodeTools

fs = ds.FileSystems[0]
node = fs['cheyjulia22@gmail.com.locationhistory.json']

js = KTreeFactory.ParseJson(node)

location_list = []
for entry in js['locations']:
    
    location = Location()
    location.Position.Value = Coordinate(float(entry['latitudeE7'].Value)/10000000,float(entry['longitudeE7'].Value)/10000000)
    location.TimeStamp.Value = TimeStamp.FromUnixTime(int(entry['timestampMs'].Value)/1000)
    location_list.append(location)




ds.Models.AddRange(location_list)
    

