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
        self.items_to_mail = []

    def close_spider(self, spider):
        if len(self.items_to_mail) > 0:
            mail_sender = smtplib.SMTP('mx.columbia.edu')
            msg = self.create_mail(spider.log)
            mail_sender.sendmail(self.sender, self.receiver, msg.as_string())
            spider.log("send to %s:\n%s" % (self.receiver, msg.as_string()))
            mail_sender.quit()

    def process_item(self, item, spider):
        self.items_to_mail.append(item)
        return item

    def create_mail(self, log):
        def pop_with_default(l,default):
            try:
                return l.pop()
            except:
                return default
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'New items in craigslist'
        msg['From'] = self.sender
        msg['To'] = self.receiver

        divider = ("-"*160 + "\n")*2
        text = "New items found in craigslist\n" + divider
        divider_html = ("-"*160 + "<br>")*2
        html =  (
            "<html>\n" +
            "\t<head></head>\n" +
            "\t<body>\n" +
            "\t\t<p>Hi, take a look at this:</p>\n" +
            divider_html
        )
        for item in self.items_to_mail:
            link = item['link']
            title = pop_with_default(item['title'],"N/A")
            price = pop_with_default(item['price'],"N/A")
            main_image = pop_with_default(item['main_image'],"")

            try:
                text += (
                    link + "\n" +
                    title + "\n" +
                    price + "\n" +
                    "".join(item['description']) + "\n" +
                    main_image + "\n" +
                    divider
                )
                html += (
                    "<div style='max-width:53em'>" + 
                    "<a href=%s>%s, %s</a><br>" +
                    "<img src=%s alt='missing image'></img><br>" +
                    "<p>%s</p><br>" + 
                    "</div>"
                ) % (
                    link,
                    title,
                    price,
                    main_image,
                    "<br>".join(item['description'])
                )
                html += divider_html
            except Exception as e:
                log("Malformed item: %s" % item)
                log(e)
                log(traceback.format_tb(sys.exc_traceback))
                continue

        html += "</body>\n</html>"
        part1 = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
        part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)
        return msg

class DuplicatesPipeline(object):
    def __init__(self):
        self.db = "crawlset.db"

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
        else:
            self.ids_seen.add(item['link'])
            return item

class FilterPipeline(object):
    def __init__(self):
        self.filters = [
            lambda item: re.search(
                r"58cm|58 cm|size.\s*58",
                "".join(item['description']),
                flags=re.IGNORECASE
            )
        ]

    def filter_by(self, item):
        for filter_function in self.filters:
            if not filter_function(item):
                return True
        return False

    def process_item(self, item, spider):
        if self.filter_by(item):
            raise DropItem("Filtered out: %s" %item)
        else:
            return item

class CountFullyProcessedItemsPipeline(object):
    def __init__(self):
        pass
    
    def open_spider(self, spider):
        self.count = 0

    def close_spider(self, spider):
        spider.log("User was notified for %d new items" % self.count)
    
    def process_item(self, item, spider):
        self.count += 1
        return item
