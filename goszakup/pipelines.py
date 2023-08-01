# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pdb
from datetime import datetime

import psycopg2

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from goszakup.items import TenderItem, LotItem


class GoszakupPipeline:
    def __init__(self, db_settings):
        self.db_settings = db_settings

    def create_tables(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS goszakup.public.goskakup_new_main (
                                    _link                              serial primary key,
                                    id                                 text,
                                    tag                                text,
                                    date                               timestamp,
                                    ocid                               text,
                                    initiationType                     text,
                                    tender_id                          text,
                                    tender_date                        timestamp,
                                    tender_procurementSubMethodDetails text,
                                    tender_mainProcurementCategory     text,
                                    tender_title                       text,
                                    tender_status                      text,
                                    tender_procurementMethodDetails    text,
                                    tender_tenderNumber                text,
                                    tender_procurementMethod           text,
                                    tender_datePublished               timestamp,
                                    tender_tenderPeriod_startDate      timestamp,
                                    tender_tenderPeriod_endDate        timestamp,
                                    tender_enquiryPeriod_startDate     timestamp,
                                    tender_enquiryPeriod_endDate       timestamp);
                                    """
        )
        self.conn.commit()

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("POSTGRESQL_SETTINGS")
        return cls(db_settings)

    def open_spider(self, spider):
        self.conn = psycopg2.connect(**self.db_settings)
        self.cursor = self.conn.cursor()

        self.create_tables()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        if isinstance(item, TenderItem):
            self.insert_tender(item)
        elif isinstance(item, LotItem):
            pass
        self.conn.commit()
        return item

    def insert_tender(self, item):
        sql = """
                INSERT INTO goszakup.public.goskakup_new_main (id, tag, date, ocid, initiationType, tender_id, 
                                    tender_date, tender_procurementSubMethodDetails, tender_mainProcurementCategory,
                                    tender_title, tender_status, tender_procurementMethodDetails,
                                    tender_tenderNumber, tender_procurementMethod, tender_datePublished,
                                    tender_tenderPeriod_startDate, tender_tenderPeriod_endDate,
                                    tender_enquiryPeriod_startDate, tender_enquiryPeriod_endDate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        data = (
            item["id"],
            item["tag"],
            item["date"],
            item["ocid"],
            item["initiationType"],
            item["tender_id"],
            item["tender_date"],
            item["tender_procurementSubMethodDetails"],
            item["tender_mainProcurementCategory"],
            item["tender_title"],
            item["tender_status"],
            item["tender_procurementMethodDetails"],
            item["tender_tenderNumber"],
            item["tender_procurementMethod"],
            item["tender_datePublished"],
            item["tender_tenderPeriod_startDate"],
            item["tender_tenderPeriod_endDate"],
            item["tender_enquiryPeriod_startDate"],
            item["tender_enquiryPeriod_endDate"],
        )
        # self.conn.rollback()
        self.cursor.execute(sql, data)
        self.conn.commit()
