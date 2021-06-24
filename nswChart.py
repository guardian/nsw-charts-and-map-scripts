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

date_index = pd.date_range(start='2020-01-21', end=gp_pvt.index[-1])
	
gp_pvt = gp_pvt.reindex(date_index)

gp_pvt = gp_pvt.fillna(0)

# newData = latest['NSW']

# new_df = pd.DataFrame(newData)
# new_df.date = pd.to_datetime(new_df.date, format="%d-%m-%Y")
# new_df = new_df.set_index('date')
# new_df = new_df.apply(pd.to_numeric)
# new_total = new_df['Total']
# new_df = new_df.drop(['Total'], axis=1)

# new_df['Local and under investigation'] = new_df[["Local, known origin", "Local, unknown origin", "Under investigation"]].sum(axis=1)

# df3 = pd.DataFrame()

# if new_df.index[-1] > gp_pvt.index[-1]:
# 	print("using sheets values")
# 	df3 = pd.concat([gp_pvt, new_df])
# else:
# 	print("ignoring sheets values")
# 	df3 = gp_pvt

# df3 = gp_pvt.append(new_df)
# df3 = df3[~df3.index.duplicated()]	
df3 = gp_pvt.copy()
lastUpdated2 = df3.index[-1]
newUpdated = lastUpdated2 + timedelta(days=1)
newUpdated = newUpdated.strftime('%Y-%m-%d')

df4 = df3.copy()

df3.index = df3.index.strftime('%Y-%m-%d')

df3.to_csv('nsw-local.csv')

#%%

def makeSourceBarsLong(df):

	lastUpdatedInt =  df.index[-1]
	
	template = [
			{
				"title": "Source of Covid-19 infections in NSW",
				"subtitle": "Showing the daily count of new cases by the source of infection. Last updated {date}".format(date=today),
				"footnote": "",
				"source": " | NSW Health",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Cases",
				"timeInterval":"day",
				"tooltip":"TRUE",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "20",
				"margin-bottom": "20",
				"margin-right": "30",
				"xAxisDateFormat": "%b %d",
				"tooltip":"<strong>{{#formatDate}}{{data.index}}{{/formatDate}}</strong><br/> {{group}}: {{groupValue}}<br/>Total: {{total}}<br/>"
			}
		]
	key = [
		{"key":"Local and under investigation","colour":"#d73027"},
		{"key":"Overseas","colour":"#74add1"},
		{"key":"Interstate", "colour":"#f07f16"}
			]
	periods = []

	chartId = [{"type":"stackedbar"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="infection-source-nsw-corona{test}".format(test=test), key=key)

makeSourceBarsLong(df3[["Local and under investigation", "Interstate", "Overseas"]])

#%%

df4['Local and under investigation, 7 day average'] = df4['Local and under investigation'].rolling(7).mean()
df4['Overseas, 7 day average'] = df4['Overseas'].rolling(7).mean()

sixty_days = lastUpdated2 - timedelta(days=60)

df_60 = df4[sixty_days:]
df_60 = df_60.round(2)

df_60.index = df_60.index.strftime('%Y-%m-%d')

#%%

def makeLocalLine(df):

	lastUpdatedInt =  df.index[-1]
	
	template = [
			{
				"title": "Trend in local and overseas-related transmission of Covid-19 in NSW, last 60 days",
				"subtitle": "Showing the 7 day rolling average of locally and overseas-acquired cases, with those under investigation added to the local category. Last updated {date}".format(date=newUpdated),
				"footnote": "",
				"source": "NSW Health",
				"dateFormat": "%Y-%m-%d",
				"yScaleType":"",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"minY": "",
				"maxY": "",
				"x_axis_cross_y":"0",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "30",
				"margin-bottom": "20",
				"margin-right": "10",
				"tooltip":"<strong>{{#formatDate}}{{index}}{{/formatDate}}</strong><br/> Local and under investigation: {{Local and under investigation, 7 day average}}<br/>Overseas: {{Overseas, 7 day average}}<br/>"
			}
		]
	key = []
	periods = []
	labels = []
	options = [{"colorScheme":"guardian"}] 
	chartId = [{"type":"linechart"}]
	df.fillna(0, inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, options=options, data=chartData, chartId=[{"type":"linechart"}], chartName="local-trend-60-days-nsw-corona-2020{test}".format(test=test))


makeLocalLine(df_60[['Local and under investigation, 7 day average','Overseas, 7 day average']])


#%%

local = df[df['likely_source_of_infection'] != "Overseas"]

local_gp = local[['notification_date','lga_name19','count']].groupby(['notification_date','lga_name19']).sum()
local_gp = local_gp.reset_index()

local_gp = local_gp.set_index('notification_date')

lastUpdated = gp_pvt.index[-1]
four_weeks_ago = lastUpdated - timedelta(days=28)

thirty_days = lastUpdated - timedelta(days=30)

short = local_gp[thirty_days:]

short_p = short.pivot(columns='lga_name19', values='count')

map_index = pd.date_range(start=thirty_days, end=lastUpdated)
short_p = short_p.reindex(map_index)

short_p.to_csv('lga-cases.csv')

two_weeks_ago = lastUpdated - timedelta(days=13)
one_week_ago = lastUpdated - timedelta(days=7)

totals = short_p[two_weeks_ago:].sum()

recent_totals = short_p.sum()

totals = totals[totals >= 5]

short_p.fillna(0, inplace=True)
no_negs = short_p

no_negs[short_p < 0] = 0

rolling = no_negs.rolling(7).mean()
rolling.to_csv("rolling.csv")
lga_movement = []

for col in totals.index:
	print(col)
	row = {}
	row['lga'] = col
	row['change'] = rolling.loc[lastUpdated, col] - rolling.loc[one_week_ago, col]
	row['this_week'] = short_p[one_week_ago:][col].sum()
	row['last_week'] = short_p[two_weeks_ago:one_week_ago][col].sum()
	row['weekly_change'] = 	row['this_week'] - row['last_week']
	row['date'] = short_p.index[-1].strftime('%Y-%m-%d')
	row['today'] = today
	lga_movement.append(row)

lga_df_movement1 = pd.DataFrame(lga_movement)

# lga_recent = []

recent_totals = recent_totals.reset_index().rename(columns={"lga_name19": "place", 0: "count" })
recent_totals['date'] = short_p.index[-1].strftime('%Y-%m-%d')
recent_totals['today'] = today
recent_totals.to_json()

#%%

syncData(lga_movement,'2020/07/nsw-corona-map{test}'.format(test=test), "nswChange")

syncData(recent_totals.to_dict('records'),'2020/07/nsw-corona-map{test}'.format(test=test), "recentLocal")