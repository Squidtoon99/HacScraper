# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy import Item, Field


class Course(Item):  # /HomeAccess/Classes/Schedule
    id = Field()
    name = Field()
    teacher = Field()
    period = Field()
    room = Field()
    marking_periods = Field()
    building = Field()
    status = Field()
    user_id = Field()
    grade = Field()
    doctype = Field()


class Assignment(Item):
    course = Field()
    name = Field()
    category = Field()
    date_due = Field()
    days = Field()
    score = Field()
    points = Field()
    weight = Field()
    extra_credit = Field()
    description = Field()
    class_average = Field()
    user_id = Field()
    doctype = Field()
