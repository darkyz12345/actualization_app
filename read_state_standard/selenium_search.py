from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from read_state_standard.utils import mult
from PyQt5.QtCore import pyqtSignal

dict_yes_or_no = {'fa fa-times-circle': 'NO',
                  'fa fa-check-circle': 'YES'
                  }

dict_yes_or_no_smile = {'NO': '\U0000274C',
                        'YES': '\U00002705'
                        }

host = "https://uzsti.uz/shop"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'}


def search_st(driver: webdriver.Chrome, wait: WebDriverWait, st: str) -> dict[str, str]:
    input_field = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.form-control.search")))
    res = {'name': '',
           'status': '',
           'term': '-',
           'url': ''}

    standard = st.split()
    input_field.clear()

    # Имитируем ввод ГОСТа (по символам)
    for char in standard[-1]:
        input_field.send_keys(char)
        time.sleep(0.1)

    time.sleep(7)  # чтобы успела обновиться выдача

    # Берём карточки
    cards = driver.find_elements(By.CSS_SELECTOR,
                                 "a.item")

    found = False
    for card in cards:
        try:
            text = card.find_element(By.CSS_SELECTOR, "div[style*='-webkit-line-clamp']").text.strip()
        except:
            continue  # если вдруг нет текста — пропускаем

        # Проверка совпадения по словам
        if all(word in text for word in standard):
            check_classes = card.find_element(By.TAG_NAME, "i").get_attribute("class")
            checkpoint = dict_yes_or_no.get(check_classes, "NO")

            # link_el = card.find_element(By.CSS_SELECTOR, "a.item")
            url = card.get_attribute('href')
            # print(url)
            res["url"] = url

            # Скриншот самой карточки
            card.screenshot(f"screen_{st}.png")

            if checkpoint == "NO":
                card.click()
                time.sleep(3)
                try:
                    date_text = driver.find_element(By.CSS_SELECTOR, "div.pulsingButton").text.strip()
                    res['term'] = date_text
                except:
                    res['term'] = "Не удалось прочитать срок"
                driver.back()
                time.sleep(3)

            res["name"] = text
            res["status"] = dict_yes_or_no_smile[checkpoint]
            found = True
            break

    if not found:
        res['name'] = 'Не найден на сайте'
        res['status'] = 'Не найден на сайте'

    return res

def get_driver(driver:webdriver.Chrome=None):
    if driver:
        driver.close()
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(host)
    wait = WebDriverWait(driver, 10)
    return driver, wait

def get_info_st(driver: webdriver.Chrome, wait: WebDriverWait, st):
    attempts = 5
    res = {}
    while attempts > 0:
        res = search_st(driver, wait, st)
        if (res['name'] == res['status'] and res['term'] == '' and res['url'] == '') == False:
            break
        if attempts == 3:
            driver, wait = get_driver(driver)
        attempts -= 1
    return res, driver, wait

def get_info_st_list(list_standard: list[str], progress_bar: pyqtSignal):
    driver, wait = get_driver()
    res = {}
    total = len(list_standard)
    for i, standard in enumerate(list_standard, start=1):
        tmp_res, driver, wait = get_info_st(driver, wait, standard)
        res[standard] = tmp_res
        progress_bar.emit(int(i * 100 / total))
    driver.close()
    return res



if __name__ == '__main__':
    driver, wait = get_driver()
    print(type(driver), type(wait))
    # print(search_st(driver, wait, 'ГОСТ 10006'))
    # print(search_st(driver, wait, 'ГОСТ 17066-94'))
    # print(search_st(driver, wait, '111111'))
    # print(get_info_st(driver, wait, 'ГОСТ 10006'))
    # print(get_info_st(driver, wait, 'ГОСТ 17066-94'))
    # print(get_info_st(driver, wait, 'ГОСТ 11111111'))
    res, driver, wait = get_info_st_list(['ГОСТ 10006', 'ГОСТ 17066-94', 'ГОСТ 11111111'])
    driver.quit()
    for key, value in res.items():
        print(key)
        for k, v in value.items():
            print(f'{k}: {v}')
        print()

