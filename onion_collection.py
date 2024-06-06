import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from stem import Signal
from stem.control import Controller
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from time import sleep
import base64
from selenium.webdriver.common.by import By

import template_matching

def save_image(fold:str, url: str, number: int):
    image_data = url.split(",")[1]

    # Decodifica i dati base64
    image_bytes = base64.b64decode(image_data)


    if not os.path.exists(fold):
        os.makedirs(fold)

    # Salva l'immagine su file
    with open(fold+"/image"+str(number)+".png", "wb") as f:
        f.write(image_bytes)


def new_tor_id():
    with Controller.from_port(port=9051) as controller:
      # Authenticating to our controller with the password
      # we used when we used the 'tor --hash-password' command
      controller.authenticate(password="68780E670F1BDD5460C4060B6C89E1FFFC37A6EA44226E5716979B70DE")
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

    driver.get("http://cebulka7uxchnbpvmqapg5pfos4ngaxglsktzvha7a5rigndghvadeyd.onion/")

    for i in range(20):
        # Switch to the iframe
        iframe = driver.find_element(By.NAME, "captcha")
        driver.switch_to.frame(iframe)

        img = driver.find_element(By.NAME, "position[]")

        img_url = img.get_attribute('src')
        save_image("onion_image", img_url, i)

        driver.refresh()
        sleep(5)

    driver.quit()