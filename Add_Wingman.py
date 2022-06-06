# MAKE SURE CART IS EMPTY
# AND YOU HAVE AT LEAST ONE COURSE ADDED ALREADY
# AND YOUR WANTED COURSE IS AT TOP OF ITS CATEGORY (that is, some GEA shit)
# TO ACCESS SEARCH RESULT IN A PRECISE WAY, MODIFY LINE 240-254

from selenium.webdriver import Chrome
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By 
from selenium.webdriver import ChromeOptions

import time
import winsound
import os
import sys
import inspect
import urllib.request
import requests
import ddddocr
import getpass

targets = [
    'L01-LEC(1179)', # eie
    # 'L02-LEC(1268)', #gea
    # 'L01-LEC(1141)'
    ]

category = "GEA"
category = "EIE"

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, currentdir) 

option = ChromeOptions()
option.add_argument('--ignore-certificate-errors')
option.add_argument('--ignore-ssl-errors')
option.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = Chrome(options=option)

def try_till_done(f,args):
    print('waiting',args)
    while True:
        try:
            ret = f(*args)
            break
        except:
            print('waiting',args)
            time.sleep(.05)
            pass
    return ret

def wait_processing():
    time.sleep(0.1)
    print("waiting for processing")
    i = driver.find_element(By.ID, "processing")
    try:
        while i.is_displayed():
            time.sleep(0.01)
    except:
        pass        
    time.sleep(0.05)

def refresh_search_result():
    i = driver.find_element(By.ID,"CLASS_SRCH_WRK2_SSR_PB_MODIFY")
    i.click()
    i.click()
    wait_processing()
    i = driver.find_element(By.ID,"CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")
    i.click()

def check_vacant_targets() -> str:
    # abandoned
    # returns 4-digit id
    for target in targets:
        try:
            print("finding",target)
            i = driver.find_element(By.LINK_TEXT,target)
            id = i.get_attribute("name").split("$")[-1]
            print("Found Matched:",target,end=" ... ")

            i = driver.find_element(By.ID, f"win0divDERIVED_CLSRCH_SSR_STATUS_LONG${id}")
            i = i.find_element(By.TAG_NAME,'img')
            alt = i.get_attribute("alt")
            print(alt)

            if alt == "Open":
                return target[-5:-1]
        except:
            pass
    print("Not found")
    return None

def check_vacant_targets_and_add():
    # try to access "select class" button @ search result page
    # returns id instead of idx
    for target in targets:
        try:
            print("finding",target)
            i = driver.find_element(By.LINK_TEXT,target)
            idx = i.get_attribute("name").split("$")[-1]
            print("Found a Match:",target,end=" ... ")


            i = driver.find_element(By.ID, f"win0divDERIVED_CLSRCH_SSR_STATUS_LONG${idx}")
            i = i.find_element(By.TAG_NAME,'img')
            alt = i.get_attribute("alt")
            print(alt)

            if alt == "Open":
                i = driver.find_element(By.ID, f"CLASS_SRCH_WRK2_SSR_PB_SELECT${idx}")
                i.click()
                return target[-5:-1]
        except:
            print("Can not add it to cart, most likely due to it's in cart already")
            pass
    print("Not found")
    return None

def select_vacant_tut_and_add() -> bool:
    # return boolean
    i = driver.find_elements(By.CSS_SELECTOR,'div[id^="win0divDERIVED_CLS_DTL_SSR_STATUS_LONG$229$$"]')
    id = None
    for e in i:
        alt = e.find_element(By.TAG_NAME,'img')
        alt = alt.get_attribute('alt')
        print("tut ",e.get_attribute('id')[-1], '...', alt)
        if alt == "Open":
            id = e.get_attribute("id").split("$$")[-1]
            radio = driver.find_element(By.ID,f"SSR_CLS_TBL_R1$sels${id}$$0")
            radio.click()
            wait_processing()
            next = driver.find_element(By.LINK_TEXT,"Next")
            next.click()
            wait_processing()
            next = driver.find_element(By.LINK_TEXT,"Next")
            wait_processing()
            next.click()
            return True
    return False

