# 3. 뉴스
# 유형: WEB CRAWLING
# 데이터타입 칼럼명: naver_news

# 공통 함수
from lib2to3.pgen2 import driver
import os
#from typing import final
#from Funcs import funcs
from tqdm import tqdm

import pandas as pd
import numpy as np

# ETC
import json, datetime, math, time, pandas as pd
import random, string, re
from dateutil.relativedelta import relativedelta

import logging
import traceback

# OPEN API
import urllib.request
from urllib.request import Request, urlopen
import urllib.parse
from urllib.parse import urlencode, quote_plus, unquote
import xml.etree.ElementTree as ET

# WEB CRAWLING
# from fake_useragent import UserAgent    #pip install fake-useragent
# from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.common.keys import Keys

# 셀레니움 OPTION 설정
# WEBDRIVER_PATH = f"{os.getcwd()}/chromedriver"
WEBDRIVER_PATH = f"C:\chromedriver.exe"
WEBDRIVER_OPTIONS = webdriver.ChromeOptions()
# WEBDRIVER_OPTIONS.add_argument('headless')
WEBDRIVER_OPTIONS.add_argument('--disable-dev-shm-usage')
WEBDRIVER_OPTIONS.add_argument('--no-sandbox')
WEBDRIVER_OPTIONS.add_argument('--ignore-certificate-errors')

IndexName = "source_data"
DataType = "naver_news"
SearchDate = str(datetime.datetime.now()).replace("T", "")
SearchID = "autoSystem"



def load_company_data():
    company_df = pd.read_csv('./Data/company_data.csv')
    
    return company_df

def get_bizNo():
     company_df = load_company_data()
     result = company_df['사업자등록번호'].to_numpy()
     return result


