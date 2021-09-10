#%%

import os
import requests
import pandas as pd
from yachtCharter import yachtCharter
import datetime

chart_key = "oz-covid-icu-capacity"

here = os.path.dirname(__file__)
data_path = os.path.dirname(__file__) + "/data/"
output_path = os.path.dirname(__file__) + "/output/"

df = pd.read_json('covid-live.json')

# 'REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'NAME', 'CASE_CNT',
#        'TEST_CNT', 'DEATH_CNT', 'RECOV_CNT', 'MED_ICU_CNT', 'MED_VENT_CNT',
#        'MED_HOSP_CNT', 'SRC_OVERSEAS_CNT', 'SRC_INTERSTATE_CNT',
#        'SRC_CONTACT_CNT', 'SRC_UNKNOWN_CNT', 'SRC_INVES_CNT', 'PREV_CASE_CNT',
#        'PREV_TEST_CNT', 'PREV_DEATH_CNT', 'PREV_RECOV_CNT', 'PREV_MED_ICU_CNT',
#        'PREV_MED_VENT_CNT', 'PREV_MED_HOSP_CNT', 'PREV_SRC_OVERSEAS_CNT',
#        'PREV_SRC_INTERSTATE_CNT', 'PREV_SRC_CONTACT_CNT',
#        'PREV_SRC_UNKNOWN_CNT', 'PREV_SRC_INVES_CNT', 'PROB_CASE_CNT',
#        'PREV_PROB_CASE_CNT', 'ACTIVE_CNT', 'PREV_ACTIVE_CNT', 'NEW_CASE_CNT',
#        'PREV_NEW_CASE_CNT', 'VACC_DIST_CNT', 'PREV_VACC_DIST_CNT',
#        'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT', 'VACC_PEOPLE_CNT',
#        'PREV_VACC_PEOPLE_CNT', 'VACC_AGED_CARE_CNT', 'PREV_VACC_AGED_CARE_CNT',
#        'VACC_GP_CNT', 'PREV_VACC_GP_CNT'

df = df.loc[df['NAME'] == "NSW"]

df = df.loc[df['REPORT_DATE'] >= "2021-08-01"].copy()

#%%
df = df[['REPORT_DATE','MED_ICU_CNT']]

df.columns = ['Date', 'ICU number']
# print(df)

import datetime
today = datetime.datetime.today()
today = datetime.datetime.strftime(today, "%Y-%m-%d")
startDate = '2021-08-01'

# subtract the baseline ICU assumption from the thresholds

# other = pd.date_range(start='2021-08-01', end=today, freq='D')
# other = other.to_frame(index=False, name='Date')
# other['Level 0'] = 579
# other['Level 1'] = 790
# other['Level 2'] = 926
# other['Surge capacity'] = 1550 

# other['Date'] = pd.to_datetime(other['Date'])
# other['Date'] = other['Date'].dt.strftime("%Y-%m-%d")

thresholds = [
	{"y1":579 - 387,"y2":579 - 387,"x1":startDate, "x2":today, "text":"Moderate"},
	{"y1":790 - 387,"y2":790 - 387,"x1":startDate, "x2":today, "text":"Severe"},
	{"y1":926 - 387,"y2":926 - 387,"x1":startDate, "x2":today, "text":"Overwhelming"},
	]

# %%


df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(by='Date', ascending=True)

updated_date = df['Date'].max()
df['Date'] = df['Date'].dt.strftime("%Y-%m-%d")
# print(df)
updated_date = datetime.datetime.strftime(updated_date, "%-d %B %Y")

# combo = pd.merge(df, other, left_on='Date', right_on='Date', how="left")

# print(combo)

def makeLineChart(df):

	template = [
			{
				"title": "Covid ICU numbers in NSW v ICU impact thresholds",
				"subtitle": f"Showing the number people in ICU over time, along with the NSW government's ICU capacity thresholds that indicate likely minimal, moderate, severe and overwhelming impact on ICU operation. Last updated {updated_date}.",
				"footnote": "",
				"source": "CovidLive.com.au, <a href='https://www.nsw.gov.au/sites/default/files/2021-09/Intensive_Care_Capacity.pdf'>ICU capacity thresholds</a>, Guardian analysis",
				"dateFormat": "%Y-%m-%d",
				"yScaleType":"",
				"xAxisLabel": "Date",
				"yAxisLabel": "",
				"minY": "",
				"maxY": "600",
				# "periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "15",
				"margin-bottom": "20",
				"margin-right": "20",
				"breaks":"no"
			}
		]
	key = []
	periods = []
	labels = []
	lines = thresholds
	chartId = [{"type":"linechart"}]
	df.fillna('', inplace=True)
	# df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], options=[{"colorScheme":"guardian", "lineLabelling":"FALSE"}], chartName=f"{chart_key}", lines=lines)

makeLineChart(df)