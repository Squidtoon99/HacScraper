import os
from scrapy.cmdline import execute
import asyncio

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
os.chdir(os.path.dirname(os.path.realpath(__file__)))

try:
    execute(
        [
            "scrapy",
            "crawl",
            "HacSpyderMain",
        ]
    )
except SystemExit:
    pass