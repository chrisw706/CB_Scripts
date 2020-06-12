#This script parses suggestions.db for eBay search history
from physical import *
import SQLiteParser
#from System.Convert import IsDBNull

#Need to store our path of the database and make it a variable.

path ='/com.ebay.mobile/databases/suggestions.db$'
searched_items= []

#Loops through the fs and fings the file

for fs in ds.FileSystems:
    for node in fs.Search(path):
        #if node.AbsolutePath.endswith('suggestions.db'): 
        f = node

        db = SQLiteParser.Database.FromNode(f)


#Loops through the database table
        for record in db.ReadTableRecords('suggestions'):
            searched = SearchedItem()
            searched.Deleted = DeletedState.Intact
            searched.Source.Value = "eBay Application"    
            searched.TimeStamp.Value = TimeStamp.FromUnixTime(int(record['date'].Value/1000))
            searched.TimeStamp.Source = MemoryRange(record['date'].Source)
            searched.Value.Value = (record ['query']).Value
            searched.Value.Source= MemoryRange(record ['query'].Source)
            searched_items.append(searched)

ds.Models.AddRange(searched_items)
