#from selenium import webdriver
import undetected_chromedriver as webdriver
import time
from selenium.webdriver.common.by import By
from random import choice
from twocaptcha import TwoCaptcha
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
import requests,os
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
import pandas as pd
import random
import soundfile as sf
import sounddevice as sd


api_key = "29ada3bf8a7df98cfa4265ea1145c77b"
INPUT='input.xlsx'

TIMEWAIT = 6


def genselx():
    # Read the Excel file into a Pandas DataFrame
    df = pd.read_excel(INPUT)

    # Convert to list of dictionaries, handling missing values
    matches = []
    for _, row in df.iterrows():
        match_data = {
            "match": row["TEAMS"],
            "id": str(row["ID"]).replace(" ", "")  # Remove spaces in the ID
        }

        # Iterate through all category columns dynamically
        for col in df.columns[2:]:  # Skip 'TEAMS' and 'ID' columns
            match_data[col] = int(row[col]) if not pd.isna(row[col]) else 0  # Default to 0 for NaN

        matches.append(match_data)

    return matches




def ua():
    with open('uas') as ugs:
        uas=[x.strip() for x in ugs.readlines()]
        ugs.close()
    return choice(uas)


def downloadFile(url):
    try:
        os.remove('captcha.png')
    except:
        pass
    with requests.get(url, stream=True, headers={


        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://access.tickets.fifa.com/pkpcontroller/wp/FWCMaint2/index_en.html?queue=05-FWC22-FCFS-PROD',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }) as r:
        r.raise_for_status()
        with open('captcha.png', 'wb') as f:
            chunk_num = 1
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                chunk_num = chunk_num + 1


def solveit():
    solver = TwoCaptcha(api_key)
    try:
        result = solver.normal('captcha.png')['code']
        return [1, result]
    except Exception as e:
        return [0, 0]


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


def wait_for_page_load(driver, timeout=30):
    """
    Waits until the page is fully loaded.

    :param driver: The WebDriver instance.
    :param timeout: The maximum time to wait for the page to load.
    :return: None
    :raises TimeoutException: If the page does not load within the timeout.
    :raises WebDriverException: For WebDriver-related errors.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("Page fully loaded!")
    except TimeoutException:
        print("Timeout: The page did not load completely within the given time.")
        raise
    except WebDriverException as e:
        print(f"WebDriver error occurred: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise


def genhead():
    headers = {}
    headers["user-agent"]= ua()
    return headers
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
#options.add_argument("--incognito")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--log-level=3")
options.add_argument("--disable-web-security")
options.add_argument("--disable-site-isolation-trials")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--lang=EN')


prefs = {"credentials_enable_service": False,
     "profile.password_manager_enabled": False}
options.add_experimental_option("prefs", prefs)
if __name__=='__main__':
    selxs_static=genselx()
    USR = input('Username: ')
    PWD = input('Password: ')
    link = input('Link: ')
    chromedriver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
    
    # Create a Service object using the chromedriver path
    service = Service(executable_path=chromedriver_path)
    if os.getlogin() in ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15',
    'S3U1', 'S3U2', 'S3U3', 'S3U4', 'S3U5', 'S3U6', 'S3U7', 'S3U8', 'S3U9', 'S3U10', 'S3U11', 'S3U12', 'S3U13', 'S3U14', 'S3U15', 'S3U16',
    'Admin3']:
        driver = webdriver.Chrome(
            version_main=129,
            options=options,
            enable_cdp_events=True
        )
    else:
        driver = webdriver.Chrome(
            options=options,
            enable_cdp_events=True
        )
    driver.get(link)
    #input('*')
    loginorfindx(link)
    try:
        driver.find_element(
            By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
    except:
        pass
    stc=input('Use Static selector(y/n):')
    if stc.lower()=='y':
        print('ID', "Match")
        for i, x in enumerate(selxs_static):
            print(i, x['match'])

        idxs = input('Insert match Index:').split(',')
        selxs = []

        for idx in idxs:
            idx = int(idx)
            match_data = selxs_static[idx]

            # Filter out non-category fields (e.g., match, id)
            categories = [
                {"name": key, "value": value}
                for key, value in match_data.items()
                if key not in ["match", "id"]  # Add additional fields to exclude here if needed
            ]

            # Restructure the data
            match_data_with_categories = {
                "match": match_data["match"],
                "id": match_data["id"],
                "categories": categories,
                "selector": f'//li[contains(@id,"{match_data["id"]}")]//*[@class="button performance-select-btn"]'
            }
            selxs.append(match_data_with_categories)

        selx = '|'.join([sel['selector'] for sel in selxs])
        # print("selxs",selxs)
    else:
        venue = ''
        vyn = input('Select venue (y|n): ')
        if vyn.lower() == ('y'):
            print('ID', 'Venue')
            for v in driver.find_elements(By.XPATH, '//*[@id="venue"]//option'):
                print(v.get_attribute('value'), v.text)
            venue = input('Type Venue ID: ').strip()
        team = ''
        tyn = input('Select team (y|n): ')
        if tyn.lower() == ('y'):
            print('ID', 'Team')
            for t in driver.find_elements(By.XPATH, '//*[@id="team"]//option'):
                print(t.get_attribute('value'), t.text)
            team = input('Type team ID: ').strip()

        selx=f'//li[contains(@data-venue-id,"{venue}") and (contains(@data-opposing-team-id,"{team}") or contains(@data-host-team-id,"{team}"))]//*[@class="button performance-select-btn"]'
    while True: 
        # print("selx",selx)
        driver.execute_cdp_cmd(
            'Network.setUserAgentOverride', {"userAgent": ua()})
        time.sleep(2)
        driver.execute_script(f"window.open('{link}/','_self')")
        # driver.get('https://resale-intl.fwc22.tickets.fifa.com/')
        if 'too many' in driver.page_source:
            print('too many')
            time.sleep(10)
            continue
        # if venue != "":
        #     Select(ensure_check_elem('//*[@id="venue"]')).select_by_value(venue)
        # if team != "":
        #     Select(ensure_check_elem('//*[@id="team"]')).select_by_value(team)
        main_match = None
        brk = 0
        while True:
            try:
                listings = driver.find_elements(
                    By.XPATH, selx)
                if len(listings) == 0:
                    break
                brk = 1
                random_listing = choice(list(range(len(listings))))
                
                element=listings[random_listing]

                driver.execute_script("arguments[0].click();", element)

                # driver.execute_script(
                #     f"document.querySelectorAll('.button.performance-select-btn')[{choice(list(range(len(listings))))}].click()")
                break
            except Exception as fdf:
                print(fdf)
                pass
        # print(brk)

        if brk == 0:
            continue
        #try:driver.execute_script('''for (i of [0,1,2,3,4,5,6]){document.querySelectorAll('a[title="Select"]')[0].click()}''')
        #except:pass
        # print('before bskt=0-')
        host = driver.find_element(By.XPATH, '//span[@class="team host"]').text
        opposing = driver.find_element(By.XPATH, '//span[@class="team opposing"]').text
        title = f"{host} vs {opposing}"
        # print(title)
        bskt=0
        time.sleep(.5)
        categ_sels=[]
        selected_category = None
        # print('selxs', selxs)
        for i in selxs:
            if i.get('match'):
                # print(i.get('match'))
                if i.get('match') == title:
                    all_category_names = sorted({category['name'] for category in i['categories'] if category['value'] != 0})
                    # print("all_category_names",all_category_names)
                    selected_category = random.choice(all_category_names)
                    categ_sels.append(f'//tr[.//th[contains(., "{selected_category}")]]//select[@aria-label="Quantity"]')

        for itm in range(len(driver.find_elements(By.XPATH, "|".join(categ_sels)))):
            if bskt>=6:
                break
            try:
                selected_value = {category['name']: category['value'] for item in selxs for category in item['categories']}.get(selected_category, None)
                # print(selected_value)
                elem = ensure_check_elem("|".join(categ_sels),click=True,tmt=1)
                dropdown = Select(elem)
                
                dropdown.select_by_value(str(selected_value))
                #itm.click()
                bskt+=1
            except Exception as e:
                print(e)
                pass
        # print(categ_sels)
        while True:
            try:
                itms = driver.find_elements(By.XPATH, "|".join(categ_sels))
                # print('Try')
                break
            except:
                # print('EXCEPT')
                try:
                    dlk = driver.find_element(
                        By.XPATH, '//*[contains(text(),"There are currently no available tickets to resell, please visit us frequently to check availability")]')
                    itms = []
                    # print('except success')
                    break
                except:
                    pass
        # uslct=0
        # while True:
        #     if uslct>=15:
        #         print('tmt9999')
        #         break

        #     uns_itms=driver.find_elements(By.XPATH,'//a[@title="UNSELECT"]')
        #     if len(uns_itms)>=bskt:
        #         break
        #     else:
        #         time.sleep(.5)
        #         uslct+=1
        if len(itms) != 0:
            ensure_check_elem('//*[@id="book"]', click=True)
            try:
                ensure_check_elem('//*[@id="restart"]', click=True, tmt=2)
            except Exception as dd:
                try:
                    ensure_check_elem('//*[@id="addOtherProducts"]', tmt=2)
                    data_play, fs = sf.read('noti.wav', dtype='float32')  
                    sd.play(data_play, fs)
                    status = sd.wait()
                    input('TAP ENTER TO FIND OTHER TIKETS')
                except:
                    pass
        time.sleep(TIMEWAIT)   

