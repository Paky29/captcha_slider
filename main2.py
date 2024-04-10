import os
from selenium.common import NoSuchElementException
from stem import Signal
from stem.control import Controller
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from time import sleep
import base64
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent

def save_image(url: str, number: int):
    image_data = url.split(",")[1]

    # Decodifica i dati base64
    image_bytes = base64.b64decode(image_data)

    if not os.path.exists("text"):
        os.makedirs("text")

    # Salva l'immagine su file
    with open("text/image"+str(number)+".png", "wb") as f:
        f.write(image_bytes)


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
        title_content = driver.title
        if title_content == "ΛNONGUΛRD v9" or title_content == "Abacus DDOS Protection":

            directory = title_content.replace(" ", "")
            if not os.path.exists(directory):
                os.makedirs(directory)
            sleep(10)

            driver.save_screenshot(directory + "\image" + str(total_cap) + ".png")

            if title_content == "Abacus DDOS Protection":
                try:
                    img_element = driver.find_element(By.TAG_NAME, 'img')
                    img_url = img_element.get_attribute('src')

                    save_image(img_url, total_cap)

                    verify_button = driver.find_element(By.CLASS_NAME, "before")

                    verify_button.click()
                except NoSuchElementException:
                    os.remove(directory + "\image" + str(total_cap) + ".png")
                    total_cap-=1
            else:
                driver.refresh()
            total_cap += 1
            new_tor_id()
            sleep(10)
        elif title_content == "504 Gateway Time-out":
            driver.refresh()
    driver.quit()
