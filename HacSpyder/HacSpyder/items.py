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
    teacher = Field()
    room = Field()
    marking_periods = Field()
    building = Field()
    status = Field()
    doctype = "course"


class Assignment(Item):
    course = Field()
    assignment = Field()
    category = Field()
    date_due = Field()
    score = Field()
    points = Field()
    weight = Field()
    extra_credit = Field()
    description = Field()
    class_average = Field()
    doctype = "assignment"
