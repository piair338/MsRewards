from modules.imports import *


def welcome_tour(elm, driver):
    try : 
        driver.find_element(By.CSS_SELECTOR, '[class="welcome-tour-next-button c-call-to-action c-glyph"]').click()
    except :
        pass
    driver.find_element(By.CSS_SELECTOR, '[class="quiz-link gray-button c-call-to-action c-glyph f-lightweight"]').click()
    sleep(5)
    driver.find_element(By.CSS_SELECTOR, '[class="c-glyph glyph-cancel"]').click()
    elm.click()
    driver.find_element(By.CSS_SELECTOR, '[class="quiz-link gray-button c-call-to-action c-glyph f-lightweight"]').click()
    sleep(5)
    driver.find_element(By.CSS_SELECTOR, '[class="c-glyph glyph-cancel"]').click()
    elm.click()
    driver.find_element(By.CSS_SELECTOR, '[class="quiz-link gray-button c-call-to-action c-glyph f-lightweight"]').click()
    sleep(5)
    driver.find_element(By.CSS_SELECTOR, '[class="c-glyph glyph-cancel"]').click()

def welcome_tour_NO(driver):
    try : 
        driver.find_element(By.CSS_SELECTOR, '[class="welcome-tour-next-button c-call-to-action c-glyph"]').click()
    except :
        pass
    driver.find_element(By.CSS_SELECTOR, '[class="c-glyph glyph-cancel"]').click()
    sleep(5)


def spotify(driver):
    sleep(5)
    driver.find_element(By.CSS_SELECTOR, '[data-bi-id="spotify-premium gratuit"]').click()
    sleep(5)
    close_tab(driver.window_handles[1])