def finish_vcode():
    ocr = ddddocr.DdddOcr(show_ad=False)
    while 1:
        i = driver.find_element(By.ID,'imgCaptcha')
        i = i.get_attribute('src')
        bogus = i.split("=")[-1]
        urllib.request.urlretrieve(i,"vcode.png")
        with open("vcode.png",'rb') as f:
            image = f.read()

        res = ocr.classification(image)
        print(res)

        cookies = driver.get_cookies()
        cookies = {d['name']:d['value'] for d in cookies}


        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://sis.cuhk.edu.cn',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        params = {
                'HK_InputValue': res,
                'bogus': bogus,
            }

        response = requests.post('https://sis.cuhk.edu.cn/ValidationServlet',cookies=cookies, params=params, headers=headers)


        if response.text.rstrip() == "Y":
            i = driver.find_element(By.ID,"inputValue")
            i.send_keys(res)
            break
        else:
            i = driver.find_element(By.CSS_SELECTOR,'img[alt="Refresh"]')
            i.click()

def enrol(courseid):
    # MAKE SURE CART IS EMPTY!
    # switch to newest semester
    radios = driver.find_elements(By.CLASS_NAME,"PSRADIOBUTTON")
    radios = [(i,i.get_attribute('id')) for i in radios]
    radios = sorted(radios,key=lambda x:x[1])
    i = radios[-1][0]
    i.click()
    i = driver.find_element(By.LINK_TEXT,"Continue")
    i.click()
    wait_processing()
    # go for the first course in cart
    i = driver.find_element(By.ID, "P_SELECT$0")
    i.click()

    # to avoid a strange server-side bug (says wrong code but it's correct)
    time.sleep(0.1)
    finish_vcode()
    i = driver.find_element(By.ID,"DERIVED_REGFRM1_LINK_ADD_ENRL")
    i.click()
    wait_processing()
    i = driver.find_element(By.ID,"DERIVED_REGFRM1_SSR_PB_SUBMIT")
    time.sleep(5)
    i.click()
    
# Login
time.sleep(2)
id = input('ID? ')
pwd = getpass.getpass('Password? ')
driver.get("https://sis.cuhk.edu.cn/")
time.sleep(0.1)
login_a = driver.find_element_by_link_text("Please click here to PeopleSoft logon page")
login_a.click()
lang_select = try_till_done(driver.find_element,(By.TAG_NAME,"select"))
lang_select = Select(lang_select)
lang_select.select_by_value("ENG")
user_id_input = driver.find_element(By.ID,'userid')
user_id_input.send_keys(id)
pwd_input = driver.find_element(By.ID,'pwd')
pwd_input.send_keys(pwd)
sign_in = driver.find_element(By.NAME,'Submit')
sign_in.submit()

# Search Page
i = driver.get("https://sis.cuhk.edu.cn/psp/csprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?PORTALPARAM_PTCNAV=HC_CLASS_SEARCH&EOPP.SCNode=HRMS&EOPP.SCPortal=EMPLOYEE&EOPP.SCName=CO_EMPLOYEE_SELF_SERVICE&EOPP.SCLabel=Self%20Service&EOPP.SCPTfname=CO_EMPLOYEE_SELF_SERVICE&FolderPath=PORTAL_ROOT_OBJECT.CO_EMPLOYEE_SELF_SERVICE.HCCC_SS_CATALOG.HC_CLASS_SEARCH&IsFolder=false")
driver.switch_to.frame(try_till_done(driver.find_element,(By.ID, 'ptifrmtgtframe')))
i = driver.find_element(By.ID,'SSR_CLSRCH_WRK_SSR_OPEN_ONLY$3')
i.click()
i = Select(driver.find_element(By.NAME,'SSR_CLSRCH_WRK_SUBJECT$0'))
i.select_by_value(category)
wait_processing()
i = Select(driver.find_element(By.ID,'SSR_CLSRCH_WRK_ACAD_CAREER$2'))
i.select_by_value("UG")
wait_processing()
i = driver.find_element(By.ID,'CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH')
i.click()
wait_processing()
i = driver.find_element(By.LINK_TEXT,'View All Sections')
i.click()
wait_processing()



# loop till target is available
while 1:
    id = check_vacant_targets_and_add()
    if id:
        winsound.MessageBeep()
        print("going for", id)
        wait_processing()
        break
    refresh_search_result()
    wait_processing()

select_vacant_tut_and_add()
time.sleep(0.05) # defensive
i = driver.get("https://sis.cuhk.edu.cn/psc/csprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL?Page=SSR_SSENRL_CART&Action=A")
enrol(id)

while 1:
    time.sleep(100)