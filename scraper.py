import logging
from datetime import datetime
from pathlib import Path
from random import randint
from time import sleep

import click
import pandas as pd
import requests
import selenium.webdriver.support.ui as ui
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from user_agents import user_agent_list


APP_DIR = Path(__file__).parent
log = logging.getLogger()


def primary_extract(page, locale, city, radius, must_contain):
    assert isinstance(locale, str)

    url = f"https://{locale}.indeed.com/jobs?q=python+developer&l={city}&start={page}&radius={radius}&as_any={must_contain}"
    headers = user_agent_list[randint(0, len(user_agent_list) - 1)]
    r = requests.get(url, headers)
    soup = BeautifulSoup(r.content, "html.parser")

    return soup


def secondary_extract(url, joblist):
    headers = user_agent_list[randint(0, len(user_agent_list) - 1)]
    r = requests.get(url, headers)
    soup = BeautifulSoup(r.content, "html.parser")
    job = secondary_process(soup)
    job["apply_url"] = url

    if job not in joblist:
        joblist.append(job)


def secondary_process(soup):
    title = soup.find(
        "h1",
        {"class": "icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title"},
    ).text.strip()
    company = soup.find(
        "div", {"class": "icl-u-lg-mr--sm icl-u-xs-mr--xs"}
    ).text.strip()
    try:
        salary = soup.find("span", {"class": "icl-u-xs-mr--xs"}).text.strip()
    except:
        salary = ""
    summary = soup.find("div", {"class": "jobsearch-jobDescriptionText"}).text

    job = {
        "title": title,
        "company": company,
        "salary": salary,
        "summary": summary,
    }

    return job


def primary_process(soup, joblist, locale):
    html = soup.prettify("utf-8")
    html_content = soup.prettify("utf-8").decode("utf-8")
    substring = '"link":"/company/'

    result = [s for s in html_content.split(",") if substring in s]

    job_links = []
    for el in result:
        modified = f"https://{locale}.indeed.com" + el[8:-1]
        if modified not in job_links:
            job_links.append(modified)
            log.info(f"job link added: {modified}")
            secondary_extract(modified, joblist)


def open_urls(urls):
    options = webdriver.ChromeOptions()
    options.binary_location = "ENTER CHROME BINARY PATH HERE"
    chrome_driver_binary = "ENTER CHROMEDRIVER BINARY PATH HERE"

    browser = webdriver.Chrome(chrome_driver_binary, chrome_options=options)

    for url in urls:
        browser.execute_script("""window.open("about:blank", "_blank");""")
        browser.switch_to.window(browser.window_handles[-1])
        browser.get(url)
        sleep(1.2)

        try:
            element = browser.find_element_by_xpath(
                '//*[@id="applyButtonLinkContainer"]/div/div[2]/a'
            )
        except Exception as e:
            element = browser.find_element_by_css_selector("#indeedApplyButton")

        ActionChains(browser).key_down(Keys.CONTROL).click(element).key_up(
            Keys.CONTROL
        ).perform()

        browser.switch_to.window(browser.window_handles[-2])

        element = browser.find_element_by_tag_name("body")
        element.send_keys(Keys.CONTROL + "w")


@click.command()
@click.option(
    "--locale",
    default="nl",
    help="this will be put in the url to search on the specific national indeed site",
)
@click.option("--count", default=50, help="number of job ads to process")
@click.option("--city", default="Amsterdam", help="i have no idea what this is")
@click.option("--radius", default=25)
@click.option("--must-contain", default="")
def main(locale: str, count: int, city: str, radius: int, must_contain: str):
    joblist = []

    for i in range(0, count, 10):
        print(f"Parsing: {i}")
        c = primary_extract(i, locale, city, radius, must_contain)
        primary_process(c, joblist, locale)

    df = pd.DataFrame(joblist)
    links = df.loc[:, "apply_url"].values.tolist()

    proper_links = []
    for link in links:
        if link != "" and "https://" in link:
            proper_links.append(link)

    df.to_csv(f"job_offers_{city}_{radius}_miles_{must_contain}.csv")
    # open_urls(proper_links)


if __name__ == "__main__":
    handler = logging.FileHandler(APP_DIR / "scraper.log")
    formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    main()
