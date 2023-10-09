# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime

import psycopg2

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from goszakup import items


class GoszakupPipeline:
    def __init__(self, db_settings):
        self.db_settings = db_settings

    def drop_tables(self):
        self.cursor.execute("""DROP TABLE IF EXISTS goskakup_new_main;""")
        self.cursor.execute("""DROP TABLE IF EXISTS goszakup_new_tender_lots;""")
        self.cursor.execute("""DROP TABLE IF EXISTS goszakup_new_tender_items;""")
        self.cursor.execute("""DROP TABLE IF EXISTS goszakup_new_bids_details;""")
        self.cursor.execute(
            """DROP TABLE IF EXISTS goszakup_new_bids_detailsproposal;"""
        )
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

        self.cursor.execute(
            """
            create table if not exists goszakup.public.goszakup_new_tender_lots (
            _link               varchar(255),
            _link_main          integer,
            id                  serial,
            title               text,
            deliveryDateDetails varchar(255),
            status              varchar(50),
            lotNumber           varchar(20),
            deliveryTerms       varchar(10),
            deliveryAddress     text,
            value_amount        integer,
            value_currency      varchar(10),
            primary key (_link, id));
            """
        )
        self.cursor.execute(
            """
            create table if not exists goszakup.public.goszakup_new_tender_items(
            _link                      varchar(255),
            _link_main                 integer,
            id                         serial,
            relatedLot                 integer,
            quantity                   integer,
            unit_id                    integer,
            unit_name                  varchar(100),
            unit_value_empty           boolean,
            unit_value_amount          integer,
            unit_value_currency        varchar(10),
            classification_id          varchar(20),
            classification_scheme      varchar(10),
            classification_description varchar(100),
            primary key (_link, id));
            """
        )

        self.cursor.execute(
            """
            create table if not exists goszakup.public.goszakup_new_bids_details(
            _link      varchar(255),
            _link_main integer,
            id         serial,
            date       timestamp,
            status     varchar(20),
            primary key (_link, id));
            """
        )
        self.cursor.execute(
            """
            create table if not exists goszakup.public.goszakup_new_bids_detailsProposal(
            _link               varchar(255),
            _link_bids_details  varchar(255),
            _link_main          integer,
            id                  serial,
            relatedItem         integer,
            relatedLot          integer,
            unit_value_amount   integer,
            unit_value_currency varchar(10),
            primary key (_link, id));
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
        match item:
            case items.TenderItem():
                self.insert_tender(item)
            case items.LotItem():
                self.insert_lot(item)
            case items.ItemItem():
                self.insert_item(item)
            case items.BidDetailItem():
                self.insert_bid_detail(item)
            case items.BidDetailProposal():
                self.insert_bid_detail_proposal(item)
        return item

    def insert_tender(self, item):
        try:
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
            self.cursor.execute(sql, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print("Error occurred in main:", e)

    def insert_lot(self, item):
        link_main = self.get_main_id(item)
        try:
            link = f"{link_main}.tender.lots.{item['lot_index'] + 1}"

            insert_query = """
                INSERT INTO goszakup_new_tender_lots (_link, _link_main, title, deliveryDateDetails, status, lotNumber, 
                                                      deliveryTerms, deliveryAddress, value_amount, value_currency)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            data = (
                link,
                link_main,
                item["title"],
                item["deliveryDateDetails"],
                item["status"],
                item["lotNumber"],
                item["deliveryTerms"],
                item["deliveryAddress"],
                item["value_amount"],
                item["value_currency"],
            )

            self.cursor.execute(insert_query, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(item)
            print("Error occurred in lots:", e)

    def insert_item(self, item):
        link_main = self.get_main_id(item)
        try:
            link = f"{link_main}.tender.items.{item['lot_index'] + 1}"

            lot_item_query = f"select id from goszakup_new_tender_lots where _link='{link_main}.tender.lots.{item['lot_index'] + 1}'"
            self.cursor.execute(lot_item_query)
            related_lot = self.cursor.fetchone()[0]

            insert_query = """
                INSERT INTO goszakup_new_tender_items (_link, _link_main, relatedLot, quantity, unit_id, unit_name, 
                                    unit_value_empty,unit_value_amount, unit_value_currency, classification_id,
                                    classification_scheme, classification_description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            data = (
                link,
                link_main,
                related_lot,
                item["quantity"],
                item["unit_id"],
                item["unit_name"],
                item["unit_value_empty"],
                item["unit_value_amount"],
                item["unit_value_currency"],
                item["classification_id"],
                item["classification_scheme"],
                item["classification_description"],
            )

            self.cursor.execute(insert_query, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(item)
            print("Error occurred in items:", e)

    def insert_bid_detail(self, item):
        link_main = self.get_main_id(item)
        try:
            link = f"{link_main}.bids.details.{item['bid_id']}"

            insert_query = """
                INSERT INTO goszakup_new_bids_details (_link, _link_main, date, status)
                VALUES (%s, %s, %s, %s);
            """

            data = (link, link_main, item["date"], item["status"])

            self.cursor.execute(insert_query, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(item)
            print("Error occurred in bids_details:", e)

    def insert_bid_detail_proposal(self, item):
        link_main = self.get_main_id(item)
        try:
            link_bids_details = f"{link_main}.bids.details.{item['bid_id']}"
            link = link_bids_details + f".priceProposal.{item['proposal_id']}"
            related_lot_query = f"""
            SELECT id FROM goszakup_new_tender_lots
            WHERE _link_main={link_main} AND lotnumber='{item['lot_number']}'
            """
            self.cursor.execute(related_lot_query)
            related_lot = self.cursor.fetchone()[0]

            insert_query = """
                INSERT INTO goszakup_new_bids_detailsProposal (_link, _link_bids_details, _link_main, relatedItem,
                 relatedLot, unit_value_amount, unit_value_currency)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """

            data = (
                link,
                link_bids_details,
                link_main,
                1,
                related_lot,
                item["unit_value_amount"],
                item["unit_value_currency"],
            )

            self.cursor.execute(insert_query, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(item)
            print("Error occurred in bids_details_proposal:", e)

    def get_main_id(self, item):
        main_link_query = f"""
                        select _link
                        from goskakup_new_main
                        where id='{item['main_id']}';
                    """
        self.cursor.execute(main_link_query)
        return self.cursor.fetchone()[0]
