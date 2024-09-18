
import datetime
import json
import pprint
from influxdb import InfluxDBClient

influx_client = InfluxDBClient('localhost', 8086, 'influx_usename', 'influx_password', 'coin')
#influx_client.create_database('macro')

def writeInflux_m2(yearmonth, m2_amount):
  print('year=',yearmonth[0:4], 'month=',  yearmonth[4:], 'm2_amount=', m2_amount)
  time_str = yearmonth[0:4] + '-' + yearmonth[4:] + "-28T00:00:00Z"
  json_body = [
    {
      "measurement": "macro",
      "tags": {
        "host": "server01",
      },
      "time": time_str,
      "fields": {
        "m2":  float(m2_amount)
      }
    }
  ]
  influx_client.write_points(json_body)


import configparser
config = configparser.ConfigParser()
read_ok = config.read(r'config.txt')
if read_ok:
    ecos_key = config.get('macro', 'ecos_key')
    print(ecos_key)
else:
    print(f'Could not read config file')
    exit()

# API sample 
#from urllib.request import urlopen
#import json
#url="http://ecos.bok.or.kr/api/StatisticSearch/"+ecos_key+"/json/kr/1/24/101Y001/M/200001/202412/BBGS00"
#result = urlopen(url)
#html = result.read()
#data = json.loads(html)
#print(data)
#for x in data.get('StatisticSearch').get('row'):
  #print(x.get('TIME'), x.get('DATA_VALUE'))
  #writeInflux_m2(x.get('TIME'), x.get('DATA_VALUE'))



# from https://github.com/WooilJeong/PublicDataReader/blob/main/test/develop.ipynb
import os
import sys
from pathlib import Path
sys.path.append(str(Path(os.getcwd()).parent))

#from config import API_KEY_INFO
#service_key = API_KEY_INFO.get("ecos")
from PublicDataReader import Ecos
api = Ecos(ecos_key)
# samples
#df = api.get_statistic_table_list()
#df = api.get_key_statistic_list()
#df = api.get_statistic_word(용어="소비자동향지수")
#df = api.get_statistic_search(통계표코드="200Y001", 주기="A", 검색시작일자="2015", 검색종료일자="2021")

# refer https://yenpa.tistory.com/85
# url = 'https://ecos.bok.or.kr/api/StatisticSearch/' + apikey + '/json/kr/' + start + '/' + end + '/101Y001/M/200001/202212/BBGS00'
# m2 
df = api.get_statistic_search(통계표코드="101Y001", 통계항목코드1="BBGS00", 주기="M", 검색시작일자="200501", 검색종료일자="202412")
print(df.size)
#print(df.head(100))

for i, row in df.iterrows():
  # print(row['시점'], row['값'])
  writeInflux_m2(row['시점'], row['값'])


