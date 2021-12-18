import pandas as pd
import requests
from yachtCharter import yachtCharter
from datetime import datetime, timedelta
import numpy as np
from syncData import syncData

#%%

pd.options.mode.chained_assignment = None  # default='warn'

url = "https://data.nsw.gov.au/data/dataset/aefcde60-3b0c-4bc0-9af1-6fe652944ec2/resource/21304414-1ff1-4243-a5d2-f52778048b29/download/confirmed_cases_table1_location.csv"
print("Getting", url)
r = requests.get(url)
with open("nsw-new.csv", 'w') as f:
	f.write(r.text)
	
#%%	

today = datetime.today().strftime('%-d %B, %Y')

#%%

test = ""
# test = "-test"	

df = pd.read_csv('nsw-new.csv')

df['count'] = 1


#%%

local = df

local_gp = local[['notification_date','lga_name19','count']].groupby(['notification_date','lga_name19']).sum()
local_gp = local_gp.reset_index()

local_gp = local_gp.set_index('notification_date')
local_gp.index = pd.to_datetime(local_gp.index, format="%Y-%m-%d")

lastUpdated = pd.to_datetime(df['notification_date'].iloc[-1], format="%Y-%m-%d")

# newUpdated = lastUpdated2 + timedelta(days=1)
newUpdated = lastUpdated.strftime('%-d %B %Y')

#%%
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

#%%
long = local_gp["2021-06-10":]
long_p = long.pivot(columns='lga_name19', values='count')
long_p.fillna(0, inplace=True)
long_p[short_p < 0] = 0
long_p_rolling = long_p.rolling(7).mean()

lga_totals = lga_df_movement1.copy()
lga_totals = lga_totals.sort_values(['this_week'], ascending=False)


# shortlist = [
# "Bayside (A)",
# "Blacktown (C)",
# "Burwood (A)",
# "Camden (A)",
# "Campbelltown (C) (NSW)",
# "Canada Bay (A)",
# "Canterbury-Bankstown (A)",
# "Central Coast (C) (NSW)",
# "Cumberland (A)",
# "Fairfield (C)",
# "Georges River (A)",
# "Inner West (A)",
# "Liverpool (C)",
# "Maitland (C)",
# "Newcastle (C)",
# "Northern Beaches (A)",
# "Parramatta (C)",
# "Penrith (C)",
# "Randwick (C)",
# "Ryde (C)",
# "Strathfield (A)",
# "Sutherland Shire (A)",
# "Sydney (C)",
# "The Hills Shire (A)",
# "Waverley (A)",
# "Willoughby (C)",
# "Wollongong (C)"
# ]

long_p_rolling = long_p_rolling[list(lga_totals.lga)]

long_p_rolling.index = long_p_rolling.index.strftime('%Y-%m-%d')

long_stack = long_p_rolling.stack().reset_index().rename(columns={"level_1":"LGA", 0:"Trend in cases"})
long_stack = long_stack.set_index('notification_date')	
long_stack = long_stack.round(2)

#%%

def makeLgaTrend(df):
	
	template = [
			{
				"title": "Trend in cases by LGA in the Sydney Covid outbreak",
				"subtitle": "Showing the seven-day rolling average in daily Covid cases for each LGA with five or more recent cases. Last updated {date}".format(date=newUpdated),
				"footnote": "",
				"source": " | Source: Guardian Australia analysis of NSW Health data",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"timeInterval":"day",
				"tooltip":"<b>{{#nicedate}}notification_date{{/nicedate}}</b><br><b>Cases, 7-day avg:</b> {{Trend in cases}}",
				"periodDateFormat":"",
				"margin-left": "35",
				"margin-top": "5",
				"margin-bottom": "22",
				"margin-right": "22",
				"xAxisDateFormat": "%b %d"
			}
		]
	key = []
	periods = []
	labels = []
	options = [{"numCols":4, "chartType":"line", "height":150, "scaleBy":"group"}]
	chartId = [{"type":"smallmultiples"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template,options=options, data=chartData, chartId=chartId, chartName="nsw-lga-trend-2021")

makeLgaTrend(long_stack)
