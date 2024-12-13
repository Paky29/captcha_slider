from stem import Signal
from stem.control import Controller
import requests
from fake_useragent import UserAgent
from time import sleep
from bs4 import BeautifulSoup
import os

session = requests.Session()

def test_creation_of_new_identity(url: str):
    tor_proxy = {
        "http": "socks5h://127.0.0.1:9150",
        "https": "socks5h://127.0.0.1:9150"
    }
    headers = {
        "User-Agent": UserAgent().random
    }
    resp = session.get(url, headers=headers, proxies=tor_proxy)
    return resp


if __name__ == "__main__":
    entry = False
    while not entry:
        resp = test_creation_of_new_identity("http://abacusxqw5uv7amzqazdbxo2nd57vaioblew6m25pbzznaf4ph6nh6ad.onion")
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Access the title content
        title_content = soup.title.string
        if title_content != "ΛNONGUΛRD":
            entry = True
            print(resp.text)
        else:
            sleep(10)

import os

from selenium.common import TimeoutException
from stem import Signal
from stem.control import Controller
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def new_tor_id():
    with Controller.from_port(port=9051) as controller:
      # Authenticating to our controller with the password
      # we used when we used the 'tor --hash-password' command
      controller.authenticate(password="872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C")
      # Send signal to Tor controller to create new identity
      # (a new exit node IP)
      controller.signal(Signal.NEWNYM)


if __name__ == "__main__":
    options = Options()
    options.headless = True
    options.binary_location = r'D:\Tor Browser\Browser\firefox.exe'
    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.socks", "127.0.0.1")
    options.set_preference("network.proxy.socks_port", 9150)

    profile = FirefoxProfile(r"D:\Tor Browser\Browser\TorBrowser\Data\Browser\profile.default")
    options.profile = profile

    driver = webdriver.Firefox(options=options)
    driver.find_element(By.ID, "connectButton").click()
    sleep(10)

    driver.get("http://abacusxqw5uv7amzqazdbxo2nd57vaioblew6m25pbzznaf4ph6nh6ad.onion")
    total_cap = 0
    while total_cap != 30:
        try:
            element = WebDriverWait(driver, 120).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "wait")) #or in caso di un altra pagina
            )
            title_content = driver.title
            #if title_content == "ΛNONGUΛRD v9" or title_content == "Abacus DDOS Protection":
            directory = title_content.replace(" ", "")
            if not os.path.exists(directory):
                os.makedirs(directory)
            sleep(10)
            driver.save_screenshot(directory + "\image" + str(total_cap) + ".png")
            total_cap += 1
            if title_content == "Abacus DDOS Protection":
                img_element = driver.find_element(By.TAG_NAME, 'img')
                img_url = img_element.get_attribute('src')

                with open("image_urls.txt", "a") as file:
                    file.write(img_url + " \n")

                verify_button = driver.find_element(By.CLASS_NAME, "before")

                verify_button.click()
            else:
                driver.refresh()
            new_tor_id()
            sleep(10)
        except TimeoutException:
            # Se il timeout scade prima che l'elemento diventi visibile
            print("Il caricamento della pagina ha impiegato troppo tempo.")

    driver.quit()
