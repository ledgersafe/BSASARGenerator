from datetime import datetime
import json


def loadActivities(filename):
    res = {}
    with open(filename, 'r') as f:
        res = json.load(f)
        return (res)
        

