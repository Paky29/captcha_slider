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

def create_dataset(total_cap):
    for i in range(total_cap):
        title_content = driver.title
        if title_content == "Captcha":
            WebDriverWait(driver, 200).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-close"))).click()

            sleep(5)

            img = driver.find_element(By.CLASS_NAME, 'cap-div')
            img_url = img.value_of_css_property("background-image").removeprefix("url(\"").removesuffix("\")")
            save_image("comp_img", img_url, i)

            script = """
            var element = document.getElementById('cap_range');
            var pseudoElement = window.getComputedStyle(element, '::-moz-range-thumb');
            return pseudoElement.getPropertyValue('background-image');
            """
            sub_img_url = driver.execute_script(script).removeprefix("url(\"").removesuffix("\")")
            save_image("sub_img", sub_img_url, i)

            solver = driver.find_element(By.NAME, "solve_captcha")
            driver.execute_script("arguments[0].scrollIntoView(true);", solver)

            # Attendi che l'elemento sia cliccabile e fai clic
            solver = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "solve_captcha"))
            )
            solver.submit()

            total_cap += 1
            new_tor_id()
            sleep(5)


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

    driver.get("http://drughubb7lmqymhpq24wmhihloii3dlp3xlqhz356dqdvhmkv2ngf4id.onion")
    WebDriverWait(driver, 200).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-close"))).click()

    sleep(2)

    img = driver.find_element(By.CLASS_NAME, 'cap-div')
    img_url = img.value_of_css_property("background-image").removeprefix("url(\"").removesuffix("\")")
    save_image("comp_img", img_url, "1")

    script = """
                var element = document.getElementById('cap_range');
                var pseudoElement = window.getComputedStyle(element, '::-moz-range-thumb');
                return pseudoElement.getPropertyValue('background-image');
                """
    sub_img_url = driver.execute_script(script).removeprefix("url(\"").removesuffix("\")")
    save_image("sub_img", sub_img_url, "1")

    template_matching.move_input(driver, "comp_img/image1.png", "sub_img/image1.png")

    solver = driver.find_element(By.NAME, "solve_captcha")
    driver.execute_script("arguments[0].scrollIntoView(true);", solver)

    # Attendi che l'elemento sia cliccabile e fai clic
    solver = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "solve_captcha"))
    )
    solver.submit()



