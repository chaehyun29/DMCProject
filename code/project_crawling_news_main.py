
import pandas as pd
import numpy as np
 
import project_crawling_news as cr_news

c = cr_news
comp_data = c.load_company_data()

# c.crawler_naver_news('1010291472', '세프디자인', '김선남', None)


for comp in comp_data.itertuples():
    c.crawler_naver_news(comp[1],comp[2], comp[3], comp[4], None)


