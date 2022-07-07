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
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.common.keys import Keys

# 셀레니움 OPTION 설정
# WEBDRIVER_PATH = f"{os.getcwd()}/chromedriver"
WEBDRIVER_PATH = f"D:\Python\WorkSpace\dmcProject\chromedriver.exe"
WEBDRIVER_OPTIONS = webdriver.ChromeOptions()
# WEBDRIVER_OPTIONS.add_argument('headless')
WEBDRIVER_OPTIONS.add_argument('--disable-dev-shm-usage')
WEBDRIVER_OPTIONS.add_argument('--no-sandbox')
WEBDRIVER_OPTIONS.add_argument('--ignore-certificate-errors')

IndexName = "source_data"
DataType = "naver_news"
SearchDate = str(datetime.datetime.now()).replace("T", "")
SearchID = "autoSystem"

# 실행 시 process(...) 또는 naver_news(...) 호출

# [(사번, 회사 이름)] 입력 필요
def process(bsn_lst:list, is_test=False, print_failed=False, file_path=None):
    bsn_set = set()
    if not file_path is None:
        # tmp = funcs.load_bsn_list(file_path)
        tmp = get_bizNo()
        bsn_set =  set(tmp)
    try:
        for bsn_info in tqdm(bsn_lst):
            if len(bsn_info)!=2:
                continue
            biz_no, company_name = bsn_info
            if company_name is None:
                continue
            # 작업 기록 존재시 통과
            if str(biz_no) in bsn_set:
                continue
            bsn_set.add(str(biz_no))
            
            results = crawler_naver_news(biz_no, company_name, None, None)
            results = sorted(results, key=lambda o: o[1]['Data']['PostDate'])
            results = results[:4000]
            for res in results:
                #funcs.save_data_to_es(index=IndexName, data=res[1], id=res[0])
                pass
            if not is_test:
                #funcs.update_searchDate_mysql(DataType, [biz_no])
                pass
    finally:
        if not file_path is None:
            #불러온 list 저장부
            #funcs.save_bsn_list(list(bsn_set), file_path)
            pass

def load_company_data():
    company_df = pd.read_csv('./Data/company_all_data.csv',encoding = 'ANSI')
    return company_df

def get_bizNo():
     company_df = load_company_data()
     result = company_df['사업자등록번호'].to_numpy()
     return result


# MySQL에서 (사번, 회사 이름) 로드
def naver_news(is_test=False, print_failed=False, file_path=None):
    # result = funcs.get_bizNo_mysql(DataType=DataType)
    result = load_company_data()
    biz_no_lst = []
    bsn_set = set()
    if not file_path is None:
        # tmp = funcs.load_bsn_list(file_path)
        tmp = get_bizNo()
        bsn_set =  set(tmp)
    try:
        for biz_no, company_name, ceo_name, biz_code, biz_type in tqdm(result):
            print(f'번호 {biz_no} 회사명 {company_name} 대표자명{ceo_name} 업종코드{biz_code} 업종{biz_type}')
         
        #for biz_no, company_name, ceo_name, date_date in tqdm(result):
            
            # 작업 기록 존재시 통과
            if str(biz_no) in bsn_set:
                continue
            bsn_set.add(str(biz_no))

            biz_no_lst.append(biz_no)
            if company_name is None:
                continue
            # results = crawler_naver_blog(biz_no, company_name, ceo_name, date_date)
            results = crawler_naver_news(biz_no, company_name, ceo_name)
            results = list(filter(lambda o: len(o)>=2, results))
            results = sorted(results, key=lambda o: o[1]['Data']['PostDate']) # PostDate 기준 정렬
            results = results[:4000] # 결과 중 4000개 까지 저장
            for res in results:
                pass
                # funcs.save_data_to_es(index=IndexName, data=res[1], id=res[0])

    finally:
        if not is_test:
            # funcs.update_searchDate_mysql(DataType, biz_no_lst)
            pass
        if not file_path is None:
            # 파일저장부
            # funcs.save_bsn_list(list(bsn_set), file_path)
            pass


