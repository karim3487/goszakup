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

    def drop_tables(self):
        self.cursor.execute("""DROP TABLE IF EXISTS goskakup_new_main;""")
        self.cursor.execute("""DROP TABLE IF EXISTS goszakup_new_tender_lots;""")
        self.conn.commit()

    def create_tables(self):
        self.cursor.execute(
            """
                create table if not exists goszakup.public.goskakup_new_main (
                    _link                              serial,
                    id                                 varchar(100),
                    tag                                varchar(50),
                    date                               timestamp,
                    ocid                               varchar(50),
                    initiationType                     varchar(50),
                    tender_id                          varchar(50),
                    tender_date                        timestamp,
                    tender_procurementSubMethodDetails varchar(50),
                    tender_mainProcurementCategory     varchar(50),
                    tender_title                       text,
                    tender_status                      varchar(50),
                    tender_procurementMethodDetails    varchar(50),
                    tender_tenderNumber                varchar(255),
                    tender_procurementMethod           varchar(255),
                    tender_datePublished               timestamp,
                    tender_tenderPeriod_startDate      timestamp,
                    tender_tenderPeriod_endDate        timestamp,
                    tender_enquiryPeriod_startDate     timestamp,
                    tender_enquiryPeriod_endDate       timestamp,
                    primary key (_link, id));
                """
        )

        # TODO: Update primary keys in tender_lots
        self.cursor.execute(
            """
            create table if not exists goszakup.public.goszakup_new_tender_lots (
                _link               varchar(255),
                _link_main          integer,
                id                  varchar(255),
                title               text,
                deliveryDateDetails varchar(100),
                status              varchar(50),
                lotNumber           varchar(20),
                deliveryTerms       varchar(10),
                deliveryAddress     text,
                value_amount        integer,
                value_currency      varchar(10),
                primary key (_link));
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

        self.drop_tables()
        self.create_tables()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        if isinstance(item, TenderItem):
            self.insert_tender(item)
        elif isinstance(item, LotItem):
            self.insert_lot(item)
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
        try:
            self.cursor.execute(sql, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print("Error occurred in main:", e)

    def insert_lot(self, item):
        main_link_query = f"""
            select _link
            from goskakup_new_main
            where id='{item['main_id']}';
        """
        self.cursor.execute(main_link_query)
        link_main = self.cursor.fetchone()[0]
        link = f"{link_main}.tender.lots.{item['lot_index']}"

        insert_query = """
            INSERT INTO goszakup_new_tender_lots (_link, _link_main, id, title, deliveryDateDetails, status, lotNumber, 
                                                  deliveryTerms, deliveryAddress, value_amount, value_currency)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        data = (
            link,
            link_main,
            item["id"],
            item["title"],
            item["deliveryDateDetails"],
            item["status"],
            item["lotNumber"],
            item["deliveryTerms"],
            item["deliveryAddress"],
            item["value_amount"],
            item["value_currency"],
        )

        try:
            self.cursor.execute(insert_query, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(item)
            print("Error occurred in lots:", e)
