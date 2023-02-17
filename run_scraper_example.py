import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from website_scraper_framework import Processor


def main():
    def fetch_function(wd: webdriver.Chrome):
        wd.find_element(By.XPATH, "//body").send_keys(Keys.END)
        time.sleep(3)

    def listpage_setup_function(wd: webdriver.Chrome):
        time.sleep(1)
        try:
            wd.find_element(By.XPATH, "//body").send_keys(Keys.END)
            time.sleep(1)
            wd.find_element(By.XPATH, "//body").send_keys(Keys.END)
        except Exception:
            ...
        time.sleep(1)

    def url_processing(url_part: str):
        if url_part.startswith("https"):
            return url_part

        return "https://exemplo.com" + url_part

    Processor().start_processing(
        base_url="https://exemplo.com",
        listpage_xpaths_attributes=[
            ("//div[contains(@class,'ola')]", "data-src"),
            ("//a[contains(@href,'/teste/')]", "href"),
        ],
        detailspage_xpaths_attributes=[
            (
                "WhatsApp",
                "//div[@id='example']",
                "data-telefono",
            ),
            (
                "price",
                "//section[contains(@class, 'example')]//td[2]",
                "textContent",
            ),
        ],
        fetch_function=fetch_function,
        listpage_setup_func=listpage_setup_function,
        url_processing=url_processing,
        # limit=10,
    )


if __name__ == "__main__":
    main()
