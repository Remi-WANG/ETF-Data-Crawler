## 0. Import the packages needed

import tushare as ts
import json
import requests
import matplotlib.pyplot as plt
import pandas as pd
import time
import re
import numpy as np

## 1. Get trading calendar using Tushare

token = 'your own tushare token'
pro = ts.pro_api(token)

cal = pro.trade_cal(exchange='', start_date='20190701', end_date='20220211', fields='cal_date', is_open='1')
cal = pd.to_datetime(cal.cal_date)

## 2. Get ETF volume data

# I know two ways to construct a request; I deploy the first for getting volume data and the second for value 
def get_etf_vol(date,code):
	"""
	get the volume of a etf at a given trading day

	"""
    params = {
        'jsonCallBack': 'jsonpCallback39629019',
        'sqlId': 'COMMON_SSE_ZQPZ_ETFZL_XXPL_ETFGM_SEARCH_L',
        'STAT_DATE': date,
        }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Referer': 'http://www.sse.com.cn/'
        }

    root_url = 'http://query.sse.com.cn/commonQuery.do'
    
    r = requests.get(url=root_url, headers=headers, params=params)
    r = r.content.decode()
    r = json.loads(re.findall('\(.*?)\)', r)[0])
    try:
        etf_vol = [info for info in r['result'] if info['SEC_CODE'] == code][0]['TOT_VOL']
    except:
        etf_vol = None
        
    vol_dict = {'date':date, 'vol':etf_vol}
    return vol_dict

def etf_vol_crawler(calendar,code):
    '''
    calendar: an iterable datetime sequence
    code: fund code in string format
    
    '''
    etf_vol_ls = list()
    for date in calendar:
        date = str.split(str(date))[0]
        etf_vol_ls.append(get_etf_vol(date,code))
        
    vol_final = pd.DataFrame(etf_vol_ls)
        
    return vol_final

## 3. Get ETF value data

def get_etf_value(code,page,start,end):
	"""
	get the etf value within a given time interval with a specified page 

	"""
        
    value_url = 'http://api.fund.eastmoney.com/f10/lsjz?\
callback=jQuery183023176955335716132_1644507388843\
&fundCode={}\
&pageIndex={}\
&pageSize=20\
&startDate={}\
&endDate={}'.format(code,page,start,end)
    
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Host': 'api.fund.eastmoney.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Referer': 'http://fundf10.eastmoney.com/jjjz_320007.html'
        }

    r = requests.get(value_url, headers=headers)
    r = r.content.decode()
    r = pd.DataFrame(json.loads(re.findall('\((.*?)\)', r)[0])['Data']['LSJZList'])
    
    value_dict = {'date':r['FSRQ'], 'value':r['LJJZ']}
    
    return pd.DataFrame(value_dict)

# take 512170 as an example 

etf_value_ls = list()
for page in range(1,100):
    try:
        etf_value_ls.append(get_etf_value(512170,page,'2019-07-01','2022-02-11'))
    except:
        break
        
value_final = pd.concat(etf_value_ls)

## 4. Put them together
final = pd.merge(vol_final,value_final)
final.set_index('date', inplace=True)