def crawler_naver_news(company_index, biz_no, company_name, ceo_name, date_date):
    """
    # date_date가 없으면 초기 적재 → 날짜 기간 조건 없이 검색
    # date_date가 있으면 업데이트 적재 → 특정 기간 조건 검색
    """
    
    logging.basicConfig(filename='./Logs/crawler_naver_news.log', level=logging.ERROR)
    
    news_urls = []
    news_titles = []
    news_dates = []
    news_contents = []

    keyword = company_name
    # 셀레니움 크롬 웹드라이버 생성
    webDriver = webdriver.Chrome(options=WEBDRIVER_OPTIONS, executable_path="C:\chromedriver.exe")
    try: # 셀레니움 비정상 종료 대비
        SrchKeyword = f'"{keyword}"'

        # 데이터가 없는 경우
        if False : #tot_num_news < 1:
            return
        else:
            pageNo = 0
            finger_print = set() # Hash Set 을 사용하여 직전 루프에서 반복 수집되는 블로그 방지
            
            url = naverNewsUrl(keyword=SrchKeyword) if date_date is None else naverNewsUrl(keyword=SrchKeyword, date_date=date_date)
            webDriver.get(url)
            time.sleep(1)
            while pageNo < 300:

                # css_selector = 'div.news_wrap.api_ani_send > div > div.news_info > div.info_group > a.info'
                # ems = webDriver.find_elements_by_css_selector(css_selector)
                ems = webDriver.find_elements(By.CSS_SELECTOR,'a.info') 
                
                if len(ems) == 0 : break
                for em in ems:
                    if em.text == '네이버뉴스': # 언론사 홈페이지 말고 네이버 뉴스만 가져오기
                        em.click()                        
                        #새창으로 드라이버 전환
                        webDriver.switch_to.window(webDriver.window_handles[1])

                        current_url = webDriver.current_url
                        news_urls.append(current_url) # 본문 링크 수집    

                        # 뉴스 타입 분류
                        news_type = current_url.split('.')[0].split('//')[1]       
                        news_titles.append(webDriver.title.split('::')[0])# 본문 기사 제목 수집

                        if news_type == 'entertain':
                            #sp_nws4 > div > div > div.news_info > div.info_group > span.info 
                            
                            # news_contents.append(webDriver.find_element_by_css_selector(css_selector).text) 

                            css_selector = '#content > div.end_ct > div > div.article_info > span > em'
                            news_dates.append(webDriver.find_element(By.CSS_SELECTOR,css_selector).text) # 본문 기사 게시 일자 및 시간 수집

                            css_selector = '#content > div.end_ct > div > div.end_body_wrp'
                            news_contents.append(webDriver.find_element(By.CSS_SELECTOR,css_selector).text) # 본문 기사 본문 내용 수집
                            

                        elif news_type == 'sports':
                            # date = webDriver.find_element_by_css_selector(css_selector).text
                            # date = date.split(' ')
                            # date = date[1] + ' ' + date[2] + ' ' + date[3]
                            # news_dates.append(date) # 본문 기사 게시 일자 및 시간 수집
                            
                            # news_contents.append(webDriver.find_element_by_css_selector(css_selector).text) # 본문 기사 본문 내용 수집

                            css_selector = '#content > div > div.content > div > div.news_headline > div > span:nth-child(1)'
                            date =webDriver.find_element(By.CSS_SELECTOR,css_selector).text
                            date = date.split(' ')
                            date = date[1] + ' ' + date[2] + ' ' + date[3]
                            news_dates.append(date) # 본문 기사 게시 일자 및 시간 수집

                            css_selector = '#newsEndContents'
                            news_contents.append(webDriver.find_element(By.CSS_SELECTOR, css_selector).text) # 본문 기사 본문 내용 수집
                        
                        else : 
                            # news_dates.append(webDriver.find_element_by_css_selector(css_selector).text) 

                            css_selector = '#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span'
                            news_dates.append(webDriver.find_element(By.CSS_SELECTOR,css_selector).text) # 본문 기사 게시 일자 및 시간 수집
                            
                            css_selector = '#contents'
                            news_contents.append(webDriver.find_element(By.CSS_SELECTOR,css_selector).text) # 본문 내용 수집
                            
                        # 현재 탭 닫기
                        webDriver.close()
                        # 다시처음 탭으로 돌아가기
                        webDriver.switch_to.window(webDriver.window_handles[0])

                #main_pack > div.api_sc_page_wrap > div > a.btn_next
                css_selector = '#main_pack > div.api_sc_page_wrap > div > a.btn_next'
                btn_next = webDriver.find_element(By.CSS_SELECTOR,css_selector)
                btn_next.click()
                pageNo += 1

        #크롤링 데이터 저장  
        news_data = []
        news_cloumns = []
        if len(news_dates) != 0:
            news_data = zip(news_dates, news_titles, news_contents, news_urls)
            news_cloumns = ['Date', 'Title', 'Content', 'URL']
            append_csv(company_index, company_name, news_data, news_cloumns)
                    
        return news_data , news_cloumns
    except Exception as e:
        print('naver_news_data Error: {}'.format(e))
        logging.error(traceback.format_exc())
        return "error"
    finally:
        webDriver.close()


# URL Query 생성
def naverNewsUrl(keyword, date_date=None):
    base_url = f"https://search.naver.com/search.naver?where=news&sm=tab_pge&"
    
    if date_date is None:
        queryParams = urlencode({
            quote_plus('query'): keyword,
        }, encoding='utf-8')           
    else:
        queryParams = urlencode({
            quote_plus('query'): keyword,
            quote_plus('ds'): unquote(date_date[:8]),
            quote_plus('de'): unquote(date_date[8:]),
        
        }, encoding='utf-8')
      
    url = base_url + queryParams
    return url




def append_csv(company_index, company_name, news_data, news_cloumns):
    
    logging.basicConfig(filename='./Logs/append_csv_log.log', level=logging.ERROR)
    
    try:
        df = pd.DataFrame(news_data)
        df.columns = news_cloumns
        df.to_csv(f'.\\company_news_data\\{company_name}_news_list_{company_index}.csv',encoding='utf-8-sig',index=False)
        
        '''
        with open(f'{company_name}_news_list.csv', 'a') as f :
            data = news_cloumns
            f.write(data)
            data = news_data
            f.write(data)
        '''

    except Exception as e:
        print('append csv Error: {}'.format(e))
        logging.error(traceback.format_exc())
        return "error"

        
