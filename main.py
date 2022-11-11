# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton
from vk_api.utils import get_random_id
import os
import psycopg2
from threading import Thread
import sqlite3
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# token = "eb7f73e097d72416d1f829dd1b9e5bbc1400c48959713fb935f33a1a76823dd91056bd6a6350e3e64e8ba"
token = 'vk1.a.OvDoILHrDaWMez-iTyDP78WOVyKqqzsTqV8ma6cNnJg2t3X5kXgWZ78LJxYjpVDoTNM9cox-Y70wIhS9knDIgG_SL0_v_sCeoRGxtuumIK2URLjI_MPQAsxzodAl8wEu7hgtUMxKRVm9esupVpEvQ1wYTWm8Xr4dHot4mdATBbTUSEWmGTy-2KpRv2uuWTik4--TtvFWq3HjKcIOm-kOdA'
# conn = sqlite3.connect('marks.sqlite')
conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
cur = conn.cursor()

class MyLongPool(VkLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                print(e)

def write_message(sender, message, keyboard = None, attachments = []):
    post = {
        "user_id": sender,
        "message": message,
        "random_id": get_random_id(),
        "attachment" : ",".join(attachments)
    }
    if attachments != None:
        post["attachment"] =  ",".join(attachments)
    if keyboard != None:
        post["keyboard"] = keyboard.get_keyboard()

    authorize.method("messages.send", post)

authorize = vk_api.VkApi(token=token)
# longpool = MyLongPool(authorize)
longpool = VkBotLongPoll(authorize, '210871312')

def main():
    # conn = sqlite3.connect('marks.sqlite')
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    cur = conn.cursor()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')


    driver = webdriver.Chrome(
        executable_path = os.environ.get("CHROMEDRIVER_PATH"),
        # executable_path='D:\PyCharm\parser_school_mosreg\chromedriver.exe',
        chrome_options = chrome_options
        )
    url = 'https://login.school.mosreg.ru/?ReturnUrl=https%3a%2f%2fschools.school.mosreg.ru%2fmarks.aspx%3fschool%3d2000000000664%26tab%3dweek'
    try:
        driver.get(url)
        time.sleep(1)
        login_input = driver.find_element(By.CSS_SELECTOR, "input[name='login'].mosreg-login-form__input")
        login_input.clear()
        login_input.send_keys("gorshunov.maksim")
        pass_input = driver.find_element(By.CSS_SELECTOR, "input[name='password'].mosreg-login-form__input")
        pass_input.clear()
        pass_input.send_keys("Secretno444")
        btn_submit = driver.find_element(By.CSS_SELECTOR, "input[type='submit'].mosreg-button")
        time.sleep(0.3)
        btn_submit.click()
        time.sleep(1.5)
        #получение блока с  оценками
        while True:
            driver.refresh()
            time.sleep(1)
            block_with_data = driver.find_element(By.ID, 'user-start-page').get_attribute('innerHTML')
            html = BeautifulSoup(block_with_data, "lxml")
            data = html.find('div').find('div').next_sibling.find('div').next_sibling
            for el in data.find_all('div', attrs={'data-mark-id': True}):
                mark = el.find('div').next_sibling.next_sibling.next_sibling.text
                subject = el.find('div').next_sibling.next_sibling.text
                ocenka = el.find('div').text
                date_end = ''
                for chr in mark:
                    if chr.isalnum():
                        date_end += chr
                date_end = ' за '.join(date_end.split('за'))
                data_with_mark = (subject, date_end, ocenka)
                cur.execute(f" SELECT * FROM marks WHERE subject='{subject}' and date='{date_end}' and mark='{ocenka}';")
                one_result = cur.fetchall()
                conn.commit()
                if len(one_result) == 0:
                    cur.execute(f" INSERT INTO marks (subject, date, mark) VALUES('{subject}', '{date_end}', '{ocenka}')")
                    conn.commit()
                    write_message(483550384, f'Новая оценка: {subject} {date_end} {ocenka}')
            time.sleep(60)
    except Exception as _ex:
        write_message(483550384, f'{datetime.now()} - {_ex}')
        print(_ex)
    finally:
        driver.close()
        driver.quit()

def listenVk():
    while True:
        for event in longpool.listen():
            if event.type == 'like_add':
                print('like')
            print(event.type)
            if event.type == VkBotEventType.MESSAGE_NEW:
                reseived_message = event.object.message['text']
                sender = event.object.message['from_id']
                text = reseived_message.lower()
                attachments = []
                if text == 'какие предметы мне подтянуть?':
                    result1 = []
                    result2 = []
                    keyboard = VkKeyboard(one_time=False)
                    keyboard.add_button("Какие предметы мне подтянуть?", color=VkKeyboardColor.PRIMARY)
                    write_message(sender, 'Сейчас пришлю. Минутку...', keyboard)
                    try:
                        # conn = sqlite3.connect('marks.sqlite')
                        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
                        cur = conn.cursor()
                        chrome_options = webdriver.ChromeOptions()
                        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
                        chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
                        chrome_options.add_argument('--headless')
                        chrome_options.add_argument('--disable-dev-shm-usage')
                        chrome_options.add_argument('--no-sandbox')
                        driver = webdriver.Chrome(
                            executable_path = os.environ.get("CHROMEDRIVER_PATH"),
                            # executable_path='D:\PyCharm\parser_school_mosreg\chromedriver.exe',
                            # service=Service(),
                            chrome_options = chrome_options
                            )
                        url = 'https://login.school.mosreg.ru/?ReturnUrl=https%3a%2f%2fschools.school.mosreg.ru%2fmarks.aspx%3fschool%3d2000000000664%26tab%3dweek'
                        try:
                            driver.get(url)
                            time.sleep(1)
                            login_input = driver.find_element(By.CSS_SELECTOR, "input[name='login'].mosreg-login-form__input")
                            login_input.clear()
                            login_input.send_keys("gorshunov.maksim")
                            pass_input = driver.find_element(By.CSS_SELECTOR, "input[name='password'].mosreg-login-form__input")
                            pass_input.clear()
                            pass_input.send_keys("Secretno444")
                            btn_submit = driver.find_element(By.CSS_SELECTOR, "input[type='submit'].mosreg-button")
                            time.sleep(0.3)
                            btn_submit.click()
                            time.sleep(1.5)
                            progress = driver.find_element(By.CSS_SELECTOR, "a[title='Успеваемость'].header-submenu__link")
                            progress.click()
                            time.sleep(1)
                            tabPeriod = driver.find_element(By.ID, 'TabPeriod')
                            tabPeriod.click()    
                            
                        except Exception as _ex:
                            write_message(483550384, f'{datetime.now()} - {_ex}')
                            print(_ex)
                        driver.refresh()
                        time.sleep(1)
                        block_with_data = driver.find_element(By.TAG_NAME, 'tbody').get_attribute('innerHTML')
                        html = BeautifulSoup(block_with_data, "lxml")
                        data = html.find_all('tr')
                        for el in range(2, len(data)):
                            try:
                                avg_mark = float(data[el].find('span', class_='analytics-app-popup-avgmark').text.replace(',', '.'))
                                if avg_mark <= 4.5:
                                    subject = data[el].find('td', class_='s2').find('strong', class_='u').text
                                    if avg_mark < 4.5:
                                        result1.append(f'{subject} - Балл: {avg_mark}')
                                    else:
                                        result2.append(f'{subject} - Балл: {avg_mark}')
                            except:
                                pass
                        if len(result1) >= 1 or len(result2) >= 1:
                            message = ""
                            if len(result1) >= 1:
                                message += f"🆘 Предметы подтянуть:\n" + "\n".join(result1)
                            if len(result2) >= 1:
                                message += '\n\n⚠ Граничный балл: \n' + "\n".join(result2)
                            write_message(sender, message, keyboard)

                        else:
                            write_message(sender, 'На данный момент вы отличник!', keyboard)

                    except Exception as _ex:
                        write_message(483550384, f'{datetime.now()} - {_ex}')
                        print(_ex)
                    finally:
                        driver.close()
                        driver.quit()
                    continue

if __name__ == '__main__':
    # cur.execute('''
    #     CREATE TABLE IF NOT EXISTS marks(
    # id INTEGER NOT NULL generated always as identity,
    # subject VARCHAR,
    # date VARCHAR,
    # mark VARCHAR);
    # ''')
    # conn.commit()
    process1 = Thread(target=main)
    process2 = Thread(target=listenVk)
    process1.start()
    process2.start()


    
    
