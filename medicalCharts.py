#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import simplejson as json
import requests

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

with open('covid-live.json', 'w') as outfile:
	json.dump(r.json(), outfile)
	
import hospitalDeaths
import hospitalPercent
import icuCapacity
	