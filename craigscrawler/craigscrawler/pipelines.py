# -*- coding: utf-8 -*-
import pickle
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from scrapy.exceptions import DropItem
import sys, traceback
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class CraigscrawlerPipeline(object):
    def process_item(self, item, spider):
        return item

class EmailNotificationPipeline(object):
    def __init__(self):
        self.sender = "ItsAMeCraig@crawl.org"
        self.receiver = "is2482@columbia.edu"

    def open_spider(self, spider):
        self.mail_sender = smtplib.SMTP('mx.columbia.edu')

    def close_spider(self, spider):
        self.mail_sender.quit()

    def process_item(self, item, spider):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'New item in craigslist'
        msg['From'] = self.sender
        msg['To'] = self.receiver

        divider = "-"*72
        try:
            text = "".join(
                [
                    "New item found in craigslist\n",
                    divider,
                    "\n",
                    divider,
                    "\n",
                    item['link'],
                    "\n",
                    item['title'][0],
                    "\n",
                    item['price'][0],
                    "\n",
                    "".join(item['description']),
                    "\n",
                    item['main_image'][0],
                    "\n",
                    divider,
                    "\n",
                    divider
                ]
            )
            html = """\
<html>
    <head></head>
    <body>
        <p>Hi, take a look at this:</p>
        <a href=%s>%s, %s</a>
        <img src=%s alt='missing image'></img>
        <p>%s</p>
    </body>
</html>
""" % (
        item['link'],
        item['title'][0],
        item['price'][0],
        item['main_image'][0],
        "".join(item['description'])
    )

        except:
            return item

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        self.mail_sender.sendmail(self.sender, self.receiver, msg.as_string())
        spider.log("send to %s:\n%s" % (self.receiver, msg.as_string()))
        return item

class DuplicatesPipeline(object):
    def __init__(self):
        self.db = "crawlset.db"

    def filter_by(self, item):
        return not ("58" in item['description'])

    def open_spider(self, spider):
        try:
            with open(self.db, "rb") as f:
                self.ids_seen = pickle.load(f)
        except IOError:
            self.ids_seen = set()

    def close_spider(self, spider):
        with open(self.db, "wb") as f:
            pickle.dump(self.ids_seen, f)

    def process_item(self, item, spider):
        if item['link'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" %item)
        if self.filter_by(item):
            raise DropItem("Filtered out. Does not contain 58: %s" %item)
        else:
            self.ids_seen.add(item['link'])
            return item
