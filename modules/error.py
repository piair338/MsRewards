from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

class Banned(Exception):
    pass

class NotBanned(Exception):
    pass