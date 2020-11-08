from scrapy import Spider, Request, Item, Field, FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin
from datetime import datetime
import logging
from traceback import print_exc
from ..items import Course, Assignment
from .. import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapy_selenium import SeleniumRequest
import asyncio


class HacSpydermainSpider(Spider):
    name = "HacSpyderMain"
    allowed_domains = ["*"]
    start_urls = []

    def start_requests(self):
        for user in settings.db.Users.find({"doctype": "user"}):
            url = user["url"].replace("https://", "")
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
                "Upgrade-Insecure-Requests": "1",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Host": url,
                "Origin": url,
                "Referrer": f"https://{url.replace('https://','').replace('http://','')}/HomeAccess/Account/LogOn?ReturnUrl=%2fHomeAccess%2f",
            }
            yield SeleniumRequest(
                url=f"{user['url']}/HomeAccess/Account/LogOn?ReturnUrl=%2fHomeAccess",
                headers=headers,
                callback=self.parse,
                wait_until=EC.presence_of_element_located(
                    (By.XPATH, "//input [@name='__RequestVerificationToken']")
                ),
                wait_time=60,
                dont_filter=True,
                meta={"cookiejar": user["_id"], "user": user},
            )

    async def parse(self, response):
        data = response.meta["user"]
        driver = response.meta["driver"]
        base = [
            "__RequestVerificationToken",
            "SCKTY00328510CustomEnabled",
            "SCKTY00436568CustomEnabled",
            "Database",
            "VerificationOption",
            "tempUN",
            "tempPW",
        ]

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
            "Upgrade-Insecure-Requests": "1",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Host": data["url"],
            "Origin": data["url"],
            "Referrer": f"https://{data['url'].replace('https://','').replace('http://','')}/HomeAccess/Account/LogOn?ReturnUrl=%2fHomeAccess%2f",
        }

        driver.find_element_by_id("LogOnDetails_UserName").send_keys(data["username"])
        driver.find_element_by_id("LogOnDetails_Password").send_keys(data["password"])
        driver.find_element_by_xpath("//button [@id='login']").click()
        yield SeleniumRequest(
                url=f"{data['url']}/HomeAccess/",
                headers=headers,
                callback=self.handle_auth_user,
                wait_time=10,
                dont_filter=True,
                meta={"cookiejar": data["_id"], "user": data},
            )

    async def handle_auth_user(self, response):
        user = response.meta["user"]

        if user.get("classes", None) == None:
            yield SeleniumRequest(
                url=user["url"] + "/HomeAccess/Classes/Schedule",
                callback=self.parse_courses,
                dont_filter=True,
                meta={"cookiejar": response.meta["cookiejar"], "user": user},
            )
        yield SeleniumRequest(
            url=user["url"] + "/HomeAccess/Classes/Classwork/Assignments.aspx",
            callback=self.parse_assignments,
            dont_filter=True,
            meta={"cookiejar": response.meta["cookiejar"], "user": user},
        )

    async def parse_assignments(self, response):
        user = response.meta["user"]
        data = lambda course, num: course.xpath(f"td[{num}]//text()").extract_first()
        first = True
        for good_counting, course in enumerate(
            response.xpath('//div [@class="AssignmentClass"]')
        ):

            messy_course_name = response.xpath(
                f"//a [@class='sg-header-heading'])[{good_counting}]"
            ).get()

            course_split = messy_course_name.split()
            course_name = " ".join(course[3:])
            course_id = " ".join(course[:3])
            first = True
            for assignment in course.xpath(""):
                if first:
                    first = not first
                    continue  # skipping first iteration for useless data

                item = Assignment()
                item.date_due = datetime.strptime("%m/%d/%Y", data(assignment, 0))
                # item.date_created = datetime.strptime("%m/%d/%Y", data(assignment, 1))
                item.assignment = data(assignment, 2)
                item.category = data(assignment, 3)
                item.score = data(assignment, 4)
                item.class_average = data(assignment, 9)
                item.course = {"name": course_name, "id": course_id}
                yield item

    async def parse_courses(self, response):
        user = response.meta["user"]
        data = lambda course, num: course.xpath(f"td[{num}]//text()").extract_first()
        first = True
        for c in response.xpath('//table [@class="sg-asp-table"]//tbody//tr'):
            if first:
                first = not first
                continue  # skipping first iteration but scrapy xpath

            item = Course()

            item.id = data(c, 1)
            item.name = data(c, 2)
            item.period = data(c, 3)
            item.teacher = data(c, 4)
            item.room = data(c, 5)
            item.days = data(c, 6)
            item.marking_periods = data(c, 7)
            item.building = data(c, 8)
            item.status = data(c, 9)
            item.user = user["_id"]
            yield item