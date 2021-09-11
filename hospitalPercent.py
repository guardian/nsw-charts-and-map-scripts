#%%

import os
import requests
import pandas as pd
from yachtCharter import yachtCharter
import datetime
pd.set_option("display.max_columns", 100)
chart_key = "oz-covid-hospitalisation-percent"

here = os.path.dirname(__file__)
data_path = os.path.dirname(__file__) + "/data/"
output_path = os.path.dirname(__file__) + "/output/"

pd.options.mode.chained_assignment = None
#%%

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

df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'],format="%Y-%m-%d")
df = df.sort_values(by='REPORT_DATE', ascending=True)

#%%

zdf = df.copy()

zdf['New_cases'] = zdf['CASE_CNT'].diff(1)
# zdf['New_over_cases'] = zdf['SRC_OVERSEAS_CNT'].diff(1)
# zdf['New_local_cases'] = zdf['New_cases'] - zdf['New_over_cases']




zdf['Local_last_14'] = zdf['New_cases'].rolling(window=14).sum()

zdf['Hospitalised_percent'] = (zdf['MED_HOSP_CNT'] / zdf['Local_last_14'])*100

zdf = zdf[['REPORT_DATE', 'Hospitalised_percent']]

zdf.columns = ['Date', 'Hospitalisation rate']

# zdf['Date'] = zdf['Date'].dt.strftime("%Y-%m-%d")





#%%
### THIS WAS THE PREVIOUS VERSION
# medical = ['REPORT_DATE','ACTIVE_CNT','MED_HOSP_CNT']
# df_med = df[medical]
# # df_med['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'], format="%Y-%m-%d")

# df_med = df_med.dropna(subset=['ACTIVE_CNT','MED_HOSP_CNT'])

# df_med = df_med.rename(columns={"REPORT_DATE": "Date", "ACTIVE_CNT":"Active cases",
#  'MED_HOSP_CNT':"In hospital"})
# # df_med = df_med.sort_values(['Date'])
# # df_med = df_med.set_index('Date')

# df_med['Percentage hospitalised'] = (df_med['In hospital'] / df_med['Active cases']) * 100

# df = df_med[['Date', 'Percentage hospitalised']]





# df['Date'] = pd.to_datetime(df['Date'])
# df = df.sort_values(by='Date', ascending=True)

updated_date = zdf['Date'].max()
zdf['Date'] = zdf['Date'].dt.strftime("%Y-%m-%d")

zdf = zdf.loc[zdf['Date'] > "2021-05-01"]
print(zdf.head(50))
# # print(df)
updated_date = datetime.datetime.strftime(updated_date, "%d %B %Y")

# print(df)

#%%


def makeLineChart(df):

    template = [
            {
                "title": "Covid hospitalisation rate in NSW",
                "subtitle": f"Showing the number of hospitalised Covid cases divided by the number of cases over the previous two weeks, including overseas acquired cases. Last updated {updated_date}.",
                "footnote": "",
                "source": "CovidLive.com.au, Guardian analysis",
                "dateFormat": "%Y-%m-%d",
                "yScaleType":"",
                "xAxisLabel": "Date",
                "yAxisLabel": "",
                "minY": "",
                "maxY": "",
                # "periodDateFormat":"",
                "margin-left": "30",
                "margin-top": "15",
                "margin-bottom": "20",
                "margin-right": "20",
                "breaks":"no"
            }
        ]
    key = []
    periods = []
    labels = []
    chartId = [{"type":"linechart"}]
    df.fillna('', inplace=True)
    # df = df.reset_index()
    chartData = df.to_dict('records')

    yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], options=[{"colorScheme":"guardian", "lineLabelling":"FALSE"}], chartName=f"{chart_key}")

makeLineChart(zdf)