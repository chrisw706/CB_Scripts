from physical import *
import re
from binascii import hexlify


class SkimmerData:

    def __init__(self,node, mem):
        self.node = node
        self.mem = mem
        self.entry = 0
        self.location = 0
        self.enbedded_entry = []
        self.credit_cards = []

    def parse(self):
        length = 0x100
        v = 0
        run = True
        while run == True: #v < 10:
            chunk = self.mem.read(length)
            if chunk[1:3] == 'T1' or chunk[2:4] == 0x0042 or chunk[4:6] == 0x0042:        
                self.entry += 1
                print(self.entry)
                f = Node('track_entry_{0}'.format(self.entry), NodeType.File | NodeType.Embedded)
                f.Deleted = DeletedState.Intact
                f.Data = self.mem.GetSubRange(self.location, length)
                v +=1
                self.location += length
                self.enbedded_entry.append(f)
                number = self.card(chunk)
                name = self.ccname(chunk)
                
                if number != 'No Card':
                    bank = self.get_bank(number)
                    cc = CreditCard()
                    cc.Deleted = DeletedState.Intact
                    cc.CreditCardNumber.Value = number
                    if name != 'Invalid Name Format':
                        cc.NameOnCard.Value = name
                    if bank != 'No Bank':
                        cc.Company.Value = bank
                    self.credit_cards.append(cc)
            if len(chunk) < 100:
                run = False
        
        return self.enbedded_entry, self.credit_cards
        
    def card(self, chunk):
        if chunk[1:3] == "T1":
            card_number = re.findall('(%B)([0-9]*?)(\^)', chunk)
            if len(card_number) > 0:
                card_number = card_number[0][1]
            else:
                card_number = "No Card"
            return card_number
        elif hexlify(chunk[2:4]) == '0042' or hexlify(chunk[4:6]) == '0042': 
            card_number = re.findall('(B)([0-9]*?)(\^)', chunk)
            if len(card_number) > 0:
                card_number = card_number[0][1]
            else:
                card_number = "No Card"
            return card_number
        else:
            return "No Card"
    
    def ccname(self, chunk):
        if chunk[1:3] == "T1" or hexlify(chunk[2:4]) == '0042' or hexlify(chunk[4:6]) == '0042':
            name = re.findall('(\^)(.*?)(\^)',chunk)
            if len(name) > 0:
                name = name[0][1].rstrip()
            else:
                name = 'Invalid Name Format'
            return name
    
    def get_bank(self,number):
        try:
            response = requests.get('https://lookup.binlist.net/'+number[0:6])
            json_data = json.loads(response.text)        
            return json_data['bank']['name']
        except:
            return 'No Bank'



mem = ds.MemoryRanges[0]
node = ds.FileSystems[0].Children[0]
data = SkimmerData(node,mem)
entries, cc = data.parse()
node.Children.AddRange(entries)
ds.Models.AddRange(cc)