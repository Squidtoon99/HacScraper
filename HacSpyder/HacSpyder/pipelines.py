# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient

from itemadapter import ItemAdapter

import asyncio
import aiosmtplib
import sys

import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MAIL_PARAMS = {
    "TLS": settings.EMAIL_TLS,
    "host": settings.EMAIL_HOST,
    "password": settings.EMAIL_PASSWORD,
    "user": settings.EMAIL_USER,
    "port": settings.EMAIL_PORT,
}


class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "items"),
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    async def send_mail_async(sender, to, subject, text, textType="plain", **params):

        # Default Parameters
        cc = params.get("cc", [])
        bcc = params.get("bcc", [])
        mail_params = params.get("mail_params", MAIL_PARAMS)

        # Prepare Message
        msg = MIMEMultipart()
        msg.preamble = subject
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(to)
        if len(cc):
            msg["Cc"] = ", ".join(cc)
        if len(bcc):
            msg["Bcc"] = ", ".join(bcc)

        msg.attach(MIMEText(text, textType, "utf-8"))

        # Contact SMTP server and send Message
        host = mail_params.get("host", "localhost")
        isSSL = mail_params.get("SSL", False)
        isTLS = mail_params.get("TLS", False)
        port = mail_params.get("port", 465 if isSSL else 25)
        smtp = aiosmtplib.SMTP(hostname=host, port=port, use_tls=isSSL)
        await smtp.connect()
        if isTLS:
            await smtp.starttls()
        if "user" in mail_params:
            await smtp.login(mail_params["user"], mail_params["password"])
        await smtp.send_message(msg)
        await smtp.quit()

    async def process_item(self, item, spider):
        print(item)
        if item["doctype"] == "course":
            self.db.Courses.find_one_and_update(
                {"doctype": "course", "id": item["id"]},
                {"$set": ItemAdapter(item).asdict()},
                upsert=True,
            )
            return item

        user = self.db.Users.find_one({"doctype": "user", "_id": item["user_id"]})

        if not user.get("notifications"):
            self.db.Assignments.find_one_and_update({"doctype": "assignment"})
        else:

            old = await self.process_grades(
                user
            )  # getting the current grades as an int

            # inserting the doc into db
            self.db[
                item["doctype"][0].upper() + item["doctype"][1:] + "s"
            ].find_one_and_update(
                {"doctype": item["doctype"], "id": item["id"]},
                {"$set": ItemAdapter(item).asdict()},
                upsert=True,
            )

            current = await self.process_grades(user)  # updated grade count

            for system in user["notifications"]:
                pass

        return item
