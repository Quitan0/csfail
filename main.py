import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_initial_history_number(driver):
    coeff_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.link.ng-star-inserted'))
    )
    for elem in coeff_elements:
        href = elem.get_attribute('href')
        if href and "/en/crash/history/" in href:
            history_number = int(href.split('/')[-1])
            return history_number

    raise ValueError("Не удалось найти начальный номер истории")


def get_coefficients(driver, coefficients, n=10000000):
    history_number = get_initial_history_number(driver)
    last_coeff = None
    while len(coefficients) < n:
        try:
            coeff_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'a[href="/en/crash/history/{history_number}"]'))
            )
            coeff_text = coeff_element.text[:-1]
            if coeff_text:  # Добавляем проверку на наличие текста
                coeff = float(coeff_text)
                if coeff != last_coeff:
                    coefficients.append(coeff)
                    last_coeff = coeff
                    print(f"Собрано коэффициентов: {len(coefficients)}, last : {str(last_coeff)}    {history_number}")
                    f = open("csfail.csv", "a")
                    f.write(str(history_number)+ " ; " + str(last_coeff) + "\n")
                    f.close()
                    if len(coefficients) >= n:
                        break

            history_number += 1
            time.sleep(2)
        except Exception as e:
            print(f"Ошибка при получении коэффициента (номер истории: {history_number}): {e}")
            time.sleep(2)
            continue

    return coefficients


options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
service = Service(executable_path='/home/ilya/PycharmProjects/chromedriver')
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://csfail.live/en/crash")
time.sleep(5)
# Получаем коэффициенты
coefficients = get_coefficients(driver, [])

min_coeff, max_coeff = 1.5, 3.0

# Проверяйте текущий коэффициент и выводите сообщение, когда подходит момент для ставки
while True:
    try:
        current_coeff = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.game__info-value--multiplier span'))
        )
        current_coeff = float(current_coeff.text)
        print(f"Текущий коэффициент: {current_coeff:.2f}")
        f = open("csfail.csv", "a")
        f.write(str(current_coeff))
        f.close()


        if min_coeff <= current_coeff <= max_coeff:
            print(f"Сейчас хороший момент для ставки! Коэффициент: {current_coeff:.2f}")

        time.sleep(1)
    except Exception as e:
        print(f"Ошибка при проверке текущего коэффициента: {e}")
        time.sleep(2)
        continue

