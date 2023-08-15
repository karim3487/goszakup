import datetime
import re
from pprint import pprint
from time import sleep

import scrapy
from lxml import html
from goszakup import const
from goszakup import helper
import ipdb

from goszakup.items import LotItem, ItemItem


class MainGoszakupSpider(scrapy.Spider):
    name = "main_goszakup"
    # allowed_domains = ["zakupki.gov.kg"]
    start_urls = ["http://zakupki.gov.kg/popp/view/order/list.xhtml"]

    def parse(self, response):
        offset = 0

        # extract j_ids for "LINKS_FORM"
        j_ids = response.css('div[id^="j_idt"][class^="ui-tooltip"]').attrib["id"]
        numbers = re.findall(r"\d+", j_ids)
        j_id1, j_id2 = numbers[0], numbers[1]

        # update j_ids in const.py
        helper.update_variable("const.py", "J_ID1", j_id1)
        helper.update_variable("const.py", "J_ID2", j_id2)

        viewstate = response.xpath(
            "//input[@name='javax.faces.ViewState']/@value"
        ).get()
        form = const.LINKS_FORM
        form["javax.faces.ViewState"] = viewstate

        while offset < 20:
            form[const.LINKS_OFFSET_KEY] = str(offset)
            pprint(form)
            yield scrapy.FormRequest(
                response.url,
                formdata=form,
                callback=self._fetch_links,
                cookies={"zakupki_locale": "ru"},
            )
            offset += const.ROWS_NUMBER
            sleep(2)

    def _fetch_links(self, response):
        response_post_html = html.fromstring(response.body)

        for tender in helper.fetch_tenders(response_post_html):
            url = const.TENDER_LINK + tender["tender_id"]
            yield tender
            yield scrapy.Request(
                url,
                callback=self._process_tender_page,
                cb_kwargs=dict(main_id=tender["id"]),
                cookies={"zakupki_locale": "ru"},
            )

    def _process_tender_page(self, response, main_id):
        response_html = html.fromstring(response.body)
        tender_type = helper.determine_tender_type(response_html)

        if tender_type == "products":
            form = const.PRODUCT_LOTS_FORM
            row_expansion_key = "j_idt78:lotsTable_expandedRowIndex"
        else:
            form = const.SERVICE_LOTS_FORM
            row_expansion_key = "j_idt78:lotsTable2_expandedRowIndex"

        form[const.VIEWSTATE_KEY] = helper.get_viewstate(response_html)

        for i in range(helper.count_lots(response_html)):
            for lot_item in helper.fetch_lots(response_html, i, tender_type, main_id):
                yield lot_item

            # TODO: fix scrapy tender_items
            # form[row_expansion_key] = str(i)
            # print("u:", response.url)
            # yield scrapy.FormRequest(
            #     const.VIEW_URL + f"?cid=6",
            #     formdata=form,
            #     callback=self._process_lot_page,
            #     cb_kwargs={"lot_index": i, "main_id": main_id},
            #     cookies={"zakupki_locale": "ru"},
            # )

    def _process_lot_page(self, response, lot_index, main_id):
        lot_page_html = html.fromstring(response.body)
        product_names_and_codes = lot_page_html.xpath(
            "//table[@class='display-table private-room-table no-borders f-right']/tbody/tr/td[1]/text()"
        )

        product_names = []
        product_codes = []

        for item in product_names_and_codes:
            code, name = item.split(" : ")
            product_names.append(name)
            product_codes.append(code)

        unit_names = lot_page_html.xpath(
            "//table[@class='display-table private-room-table no-borders f-right']/tbody/tr/td[2]/text()"
        )
        quantities = lot_page_html.xpath(
            "//table[@class='display-table private-room-table no-borders f-right']/tbody/tr/td[3]/text()"
        )
        assert (
            len(product_names)
            == len(product_codes)
            == len(unit_names)
            == len(quantities)
        )

        for i in range(len(product_names)):
            item = ItemItem()
            item["main_id"] = main_id

            item["lot_index"] = lot_index
            item["item_index"] = i
            item["quantity"] = helper.clear_field(quantities[i])
            item["unit_id"] = 1
            item["unit_name"] = helper.clear_field(unit_names[i])
            item["unit_value_empty"] = False
            item["unit_value_amount"] = helper.to_int(
                helper.lot_gen_info(response, lot_index + 1, 3)
            )
            item["unit_value_currency"] = "KGS"
            item["classification_id"] = helper.clear_field(product_codes[i])
            item["classification_scheme"] = "OKGZ"
            item["classification_description"] = helper.clear_field(product_names[i])

            yield item
