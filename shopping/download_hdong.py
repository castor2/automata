#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import requests
import codecs
import urllib
import wget
import re    #regular expression 
import yaml

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import parse_qs

import pandas as pd
import numpy  as np
import zipfile
from tabulate import tabulate

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


conf = yaml.load(open('download_config.yaml'), Loader=yaml.FullLoader)

url_in  = conf['site_info']['url_hdong']
url_dns = urlparse(url_in).scheme + "://" + urlparse(url_in).netloc
path_data_hdong = conf['site_info']['path_data_hdong']

SLACK_TOKEN = conf['slack_info']['token']
V2N_MONITORING_CHANNEL = conf['slack_info']['channel']
client = WebClient(token=SLACK_TOKEN)


# In[ ]:


def send_slack_msg(slack_msg):
    try:
        response = client.chat_postMessage(
            channel=V2N_MONITORING_CHANNEL,
            text=slack_msg
        )
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["error"]    # str like 'invalid_auth', 'channel_not_found'


#https://stackoverflow.com/questions/40145631/precisely-catch-dns-error-with-python-requests
def sitecheck(url):
    status = None
    message = ''
    try:
        resp = requests.head('http://' + url)
        status = str(resp.status_code)
    except requests.ConnectionError as exc:
        print(exc)

        if ("[Errno 11001] getaddrinfo failed" in str(exc) or     # Windows
            "[Errno -2] Name or service not known" in str(exc) or # Linux
            "[Errno 8] nodename nor servname " in str(exc)):      # OS X
            message = 'DNSLookupError'
        else:
            raise

    return url, status, message

# ref https://stackoverflow.com/questions/70753206/download-and-extract-only-news-from-bbc
def get_links(url):
    LINKS = []

    response = requests.get(url)
    soup = BeautifulSoup(response.text, features='lxml')
    #print(soup)
    #soup = codecs.open("test.html", "r", "utf-8")
    #contents = soup.read()

    # get table of links
    #for html in soup.find_all('li', class_name='wrap'):
    for html in soup.find_all('div', 'wrap'):
        link = html.find('a').get('href')
        if "https://" in link:
            LINKS.append(link)
        else:
            # link = url+link
            link = url_dns + link
            LINKS.append(link)
        print("adding ", link)
    
    #NEW_LINKS = []
    #for link in LINKS:
    #    # print(link) # https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardList.do?bbsId=BBSMSTR_000000000052/frt/bbs/type001/commonSelectBoardArticle.do;jsessionid=5C2MFy-f8LqD8CjwDP939Fal.node10?bbsId=BBSMSTR_000000000052&nttId=101209
    #    parsed_url = urlparse(link)
    #    # print(parsed_url.query) # bbsId=BBSMSTR_000000000052/frt/bbs/type001/commonSelectBoardArticle.do;jsessionid=5C2MFy-f8LqD8CjwDP939Fal.node10?bbsId=BBSMSTR_000000000052&nttId=106692
    #    bbsId_org = parse_qs(parsed_url.query)['bbsId'] # BBSMSTR_000000000052/frt/bbs/type001/commonSelectBoardArticle.do;jsessionid=EdoTpHz-2hU-SBFcvLXcOZUK.node50?bbsId=BBSMSTR_000000000052
    #    bbsId = bbsId_org[0].split('/')[0] # BBSMSTR_000000000052
    #    nttId = parse_qs(parsed_url.query)['nttId'][0] # 106692
    #    # add links https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000052&nttId=106692
    #    NEW_LINKS.append('https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?'+'bbsId='+bbsId+'&nttId='+nttId)

    return LINKS

def get_html(url):
    LINKS = []

    response = requests.get(url)
    soup = BeautifulSoup(response.text, features='lxml')
    #print(soup)
    #soup = codecs.open("test.html", "r", "utf-8")
    #contents = soup.read()
    
    return soup

def get_donwload_links(url): 
    FILES = []

    response = requests.get(url)
    soup = BeautifulSoup(response.text, features='lxml')

    # fileList
    # [0] jscode20240201.zip
    # [1] jscode20240201(말소코드포함).zip
    # [2] 240201 행정기관(행정동) 및 관할구역(법정동) 변경내역(예천군 호명읍).hwpx
    # [3] 행정기관(행정동) 및 관할구역(법정동) 코드 Layout.hwpx
    for html in soup.find_all('div', 'fileList'):
        link = html.find('a').get('href') # /cmm/fms/FileDown.do?atchFileId=FILE_00124537hf7rFYg&fileSn=0
        if "https://" in link:
            FILES.append(link)
        else:
            # link = url+link
            link = url_dns + link
            FILES.append(link)
        print("adding download link:", link)

    # print(FILES) # 'https://www.mois.go.kr/cmm/fms/FileDown.do?atchFileId=FILE_00124537hf7rFYg&fileSn=0']

    return FILES
