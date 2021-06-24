#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import requests
from datetime import datetime, timedelta
import numpy as np


#%%

pd.options.mode.chained_assignment = None  # default='warn'

url = "https://data.nsw.gov.au/data/dataset/97ea2424-abaf-4f3e-a9f2-b5c883f42b6a/resource/2776dbb8-f807-4fb2-b1ed-184a6fc2c8aa/download/covid-19-cases-by-notification-date-location-and-likely-source-of-infection.csv"
print("Getting", url)
r = requests.get(url)
with open("nsw.csv", 'w') as f:
	f.write(r.text)
#%%
	
df = pd.read_csv('nsw.csv')	
df['count'] = 1
gp = df[['notification_date','count']].groupby(['notification_date']).sum()
gp['mean_7day'] = gp['count'].rolling(7).mean()
gp.to_csv('nsw-cases.csv')