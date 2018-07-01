import requests
import time
#url="https://api.coindesk.com/v1/bpi/currentprice.json"
url = "https://www.bitstamp.net/api/ticker/"

print('date,close')
f = open("data/new.csv","a")
#f.write("date,close\n")
while [ 1 ]:
   r = requests.get(url)
   rd = r.json()
   d = rd['timestamp']
   p = rd['ask']
   data = d+","+p+"\n"
   f.write(data)
   print(d,',', p)
   time.sleep(1)

f.close()

