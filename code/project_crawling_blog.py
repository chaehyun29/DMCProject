# 2. 네이버 블로그
# 유형: WEB CRAWLING
# 데이터타입 칼럼명: naver_blog

# 공통 함수
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
from fake_useragent import UserAgent    #pip install fake-useragent
# from bs4 import BeautifulSoup as bs
from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.common.keys import Keys

# 셀레니움 OPTION 설정
# WEBDRIVER_PATH = f"{os.getcwd()}/chromedriver"
WEBDRIVER_PATH = f"D:\lch\workspace\project\chromedriver.exe"
WEBDRIVER_OPTIONS = webdriver.ChromeOptions()
# WEBDRIVER_OPTIONS.add_argument('headless')
WEBDRIVER_OPTIONS.add_argument('--disable-dev-shm-usage')
WEBDRIVER_OPTIONS.add_argument('--no-sandbox')
WEBDRIVER_OPTIONS.add_argument('--ignore-certificate-errors')

IndexName = "source_data"
DataType = "naver_blog"
SearchDate = str(datetime.datetime.now()).replace("T", "")
SearchID = "autoSystem"

# 실행 시 process(...) 또는 naver_blog(...) 호출

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
            
            results = crawler_naver_blog(biz_no, company_name, None, None)
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
def naver_blog(is_test=False, print_failed=False, file_path=None):
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
            results = crawler_naver_blog(biz_no, company_name, ceo_name)
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


def crawler_naver_blog(biz_no, company_name, ceo_name, date_date):
    """
    # date_date가 없으면 초기 적재 → 날짜 기간 조건 없이 검색

    # date_date가 있으면 업데이트 적재 → 특정 기간 조건 검색
    """
    results = []

    keyword = company_name
    # 셀레니움 크롬 웹드라이버 생성
    webDriver = webdriver.Chrome(options=WEBDRIVER_OPTIONS, executable_path=WEBDRIVER_PATH)
    webDriver = webdriver.Chrome(options=WEBDRIVER_OPTIONS, executable_path='D:\lch\workspace\project\chromedriver.exe')
    try: # 셀레니움 비정상 종료 대비8
        SrchKeyword = f'"{keyword}"'

        # 포스팅 개수 계산
        url = naverBlogUrl(pageNo=1, keyword=SrchKeyword) if date_date is None else naverBlogUrl(pageNo=1, keyword=SrchKeyword, date_date=date_date)
        webDriver.get(url) # 셀레니움 HTTP/GET method 실행
        time.sleep(1) # 1초 대기

        # "css selector" 로 검색 결과 "건" 수 수집
        css_selector = '#content > section > div.category_search > div.search_information > span > span > em'
        tot_num_post = webDriver.find_element_by_css_selector(css_selector).text.replace("건", "")
        while True:
            if ',' not in tot_num_post:
                break
            tot_num_post = tot_num_post.replace(',', '')
        tot_num_post = int(tot_num_post)

        # 데이터가 없는 경우
        if tot_num_post < 1:
            return
        else:
            # 페이지 당 7개씩 존재 → "전체 건 수"/7 = 검색결과 페이지 수
            tot_num_page = math.ceil(tot_num_post / 7)
            finger_print = set() # Hash Set 을 사용하여 직전 루프에서 반복 수집되는 블로그 방지
            for pageNo in range(1, tot_num_page + 1):
                if pageNo > 300:
                    break
                url = naverBlogUrl(pageNo=pageNo, keyword=SrchKeyword) if date_date is None else naverBlogUrl(pageNo=pageNo, keyword=SrchKeyword, date_date=date_date)
                webDriver.get(url)
                time.sleep(1)

                css_selector = 'div.info_post > div.writer_info > span.name_blog'
                blog_name = [i.text for i in webDriver.find_elements_by_css_selector(css_selector)] # 블로그 이름 수집
                css_selector = 'div.info_post > div.writer_info > a > em.name_author'
                author_name = [i.text for i in webDriver.find_elements_by_css_selector(css_selector)] # 블로그 저자 이름 수집
                css_selector = 'div.info_post > div.writer_info > span.date'
                post_date = [i.text for i in webDriver.find_elements_by_css_selector(css_selector)] # 포스트 날짜 수집
                css_selector = 'div.desc > a.desc_inner > strong > span.title'
                post_title = [i.text for i in webDriver.find_elements_by_css_selector(css_selector)] # 포스트 이름 수집
                
                # 직전 페이지와 같은 타이틀의 게시글이 반복될 경우 루프 종료
                checker_lst = list(map(lambda o: o in finger_print, post_title))
                checker = True
                for x in checker_lst:
                    checker = checker and x
                if checker:
                    break
                finger_print = set(post_title)
                
                doc_id = [i.get_property('href').split('/')[-1] for i in webDriver.find_elements_by_xpath('//*[@id="content"]/section/div[2]/div/div/div[1]/div[1]/a[1]')] # 문서 ID 경로
                upload_id = [f'{i}/{j}' for i,j in zip(author_name, doc_id)]

                post_content = []
                for i in range(1, len(blog_name) + 1):
                    # 블로그 내용 수집
                    css_selector = '#content > section > div.area_list_search > div:nth-child(' + str(
                        i) + ') > div > div.info_post > div.desc > a.text'
                    try:
                        post = webDriver.find_element_by_css_selector(css_selector).text
                    except Exception as e:
                        post = ""
                    post_content.append(post)

                # JSON 형태로 저장
                for idx in range(len(blog_name)):
                    naver_blog_data = {
                        "BusinessNum": biz_no,
                        "DataType": DataType,
                        "SearchDate": str(datetime.datetime.now()).replace("T", ""),
                        "SearchID": SearchID,
                        "Data": {
                            'BlogName':blog_name[idx],
                            'AuthorName':author_name[idx],
                            'PostDate':calc_date(post_date[idx]),
                            'PostTitle':post_title[idx],
                            'PostContent':post_content[idx],
                        }
                    }
                    results.append((upload_id[idx], naver_blog_data))
        return results
    except Exception as e:
        print('naver_blog_data Error: {}'.format(e))
        return "error"
    finally:
        webDriver.close()

# URL Query 생성
def naverBlogUrl(pageNo, keyword, date_date=None):
    base_url = "https://section.blog.naver.com/Search/Post.nhn?"
    if date_date is None:
        queryParams = urlencode({
            quote_plus('pageNo'): pageNo,
            quote_plus('rangeType'): 'ALL',
            quote_plus('orderBy'): 'sim',
            quote_plus('keyword'): unquote(keyword)
        }, encoding='utf-8')
    else:
        queryParams = urlencode({
            quote_plus('pageNo'): pageNo,
            quote_plus('rangeType'): 'ALL',
            quote_plus('orderBy'): 'sim',
            quote_plus('keyword'): unquote(keyword),
            quote_plus('startDate'): unquote(date_date),
            quote_plus('endDate'): unquote(SearchDate[:10]),
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


data = crawler_naver_blog('1010291472', '글로벌에이스', '김선남', None)
df = pd.DataFrame(list(data.items()),columns=["BusinessNum","DataType","SearchDate","SearchID","Data"])
df.to_csv('sample.csv')


'''
naver_blog_data = {
                        "BusinessNum": biz_no,
                        "DataType": DataType,
                        "SearchDate": str(datetime.datetime.now()).replace("T", ""),
                        "SearchID": SearchID,
                        "Data": {
                            'BlogName':blog_name[idx],
                            'AuthorName':author_name[idx],
                            'PostDate':calc_date(post_date[idx]),
                            'PostTitle':post_title[idx],
                            'PostContent':post_content[idx],
                        }

'''

