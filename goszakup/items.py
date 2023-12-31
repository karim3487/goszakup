# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TenderItem(scrapy.Item):
    _link = scrapy.Field()  # 0, 1, 2...
    id = scrapy.Field()  # ocds-h7i0z4-10761964-2022-01-08T15:19:04.326+06:00
    tag = scrapy.Field()  # compiled
    date = scrapy.Field()  # 2022-01-08T15:19:04.326+06:00
    ocid = scrapy.Field()  # ocds-h7i0z4-10761964
    initiationType = scrapy.Field()  # tender
    tender_id = scrapy.Field()  # 10761964
    tender_date = scrapy.Field()  # 2016-04-13T14:23:46.243+06:00
    tender_procurementSubMethodDetails = (
        scrapy.Field()
    )  # {standard, twopackage, personific, centralised, framework, null}
    tender_mainProcurementCategory = (
        scrapy.Field()
    )  # {product, service, work, consultService}
    tender_title = scrapy.Field()
    tender_status = scrapy.Field()  # {complete, cancelled, active, unsuccessful}
    tender_procurementMethodDetails = (
        scrapy.Field()
    )  # {singleSource, simplicated, oneStage, egov, downgrade,
    # personific, consultSingleSource, twostage, consultQualityPrice,
    # consultPrice}
    tender_tenderNumber = scrapy.Field()
    tender_procurementMethod = scrapy.Field()  # {open, selective, direct, limited}
    tender_datePublished = scrapy.Field()
    tender_tenderPeriod_startDate = scrapy.Field()
    tender_tenderPeriod_endDate = scrapy.Field()
    tender_enquiryPeriod_startDate = scrapy.Field()
    tender_enquiryPeriod_endDate = scrapy.Field()


class LotItem(scrapy.Item):
    main_id = scrapy.Field()  # main id for select main and extract link
    lot_index = scrapy.Field()

    _link = scrapy.Field()  # 1.tender.lots.0
    _link_main = scrapy.Field()  # 1
    id = scrapy.Field()  # 18152463
    title = scrapy.Field()
    deliveryDateDetails = scrapy.Field()  # 30 дней
    status = scrapy.Field()  # {complete, cancelled, active, unsuccessful}
    lotNumber = scrapy.Field()  # L001-01
    deliveryTerms = scrapy.Field()  # {DDP, DAP, CIP, EXW, CPT, FOB, DAT, FCA, CIF, CFR}
    deliveryAddress = scrapy.Field()
    value_amount = scrapy.Field()  # 10000
    value_currency = scrapy.Field()  # KGS


class ItemItem(scrapy.Item):
    main_id = scrapy.Field()  # main id for select main and extract link
    item_index = scrapy.Field()
    lot_index = scrapy.Field()

    _link = scrapy.Field()
    _link_main = scrapy.Field()
    id = scrapy.Field()
    relatedLot = scrapy.Field()
    quantity = scrapy.Field()
    unit_id = scrapy.Field()
    unit_name = scrapy.Field()
    unit_value_empty = scrapy.Field()
    unit_value_amount = scrapy.Field()
    unit_value_currency = scrapy.Field()
    classification_id = scrapy.Field()
    classification_scheme = scrapy.Field()
    classification_description = scrapy.Field()


class BidDetailItem(scrapy.Item):
    main_id = scrapy.Field()  # main id for select main and extract link
    bid_id = scrapy.Field()

    _link = scrapy.Field()
    _link_main = scrapy.Field()
    id = scrapy.Field()
    date = scrapy.Field()
    status = scrapy.Field()


class BidDetailProposal(scrapy.Item):
    main_id = scrapy.Field()  # main id for select main and extract link
    bid_id = scrapy.Field()
    proposal_id = scrapy.Field()
    lot_number = scrapy.Field()

    _link = scrapy.Field()
    _link_bids_details = scrapy.Field()
    _link_main = scrapy.Field()
    id = scrapy.Field()
    relatedItem = scrapy.Field()
    relatedLot = scrapy.Field()
    unit_value_amount = scrapy.Field()
    unit_value_currency = scrapy.Field()


class BidDetailTenderers(scrapy.Item):
    main_id = scrapy.Field()  # main id for select main and extract link
    bid_id = scrapy.Field()

    _link = scrapy.Field()
    _link_bids_details = scrapy.Field()
    _link_main = scrapy.Field()
    id = scrapy.Field()


class BidDetailRelatedLots(scrapy.Item):
    main_id = scrapy.Field()  # main id for select main and extract link
    bid_id = scrapy.Field()

    _link = scrapy.Field()
    _link_bids_details = scrapy.Field()
    _link_main = scrapy.Field()
    id = scrapy.Field()
    value_amount = scrapy.Field()
    value_currency = scrapy.Field()
    value_initialAmount = scrapy.Field()
