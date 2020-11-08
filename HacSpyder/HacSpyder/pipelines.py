# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import motor.motor_asyncio  # async
from itemadapter import ItemAdapter


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
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    async def process_item(self, item, spider):
        print(item)
        self.db[item.doctype[0].upper() + item.doctype[1:] + "s"].find_one_and_update(
            {"doctype": item.doctype, "id": item.id},
            {"$set": ItemAdapter(item).asdict()},
            upsert=True,
        )

        return item
