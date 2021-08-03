#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import requests
from yachtCharter import yachtCharter
from datetime import datetime, timedelta
import numpy as np
from syncData import syncData

#%%

pd.options.mode.chained_assignment = None  # default='warn'

url = "https://data.nsw.gov.au/data/dataset/97ea2424-abaf-4f3e-a9f2-b5c883f42b6a/resource/2776dbb8-f807-4fb2-b1ed-184a6fc2c8aa/download/covid-19-cases-by-notification-date-location-and-likely-source-of-infection.csv"
print("Getting", url)
r = requests.get(url)
with open("nsw.csv", 'w') as f:
	f.write(r.text)
	
#%%

latest = requests.get('https://interactive.guim.co.uk/docsdata/1XeCK-B3eOKKfN-BCXbV0Ln46_xT7jE6ozTAJ7pAPRvo.json').json()['sheets']

#%%	

today = datetime.today().strftime('%-d %B, %Y')

#%%

test = ""
# test = "-test"	

df = pd.read_csv('nsw.csv')

def combine(row):
	if row['likely_source_of_infection'] == "Locally acquired - linked to known case or cluster":
		return "Local, known origin"
	elif row['likely_source_of_infection'] == "Locally acquired - no links to known case or cluster" or row['likely_source_of_infection'] == "Locally acquired - investigation ongoing":
		return "Local, unknown origin"
	elif row['likely_source_of_infection'] == "Overseas":
		return "Overseas"
	elif row['likely_source_of_infection'] == "Interstate":
		return "Interstate"

df['combined'] = df.apply(combine, axis=1)
df['count'] = 1
df['notification_date'] = pd.to_datetime(df['notification_date'], format="%Y-%m-%d")

gp = df[['notification_date','combined','count']].groupby(['notification_date','combined']).sum()

gp_pvt = gp.reset_index().pivot(index='notification_date', columns='combined', values='count')

gp_pvt['Local and under investigation'] = gp_pvt[["Local, known origin", "Local, unknown origin"]].sum(axis=1)

date_index = pd.date_range(start='2020-07-01', end=gp_pvt.index[-1])
	
gp_pvt = gp_pvt.reindex(date_index)

gp_pvt = gp_pvt.fillna(0)

#%%

newData = latest['NSW']

new_df = pd.DataFrame(newData)
new_df.date = pd.to_datetime(new_df.date, format="%d-%m-%Y")
new_df = new_df.set_index('date')
new_df = new_df.apply(pd.to_numeric)
new_total = new_df['Total']
new_df = new_df.drop(['Total'], axis=1)

new_df['Local and under investigation'] = new_df[["Local, known origin", "Local, unknown origin", "Under investigation"]].sum(axis=1)

new_df = new_df["2021-07-01":]

#%%

unknowns = pd.DataFrame()
unknowns['Daily'] = new_df['Local, unknown origin']
unknowns['Adjusted'] = gp_pvt['Local, unknown origin']

if pd.isna(unknowns['Adjusted'].iloc[-1]):
	unknowns['Adjusted'].iloc[-1] = unknowns['Daily'].iloc[-1]
# unknowns['Adjusted'].iloc[-2] = unknowns['Daily'].iloc[-2]
unknowns['Difference'] = unknowns['Daily'] - unknowns['Adjusted']

total_unknowns_daily = unknowns['Daily'].sum()
total_unknowns_adjusted = unknowns['Adjusted'].sum()

lastUpdated = unknowns.index[-1]
updatedText = lastUpdated.strftime('%-d %B, %Y')

resolved = total_unknowns_daily - total_unknowns_adjusted
unknowns.index = unknowns.index.strftime('%Y-%m-%d')

unknowns_stack = unknowns.stack().reset_index().rename(columns={"level_1":"category", 0:"count"})
unknowns_stack = unknowns_stack.set_index('date')


#%%

def makeUnknownsChart(df):
	
	template = [
			{
				"title": "How many cases with an unknown transmission source are resolved?",
				"subtitle": "Last updated {date}".format(date=updatedText),
				"footnote": "",
				"source": " | Source: NSW Health, Guardian Australia",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"timeInterval":"day",
				"tooltip":"",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "5",
				"margin-bottom": "22",
				"margin-right": "25",
				"xAxisDateFormat": "%b %d"
			}
		]
	key = []
	periods = []
	labels = []
	options = [{"numCols":1, "chartType":"bar", "height":70}]
	chartId = [{"type":"smallmultiples"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template,options=options, data=chartData, chartId=chartId, chartName="nsw-cases-unknown-updates-2021")

makeUnknownsChart(unknowns_stack)


#%%
# df3 = pd.DataFrame()

# if new_df.index[-1] > gp_pvt.index[-1]:
# 	print("using sheets values")
# 	df3 = pd.concat([gp_pvt, new_df])
# else:
# 	print("ignoring sheets values")
# 	df3 = gp_pvt