#
# download the first attached file from article link
#
def download_files(article_link):
    FILE_LINKS = get_donwload_links(article_link)
    FILE_NAMES = []
    FILE_DATES = []
    STATUS = 'READY'

    # sample https://www.mois.go.kr/cmm/fms/FileDown.do?atchFileId=FILE_00124537hf7rFYg&fileSn=0
    for link in FILE_LINKS:
        #final_url = requests.head(link, allow_redirects=True).url
        #print('final_url:', final_url)

        result = wget.download(link)
        print('file download: ', result)
    
        # ref https://stackoverflow.com/questions/12595051/check-if-string-matches-pattern
        if re.match(r"jscode[0-9]{8}.zip", result):
            version_date = re.findall(r'\d+',result)[0]  # first digit string like 20240201
            print('effective date:', version_date)
            FILE_NAMES.append(result)
            FILE_DATES.append(version_date)
            STATUS = 'OK'
        elif re.match(r"jscode[0-9]{8}[0-9() ]{3,10}.zip", result):
            print('delete duplicated file:', result, ', use existing one')
            os.remove(result)
            version_date = re.findall(r'\d+',result)[0]
            print('effective date:', version_date)
            FILE_NAMES.append(result)
            FILE_DATES.append(version_date)
            STATUS = 'DUPLICATED'
        else:
            print('not a jscode file. delete:',result)
            os.remove(result)
            STATUS = 'NOT JSCODE FILE'

    return FILE_DATES, FILE_NAMES, STATUS
    


# ## unzipped files 
# 6190366 Jan 22 18:02 KIKcd_B.20240201\
#  762910 Jan 22 18:06 KIKcd_B.20240201.xlsx\
# 1178415 Jan 22 18:02 KIKcd_H.20240201\
#  147134 Jan 22 18:10 KIKcd_H.20240201.xlsx\
# 3598320 Jan 22 18:02 KIKmix.20240201\
#  875062 Jan 22 18:13 KIKmix.20240201.xlsx
# 
# # csv files
# KIKcd_B.20240201\
# KIKcd_H.20240201\
# KIKmix.20240201
# 
# # xls files 
# KIKcd_B.20240201.xlsx\
# KIKcd_H.20240201.xlsx\
# KIKmix.20240201.xlsx

# In[ ]:


def unzip_csv(date, filename):
    unzip_path = path_data_hdong+'/'+date
    
    if( os.path.exists(path_data_hdong)!=True ): 
        # make directory data_hdong/20240206 
        #os.mkdir(path_data_hdong, mode = 0o755, *, dir_fd = None)
        os.mkdir(path_data_hdong)
        os.mkdir(unzip_path)
    elif( os.path.exists(unzip_path)!=True ): 
        os.mkdir(unzip_path)
    else:
        # do nothing
        print('directory already exist:', unzip_path)
        

    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(unzip_path)

    #df_hdong = pd.read_csv('data_hdong/KIKcd_H.20240201', encoding='CP949')
    #df_bdong = pd.read_csv('data_hdong/KIKcd_B.20240201', encoding='CP949')
    #df_mix   = pd.read_csv('data_hdong/KIKmix.20240201', encoding='CP949')
    df_hdong = pd.read_excel(unzip_path+'/KIKcd_H.'+ date +'.xlsx')
    df_bdong = pd.read_excel(unzip_path+'/KIKcd_B.'+ date +'.xlsx')
    df_mix   = pd.read_excel(unzip_path+'/KIKmix.' + date +'.xlsx')
    
    print('hdong:', df_hdong.shape)
    print('bdong:', df_bdong.shape)
    print('mix:  ', df_mix.shape)
    df_mix.rename(columns={'행정동코드': 'adong_cd', '시도명': 'region', '시군구명': 'sgg', '읍면동명':'emd', '법정동코드':'ldong_cd', '동리명':'emd_l', '생성일자':'createdAt', '말소일자':'deletedAt'},  inplace = True, errors="raise")
    df_mix['vaildFrom']=date

    csv_filename = unzip_path+'/KIKmix.'+date+'.csv' 
    df_mix.to_csv(csv_filename, sep=',', na_rep='', index=False)
    #check
    # df_mix = pd.read_csv('data_hdong/KIKmix.20240201.csv', encoding='utf-8')
    # df_mix.head(20)

    return csv_filename


# In[ ]:


# test shell

article_links = get_links(url_in)

# get latest article [0]
dates, names, status = download_files(article_links[0])
print(dates, names, status)
if (status == 'OK' ): 
    slack_msg = 'incoming file: ' + names[0] + '\nvalid from ' + dates[0]
    send_slack_msg(slack_msg)
    print('save jscode file to csv')
    filename = unzip_csv(dates[0], names[0])
    send_slack_msg('saved to ' + filename)

elif (status == 'DUPLICATED' ): 
    print('already exists. skip')
else: 
    print('not a jscode file')

