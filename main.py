!pip install selenium
!apt-get update 
!apt-get install -y chromium-chromedriver 
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def init_driver():
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
    )
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    return driver


def scrape_hotels(base_urls, pages, output_csv):
    driver = init_driver()
    all_hotels = []

    try:
        for base_url in base_urls:
            for page in range(pages):
                url = f"{base_url}&s={30 * page}"
                print(f"Загружается страница: {url}")
                driver.get(url)

                try:
                    # Динамическое ожидание карточек отелей
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "reviews-travel__item"))
                    )
                except TimeoutException:
                    print(f"Время ожидания истекло для страницы: {url}")
                    continue

                hotel_items = driver.find_elements(By.CLASS_NAME, "reviews-travel__item")

                if not hotel_items:
                    print(f"На странице {page + 1} не найдено отелей.")
                    continue

                for hotel in hotel_items:
                    try:
                        name = hotel.find_element(By.CLASS_NAME, "h4").text.strip()
                    except NoSuchElementException:
                        name = "Не указано"

                    try:
                        link = hotel.find_element(By.TAG_NAME, "a").get_attribute("href")
                    except NoSuchElementException:
                        link = "Не указано"

                    all_hotels.append({"Name": name, "Link": link})

    except Exception as ex:
        print(f"Ошибка при сборе данных: {ex}")

    finally:
        driver.quit()
        print("Сбор данных завершен.")

    save_to_csv(all_hotels, output_csv)


def save_to_csv(hotel_data, output_csv):
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Name", "Link"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for hotel in hotel_data:
            writer.writerow(hotel)
    print(f"Данные успешно сохранены в '{output_csv}'.")


def main():
    base_urls = [
        "https://tury.ru/hotel/?cn=0&ct=464&ht=0&ad=2&ch=0&dt_f=2025-02-08&dt_t=2025-04-10",
        "https://tury.ru/hotel/?cn=0&ct=332855&ht=0&ad=2&ch=0&dt_f=2025-02-08&dt_t=2025-04-10",
        "https://tury.ru/hotel/?cn=0&ct=112465&ht=0&ad=2&ch=0&dt_f=2025-02-08&dt_t=2025-04-10",
    ]
    output_csv = "hotels_data.csv"
    scrape_hotels(base_urls, pages=16, output_csv=output_csv)


if __name__ == "__main__":
    main()
