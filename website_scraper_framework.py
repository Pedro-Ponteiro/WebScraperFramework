import os
from typing import Callable, Dict, List, Tuple

import chromedriver_autoinstaller
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class ListPage:
    def __init__(
        self,
        wd: webdriver.Chrome,
        url: str,
        listpage_setup_func: Callable[[webdriver.Chrome], None],
        listpage_xpaths_attributes: str,
        url_formatting: Callable[[str], str],
    ) -> None:
        self.wd = wd
        self.url = url
        self.xpaths_attributes = listpage_xpaths_attributes
        self.wd.get(self.url)
        self.url_formatting = lambda x: x
        if url_formatting:
            self.url_formatting = url_formatting
        if listpage_setup_func:
            listpage_setup_func(self.wd)

    def collect_displayed_urls(self, limit):
        collected_urls = []

        for xpath, attribute in self.xpaths_attributes:
            elements_found = self.wd.find_elements(By.XPATH, xpath)

            urls = [elem.get_attribute(attribute) for elem in elements_found]
            urls = [self.url_formatting(url) for url in urls if url is not None]

            collected_urls.extend(urls)
            collected_urls = list(set(collected_urls))

            if limit and limit <= len(collected_urls):
                collected_urls = collected_urls[:limit]
                break
        return collected_urls

    def fetch_until_limit(self, limit, fetch_function):
        previous_urls = self.collect_displayed_urls(limit)
        repeated_urls_count = 0

        while len(previous_urls) != limit:
            fetch_function(self.wd)
            current_urls = self.collect_displayed_urls(limit)

            if len(current_urls) == len(previous_urls):
                repeated_urls_count += 1

            previous_urls = current_urls

            if repeated_urls_count == 3:
                break
        return previous_urls

    def collect_urls(
        self, limit=False, fetch_function: Callable[[webdriver.Chrome], None] = None
    ) -> List[str]:
        if fetch_function is None:
            return self.collect_displayed_urls(limit)

        return self.fetch_until_limit(limit, fetch_function)


class DetailsPage:
    def __init__(
        self,
        wd: webdriver.Chrome,
        url: str,
        infoname_xpaths_attribute: List[Tuple[str, str, str]],
    ) -> None:
        self.wd = wd
        self.wd.get(url)
        self.url = url
        self.infonames_xpaths_attribute = infoname_xpaths_attribute

    def collect_infos(self) -> Dict[str, str]:
        out_data = {"url": self.url}

        for infoname, xpath, attribute in self.infonames_xpaths_attribute:
            try:
                result = self.wd.find_elements(By.XPATH, xpath)[0].get_attribute(
                    attribute
                )
            except Exception:
                result = ""

            out_data[infoname] = result

        return out_data


class Processor:
    def __init__(self) -> None:
        pass

    def get_all_data(self, wd: webdriver.Chrome, urls, infoname_xpaths_attribute):
        all_data = []

        for url in urls:
            details_page = DetailsPage(wd, url, infoname_xpaths_attribute)

            data = details_page.collect_infos()
            all_data.append(data)

        return all_data

    def save_data(self, all_data, base_url):
        df = pd.DataFrame(all_data)

        files_count = len(os.listdir("."))

        save_path = base_url.split("//")[1].split(".")[0] + str(files_count) + ".xlsx"

        df.to_excel(
            save_path,
            index=None,
        )

        return save_path

    def start_processing(
        self,
        base_url,
        listpage_xpaths_attributes,
        detailspage_xpaths_attributes,
        listpage_setup_func=None,
        limit=False,
        fetch_function=None,
        url_processing=None,
    ) -> str:
        chromedriver_autoinstaller.install()

        with webdriver.Chrome() as wd:
            urls = ListPage(
                wd,
                base_url,
                listpage_setup_func,
                listpage_xpaths_attributes,
                url_processing,
            ).collect_urls(limit=limit, fetch_function=fetch_function)

            all_data = self.get_all_data(
                wd,
                urls,
                detailspage_xpaths_attributes,
            )

        save_path = self.save_data(all_data, base_url)

        return save_path
