import json
import pendulum
import calendar
from meteocalc import heat_index
import numpy as np

import urllib, json

#print data
#import pandas as pd

#t=pendulum.create(2014,9,18,12,00,00,tz='EST')
#ut=calendar.timegm(t.utctimetuple())
##outputs 1411059600

#to go backwards
#q=pendulum.from_timestamp(1411059600,'EST')
def get_forecast():
    #unix_tstamp=calendar.timegm(pendulum.now().utctimetuple())

    #adding this is a time machine request avoid for realtime forecasts, no need for unix timestmap
    #url='https://api.darksky.net/forecast/32cd2be3e8e674975b2e987ab7ee16b6/40.7829,-73.9654,'+str(unix_tstamp)
    url='https://api.darksky.net/forecast/32cd2be3e8e674975b2e987ab7ee16b6/40.7829,-73.9654'



    response = urllib.urlopen(url)
    d = json.loads(response.read())
    #with open('https://api.darksky.net/forecast/32cd2be3e8e674975b2e987ab7ee16b6/40.7829,-73.9654,141105960') as json_data:
    #with open('40.7829,-73.9654,1489503600') as json_data:
        #d = json.load(json_data)
        #print(d)
    forecasts=d['hourly']['data']
    forecasts=forecasts[0:24]

    #temperature,rh,rain
    #timestamp=[]
    #temperature=[] #in F
    #rh=[] #0-1
    ##rain=[] #in/hr
    #fractionalhour,dayofweek,month1505962085
    values=[]
    #need to get into this format
    #keys=['day_of_week','weeks','hr','stop_id','heat_index']
    for forecast in forecasts:
        T=pendulum.from_timestamp(forecast['time'],'America/New_York')
        #print T
        day_of_week=T.weekday()
        month=T.month
        fractionalhour=T.hour+(T.minute/60.)+(T.second/3600.)
        temperature=(float(forecast['temperature']))
        rh=(float(forecast['humidity']))
        rain=(float(forecast['precipIntensity']))
        HI=float(heat_index(temperature,rh))
        #bug in t.week_of_year
        values.append([day_of_week,T.week_of_year, fractionalhour, 1 ,HI,])
        #this has been customized for h

    return np.array(values)

#df=pd.read_json('https://api.darksky.net/forecast/32cd2be3e8e674975b2e987ab7ee16b6/40.7829,-73.9654,1411059600')
#https://api.darksky.net/forecast/32cd2be3e8e674975b2e987ab7ee16b6
