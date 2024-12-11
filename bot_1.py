from selenium import webdriver
import undetected_chromedriver as webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from threading import Thread
from random import choice
import pandas as pd

TIMEWAIT = 1
INPUT='input.xlsx'

def ua():
    with open('uas') as ugs:
        uas=[x.strip() for x in ugs.readlines()]
        ugs.close()
    return choice(uas)


def ensure_check_elem(selector, methode=By.XPATH, tmt=20, click=False):
    global driver
    var = None
    tmt0 = 0
    while True:
        if tmt0 >= tmt:
            raise Exception('Not Found')
        try:
            var = driver.find_element(methode, selector)
            if click:
                var.click()
            break
        except:
            pass
        tmt0 += 0.5
        time.sleep(0.5)
    return var


def check():
    while True:
        a = input('>> ')
        if a == "exit":
            break
        try:
            print(eval(a))
        except Exception as r:
            print(r)


def loginorfindx(link, sel=''):
    
    solved = 0
    while True:
        if solved == 0:
            try:
                e=driver.find_element(By.XPATH,'//*[@id="img_captcha"]')
                i_url = ensure_check_elem('//*[@id="img_captcha"]', tmt=2).screenshot_as_png
                try:
                    os.remove('captcha.png')
                except:
                    pass
                r=open('captcha.png','wb')
                r.write(i_url)
                r.close()

                capres = solveit()
                if capres[0] == 1:
                    ensure_check_elem('//*[@id="secret"]').send_keys(capres[-1])
                    ensure_check_elem('//*[@id="submit_button"]', click=True)
                
            except:
                pass
            
        try:
            driver.find_element(By.XPATH,
                                '//*[@id="actionButtonText"]').click()
            solved=1
        except:
            pass

        if sel != "":
            try:
                seled = driver.find_element(By.XPATH, sel)
                break
            except:
                pass
        else:
            if "/event/date/product/" in driver.current_url:
                break
            else:
                pass

            try:
                eml = ensure_check_elem('//form[@id="frmLogin"]//input[@name="email"]', tmt=2)
                eml.clear()
                for k in USR:
                    eml.send_keys(k)
                    time.sleep(.1)
                time.sleep(2)
                pwd = ensure_check_elem('//form[@id="frmLogin"]//input[@name="password"]', tmt=2)
                pwd.clear()
                for k in PWD:            
                    pwd.send_keys(k)
                    time.sleep(.1)
                time.sleep(4)
                try:
                    driver.find_element(
                        By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
                except:
                    pass
                ensure_check_elem('//button[@type="submit" and @data-skform="frmLogin"]', tmt=2, click=True)
                # time.sleep(5)
                timer = 15
                while timer > 0:
                    if 'auth.fifa.com' not in driver.current_url: 
                        break
                    else:
                        timer -= 1
                        time.sleep(1)
                if link and timer > 0: driver.get(link)
            except:
                pass

def genselx():
    vals=pd.read_excel(INPUT).values.tolist()
    matches= []
    for val in vals:
        for i,c in enumerate(val[2:]):
            try:
                matches.append({
                    "id":val[1],
                    f"{i+1}":int(c)
                    })
            except:
                pass
    return matches

def cockpp():
    global driver
    global cock
    while cock!=1:
        try:
            driver.find_element(By.XPATH,'//*[@id="onetrust-accept-btn-handler"]').click()
            cock=1
            return cock
        except:
            pass
def genhead():
    headers = {}
    headers["user-agent"]= ua()
    return headers

options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")
options.add_argument('--lang=EN')
options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
prefs = {"credentials_enable_service": False,
     "profile.password_manager_enabled": False}
options.add_experimental_option("prefs", prefs)
coo88=False
if __name__=='__main__':    
    USR = input('Username: ').strip()
    PWD = input('Password: ').strip()
    driver = webdriver.Chrome(options=options)
    driver.get('chrome://extensions/')
    link = input('link')
    cock=0
    t=Thread(target=cockpp)
    t.start()
    
    while True: 
        selxs=genselx()
        driver.execute_cdp_cmd(
            'Network.setUserAgentOverride', {"userAgent": ua()})
        matchx=choice(selxs)
        
        mtc=matchx['id']
        CATEG=list(matchx.keys())[-1]
        SEATS=matchx[f'{CATEG}']

        try:
            driver.get(link)
            loginorfindx(link)
            if 'too many' in driver.page_source or '503 Service Unavailable' in driver.page_source or "HTTP ERROR 429" in  driver.page_source:
                time.sleep(10)
                continue
        except:

            continue

        
        if CATEG==1:
            selv=2
        elif CATEG==2:
            selv=7
        else:
            selv=12
        unv=0
        while True:
            try:
                ryh=driver.find_element(By.XPATH,'//*[contains(@class,"quan")][contains(text(),"0 tickets")]')
            except:
                break
            try:
                Select(ensure_check_elem(f'//table//tr[{selv}]//select[contains(@id,"qua")]',tmt=1.5)).select_by_value(str(SEATS))
            except:
                unv=1
                break
            
        if unv == 0:
            try:
                while True:
                    try:
                        book=driver.find_element(By.XPATH,'//*[@id="book"]')
                    except:raise Exception('NF BOOK')
                    try:
                        book.click()
                        break
                    except:
                        pass
            except:
                continue
            try:
                ensure_check_elem('//*[@class="message success "]/p[contains(text(),"ucces")]', tmt=2)
                ch852=input('SUCCESS : TAP Enter to continue: ')
            except:
                continue
            
        if "https://access.tickets.fifa.com/pkpcontrolle" in driver.current_url:
            time.sleep(3)
            
            try:
                ensure_check_elem('//*[@id="actionButton"]',tmt=3,click=True)
            except:
                pass
            loginorfindx()
            logged=True
            continue
        
        try:
            driver.find_element(By.XPATH,'//*[@id="warningTimeoutWRButton"]').click()
            
        except:
            pass
        time.sleep(TIMEWAIT)   

