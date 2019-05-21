from datetime import datetime
import json

tinfo = {}
#tinfo 
with open("./t.json", 'r') as f:
    tInfo = json.load(f)
    print(type(tInfo))


print(tInfo[0]['PackageId'])


for i, t in enumerate(tInfo):
    print(i, t)
