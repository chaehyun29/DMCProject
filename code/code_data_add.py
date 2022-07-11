#code를 크게 분류하여 변경하는 함수
def change_code(code):
  code = int(code)
  if (code>=10)&(code<=11):return '10'
  elif (code==12):return '12'
  elif (code>=13)&(code<=15):return '13'
  elif (code==16):return '16'
  elif (code>=17)&(code<=18):return '17'  
  elif (code>=19)&(code<=25):return '19'
  elif (code>=26)&(code<=31):return '26'
  elif (code>=32)&(code<=33):return '32'
  elif (code==34):return '34'
  elif (code>=35)&(code<=39):return '35'
  elif (code>=41)&(code<=42):return '41'
  elif (code>=45)&(code<=47):return '45'
  elif (code>=49)&(code<=52):return '49'
  elif (code==55):return '55'
  elif (code==56):return '56'
  elif (code>=58)&(code<=63):return '58'
  elif (code>=64)&(code<=66):return '64'
  elif (code==68):return '68'
  elif (code>=70)&(code<=73):return '70'
  elif (code>=74)&(code<=76):return '74'
  elif (code==84):return '84'
  elif (code==85):return '85'
  elif (code>=86)&(code<=87):return '86'
  elif (code>=90)&(code<=91):return '90'
  elif (code==94):return '94'
  elif (code>=95)&(code<=96):return '95'
  elif (code==97):return '97'
  elif (code==98):return '98'
  elif (code==99):return '99'

#코드 인덱스 컬럼 생성
all_data_copy['c_index'] = all_data_copy['code'].apply(lambda x : change_code(x))


#크게 분류한 코드의 분류명 딕셔너리
industry_dict = {'10':'식음료 제조업','12':'담배 제조업','13':'패션 제조업','16':'가구 제조업','17':'출판 관련 제조업','19':'특수가공물질 제조업',
                 '26':'기기류 제조업','32':'단순 제조업','34':'산업용 기계 및 장비 수리업','35':'에너지 자원 관련','41':'건설업',
                 '45':'도소매업','49':'운수 및 창고업','55':'숙박업','56':'음식점','58':'정보통신업','64':'금융 및 보험','68':'부동산업',
                 '70':'전문과학기술업','74':'사업관리지원','84':'공공 행정','85':'교육','86':'보건복지','90':'관광산업','94':'협회',
                 '95':'AS','97':'가구 내 고용 활동','98':'재화','99':'국제 및 외국기관'}

#코드 분류명 컬럼 생성
all_data_copy['c_name']=[industry_dict[x] for x in list(all_data_copy['c_index'])]