def crawler_naver_news(biz_no, company_name, ceo_name, date_date):
    """
    # date_date가 없으면 초기 적재 → 날짜 기간 조건 없이 검색
    # date_date가 있으면 업데이트 적재 → 특정 기간 조건 검색
    """
    results = []
    news_urls = []
    news_titles = []
    news_dates = []
    news_contents = []

    keyword = company_name
    # 셀레니움 크롬 웹드라이버 생성
    webDriver = webdriver.Chrome(options=WEBDRIVER_OPTIONS, executable_path=WEBDRIVER_PATH)
    try: # 셀레니움 비정상 종료 대비
        SrchKeyword = f'"{keyword}"'

        # 데이터가 없는 경우
        if False : #tot_num_news < 1:
            return
        else:
            pageNo = 0
            finger_print = set() # Hash Set 을 사용하여 직전 루프에서 반복 수집되는 블로그 방지
            while True:
                if pageNo > 300:
                    break
                url = naverNewsUrl(keyword=SrchKeyword) if date_date is None else naverNewsUrl(keyword=SrchKeyword, date_date=date_date)
                webDriver.get(url)
                time.sleep(1)

                css_selector = 'div.news_wrap.api_ani_send > div > div.news_info > div.info_group > a.info'
                ems = webDriver.find_elements_by_css_selector(css_selector)
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
                            css_selector = '#content > div.end_ct > div > div.article_info > span > em'
                            #sp_nws4 > div > div > div.news_info > div.info_group > span.info 
                            news_dates.append(webDriver.find_element_by_css_selector(css_selector).text) # 본문 기사 게시 일자 및 시간 수집
                            
                            css_selector = '#content > div.end_ct > div > div.end_body_wrp'
                            news_contents.append(webDriver.find_element_by_css_selector(css_selector).text) # 본문 기사 본문 내용 수집

                        elif news_type == 'sports':
                            css_selector = '#content > div > div.content > div > div.news_headline > div > span:nth-child(1)'
                            date = webDriver.find_element_by_css_selector(css_selector).text
                            date = date.split(' ')
                            date = date[1] + ' ' + date[2] + ' ' + date[3]
                            news_dates.append(date) # 본문 기사 게시 일자 및 시간 수집
                            
                            css_selector = '#newsEndContents'
                            news_contents.append(webDriver.find_element_by_css_selector(css_selector).text) # 본문 기사 본문 내용 수집

                        # 현재 탭 닫기
                        webDriver.close()
                        # 다시처음 탭으로 돌아가기
                        webDriver.switch_to.window(webDriver.window_handles[0])
                
        return zip(news_dates, news_titles, news_contents, news_urls) , ['Date', 'Title', 'Content', 'URL']
    except Exception as e:
        print('naver_news_data Error: {}'.format(e))
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
            quote_plus('ds'): unquote(date_date),
            quote_plus('de'): unquote(SearchDate[:10]),
        
        }, encoding='utf-8')
      
    url = base_url + queryParams
    return url




# 페이지에 기록된 시간 표시를 표준시간 (연,월,일) 표시로 변경
# 예) "1시간전" → [현재시간] - 1시간 → 2022-07-05
def calc_date(date_str:str):
    # 정규표현식으로 문장 내 숫자 존재 확인
    matched_lst = re.findall("\d+", date_str)
    if len(matched_lst)==3:
        return f"{matched_lst[0]}-{matched_lst[1].zfill(2)}-{matched_lst[2].zfill(2)}"
    
    delta = None
    delta_int = int(re.findall("\d+", date_str)[0])
    if "시간" in date_str:
        delta = datetime.timedelta(hours=delta_int)
    elif "분" in date_str:
        delta = datetime.timedelta(minutes=delta_int)
    elif "초" in date_str:
        delta = datetime.timedelta(seconds=delta_int)
    
    result = datetime.datetime.strptime(SearchDate, '%Y-%m-%d %H:%M:%S.%f') - delta

    return result.strftime("%Y-%m-%d")



news_data = crawler_naver_news('1010291472', '글로벌에이스', '김선남', None)