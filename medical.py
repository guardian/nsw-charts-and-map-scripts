#%%
import simplejson as json
import boto3
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from yachtCharter import yachtCharter
# from modules.syncData import syncData

here = os.path.dirname(__file__)
data_path = os.path.dirname(__file__) + "/data/"
output_path = os.path.dirname(__file__) + "/output/"

print("Checking covidlive")

#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

#%%

## Grab Covid Live Data

data = r.json()

df = pd.read_json(r.text)
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


nsw = df.loc[df['NAME'] == "NSW"]
cols = nsw.columns

#%%

# medical = ['REPORT_DATE','ACTIVE_CNT','MED_HOSP_CNT','MED_ICU_CNT','MED_VENT_CNT', 'DEATH_CNT']
medical = ['REPORT_DATE','MED_HOSP_CNT','MED_ICU_CNT','MED_VENT_CNT', 'DEATH_CNT']
nsw_med = nsw[medical]
nsw_med['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'], format="%Y-%m-%d")
# nsw_med = nsw_med.rename(columns={"REPORT_DATE": "Date",'ACTIVE_CNT':"Active cases","MED_ICU_CNT":"In ICU",  'MED_VENT_CNT':"On ventilators", 'MED_HOSP_CNT':"In hospital", "DEATH_CNT":"Deaths"})
nsw_med = nsw_med.rename(columns={"REPORT_DATE": "Date","MED_ICU_CNT":"In ICU",'MED_VENT_CNT':"On ventilators", 'MED_HOSP_CNT':"In hospital", "DEATH_CNT":"Deaths"})
nsw_med = nsw_med.sort_values(['Date'])
nsw_med = nsw_med.set_index('Date')

#%%

nsw_med.loc[:"2021-07-09", "Deaths"] = 0
nsw_med.loc["2021-07-09":, "Deaths"] = nsw_med.loc["2021-07-09":, "Deaths"].sub(nsw_med.loc["2021-07-09":, "Deaths"].shift())
nsw_med.loc["2021-07-09":"2021-07-10", "Deaths"] = 0
nsw_med['Deaths'] = nsw_med['Deaths'].cumsum()

#%%
lastUpdated = nsw_med.index[-1]
updatedText = lastUpdated.strftime('%-d %B, %Y')
sixty_days = lastUpdated - timedelta(days=60)
nsw_med_60 = nsw_med["2021-06-15":]
# nsw_med_60 = nsw_med
nsw_med_60.index = nsw_med_60.index.strftime('%Y-%m-%d')
nsw_med_60_stack = nsw_med_60.stack().reset_index().rename(columns={"level_1":"category", 0:"count"})
nsw_med_60_stack = nsw_med_60_stack.set_index('Date')

#%%

def makeNswMedicalChart(df):
	
	template = [
			{
				"title": "NSW hospitalisations and deaths",
				"subtitle": "Hospitalisation figures are totals at each point in time, number of deaths is the cumulative sum from 10 July onwards. Last updated {date}".format(date=updatedText),
				"footnote": "",
				"source": " | Source: <a href='https://covidlive.com.au/' target='_blank'>Covidlive.com.au</a>",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"timeInterval":"day",
				"tooltip":"<strong>Date: </strong>{{#nicedate}}Date{{/nicedate}}<br/><strong>Cases: </strong>{{Cases}}",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "5",
				"margin-bottom": "20",
				"margin-right": "25",
				"xAxisDateFormat": "%b %d"
			}
		]
	key = []
	periods = []
	labels = []
	options = [{"numCols":1, "chartType":"area", "height":70,"scaleBy":"group"}]
	chartId = [{"type":"smallmultiples"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template,options=options, data=chartData, chartId=chartId, chartName="nsw-cases-v-hospitalisation-2021")

makeNswMedicalChart(nsw_med_60_stack)
