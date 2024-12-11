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


def genselx():
    # Read the Excel file into a Pandas DataFrame
    df = pd.read_excel(INPUT)

    # Convert to list of dictionaries, handling missing values
    matches = []
    for _, row in df.iterrows():
        match_data = {
            "match": row["TEAMS"],
            "id": str(row["ID"]).replace(" ", ""),  # Remove spaces in the ID
            "categories": []  # Initialize the categories array
        }

        # Iterate through all category columns dynamically
        for col in df.columns[2:]:  # Skip 'TEAMS' and 'ID' columns
            category = {
                "name": col,
                "value": int(row[col]) if not pd.isna(row[col]) else 0  # Default to 0 for NaN
            }
            match_data["categories"].append(category)

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


def check_for_element(driver, selector, click=False, xpath=False, debug=False):
    try:
        if xpath:
            element = driver.find_element(By.XPATH, selector)
        else:
            element = driver.find_element(By.CSS_SELECTOR, selector)
        if click: 
            driver.execute_script("arguments[0].scrollIntoView();", element)
            element.click()
        return element
    except Exception as e: 
        if debug: print("selector: ", selector, "\n", e)
        return None


def check_for_elements(driver, selector, xpath=False, debug=False):
    try:
        if xpath:
            element = driver.find_elements(By.XPATH, selector)
        else:
            element = driver.find_elements(By.CSS_SELECTOR, selector)
        return element
    except Exception as e: 
        if debug: print("selector: ", selector, "\n", e)
        return None


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
            if "/secured/selection/resale/" in driver.current_url:
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


def find_category_value(categories, category_name):
    for category in categories:
        if category['name'] == category_name:
            return category['value']
    return None  # Return None if the category is not found


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
    time_to_wait = int(input('Інтервал оновлення: '))
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


    while True:
        driver.execute_cdp_cmd(
            'Network.setUserAgentOverride', {"userAgent": ua()})
        time.sleep(2)
        driver.execute_script(f"window.open('{link}/','_self')")
        host = check_for_element(driver, '//span[@class="team host"]', xpath=True)
        opposing = check_for_element(driver, '//span[@class="team opposing"]', xpath=True)

        if host is None or opposing is None:
            print('Не вдалось знайти назву матчу')
            time.sleep(time_to_wait)
            continue
        title = f"{host.text} vs {opposing.text}"
        bskt=0
        time.sleep(.5)
        categ_sels=[]
        selected_category = None
        
        main_match = [i for i in selxs_static if i.get('match') == title]
        if not main_match: 
            print('Такого матчу не існує в таблиці.')
            time.sleep(time_to_wait)
            continue
        if check_for_element(driver, 'section[style="display: block;"][id="no_ticket_on_sale"]'):
            print('No tickets on sale.')
            time.sleep(time_to_wait)
            continue
        start_over = False
        
        all_category_names = sorted({category['name'] for category in \
         main_match[0]['categories'] if category['value'] != 0})
        
        # FILTRATION
        no_filtration = False

        seat_categories_table_raw = check_for_elements(driver, \
        '//div[@id="seat_categories_table"]//label/span', xpath=True, debug=True)
        seat_categories_table =\
        [seat_category.text for seat_category in seat_categories_table_raw]
        
        if seat_categories_table_raw:
            for seat_category in seat_categories_table_raw:
                if seat_category.text in all_category_names:
                    categ_sels.append(\
                    f'//tr[.//td[contains(., "{seat_category.text}")]]')
                    time.sleep(1)
                    seat_category.click()
        else:
            categ_sels.append(\
                    f'//tr[.//td[contains(., " ")]]')
            no_filtration = True
        if start_over or categ_sels == []:
            print('Немає необхідних категорій')
            time.sleep(time_to_wait)
            continue
        
        # ADD TICKET
        #//td[@class="resale-item-action"]//span[@class="button"]
        seats = []
        seats_obj = []
        last_added_seat_number = None
        last_added_block_row = None
        previous_category = None
        temp_cat_obj = {}
        filled_cat_obj = False
        while True:
            for itm in driver.find_elements(By.XPATH, "|".join(categ_sels)):
                category_info_raw = None
                category_info = None
                category_info_raw = check_for_element(itm, 
                    './/td[@class="resale-item-seatCat category"]/div/span[2]', xpath=True)
                if category_info_raw: category_info = category_info_raw.text
                if len(seats) >= 6 or filled_cat_obj:
                    break

                
                current_pagination = check_for_element(driver, '//span[@class="page current"]/a', xpath=True)
                if current_pagination:
                    current_pagination = current_pagination.text
                else:
                    start_over = True
                    break

                
                try:
                    seat_info_raw = check_for_element(itm, \
                     './/td[@class="resale-item-seatPath seatPath"]', xpath=True)

                    seat_info = seat_info_raw.text

                    block, row, seat = seat_info.strip().split(' / ')
                    seat_number = int(seat.split(' ')[1])
                    current_block_row = block + " " + row
                    
                    if not no_filtration:
                        if last_added_block_row != current_block_row or \
                        (last_added_seat_number is not None and \
                        abs(seat_number - last_added_seat_number) not in (1, 2)):
                            seats.clear()
                            seats_obj.clear()
                            temp_cat_obj = {}
                    elif no_filtration:
                        if category_info not in all_category_names or \
                         last_added_block_row != current_block_row or \
                        (last_added_seat_number is not None and \
                        abs(seat_number - last_added_seat_number) not in (1, 2)):
                            seats.clear()
                            seats_obj.clear()
                            temp_cat_obj = {}
                    if not temp_cat_obj.get(category_info):
                        temp_cat_obj[category_info] = 0
                    
                    if temp_cat_obj.get(category_info) or temp_cat_obj.get(category_info) == 0:
                        if temp_cat_obj[category_info] < find_category_value(main_match[0]['categories'], category_info):
                            seats.append(seat_info)
                            seats_obj.append({'selenium_obj':itm,\
                            'seat_info':seat_info, 'pagination_level': current_pagination})
                            temp_cat_obj[category_info] += 1
                        elif temp_cat_obj[category_info] >= find_category_value(main_match[0]['categories'], category_info):
                            filled_cat_obj = True
                    last_added_block_row = current_block_row
                    last_added_seat_number = seat_number
                except Exception as e:
                    print(e)
                    pass
            if start_over: break
            pagination_next = check_for_element(driver, \
             '//span[@class="page next"]', xpath=True, click=True)
            
            if not pagination_next:
                while True:
                    pagination_first = check_for_element(driver, \
                    '//span[@class="page previous"]/a',\
                    xpath=True, click=True)
                    if not pagination_first: break
                break
        if start_over: 
            print('No tickets')
            time.sleep(time_to_wait)
            continue
        if filled_cat_obj == False: 
            print('Недостатньо квитків було знайдено')
            time.sleep(time_to_wait)
            continue
        else:
            time.sleep(1)
            for seat_obj in seats_obj:
                check_for_element(driver, \
                f'//span[@class="page "]/a[contains(text(),"{seat_obj['pagination_level']}")]', xpath=True, click=True)
                check_for_element(driver, f'.//td[@class="resale-item-seatPath seatPath"][contains(normalize-space(text()), "{seat_obj['seat_info']}")]', xpath=True, click=True, debug=True)
                
        while True:
            try:
                itms = driver.find_elements(By.XPATH, "|".join(categ_sels))
                break
            except:
                try:
                    dlk = driver.find_element(
                        By.XPATH, '//*[contains(text(),"There are currently no available tickets to resell, please visit us frequently to check availability")]')
                    itms = []
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
        time.sleep(time_to_wait)   

