# This file updates NASDAQ, S&P 500, and DJIA close data
import csv
from datetime import datetime
import json
import requests

# set path to data folder
path='/var/www/html/austinclemens/stock_market/DATA/'

#### get data from FRED ####
# load FRED API key
with open(path+'FRED_API.txt', 'r') as file:
	FRED_api=file.read()

# function to get data from the FRED API
def data_scrape(series, FRED_api, frequency):
	# get all series data in one go
	p = requests.get('https://api.stlouisfed.org/fred/series/observations?series_id='+series+'&api_key='+FRED_api+'&file_type=json&frequency='+frequency+'&aggregation_method=avg')
	json_data = json.loads(p.text)
	return json_data

# retrieve the series from FRED
DJIA_fred=data_scrape('DJIA',FRED_api,'d')['observations']
SP500_fred=data_scrape('SP500',FRED_api,'d')['observations']
NASDAQCOM_fred=data_scrape('NASDAQCOM',FRED_api,'d')['observations']

# load existing dataset
with open(path+'stock_close.csv', 'r') as file:
	reader=csv.reader(file)
	stocks=[row for row in reader][1:]

# convert all dates in both datasets to datetimes
for item in DJIA_fred:
	item['date']=datetime.strptime(item['date'], "%Y-%m-%d")
for item in SP500_fred:
	item['date']=datetime.strptime(item['date'], "%Y-%m-%d")
for item in NASDAQCOM_fred:
	item['date']=datetime.strptime(item['date'], "%Y-%m-%d")
for item in stocks:
	item[0]=datetime.strptime(item[0], "%m/%d/%y")

# now do two loops, one through the existing data to find missings and replace them
for item in stocks:
	if item[1]=='':
		try:
			item[1]=[row for row in NASDAQCOM_fred if row['date']==item[0]][0]['value']
		except:
			print("Don't have data for NASDAQ on "+item[0].strftime("%m/%d/%y"))
	if item[2]=='':
		try:
			item[2]=[row for row in SP500_fred if row['date']==item[0]][0]['value']
		except:
			print("Don't have data for SP500 on "+item[0].strftime("%m/%d/%y"))
	if item[3]=='':
		try:
			item[3]=[row for row in DJIA_fred if row['date']==item[0]][0]['value']
		except:
			print("Don't have data for DJIA on "+item[0].strftime("%m/%d/%y"))

# and a second loop to add completely new dates
existing=[item[0] for item in stocks]
new=[]
for item in DJIA_fred:
	if item['date'] not in existing and item['value']!='.':
		try:
			SP500_value=[spitem for spitem in SP500_fred if spitem['date']==item['date']][0]['value']
		except:
			SP500_value=''
		try:
			NASDAQCOM_value=[nqitem for nqitem in NASDAQCOM_fred if nqitem['date']==item['date']][0]['value']
		except:
			NASDAQCOM_value=''
		try:
			DJIA_value=[nqitem for nqitem in DJIA_fred if nqitem['date']==item['date']][0]['value']
		except:
			DJIA_value=''
		new.append([item['date'].strftime("%m/%d/%y"),NASDAQCOM_value,SP500_value,DJIA_value])

for item in stocks:
	item[0]=item[0].strftime("%m/%d/%y")
for item in new:
	stocks.append(item)

# and write all rows to file
with open(path+'stock_close.csv', 'w') as file:
	writer=csv.writer(file)
	writer.writerow(['Date','NASDAQ','SP500','DOW'])
	for row in stocks:
		writer.writerow(row)