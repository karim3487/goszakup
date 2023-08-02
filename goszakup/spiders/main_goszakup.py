import datetime
import re
from pprint import pprint
from time import sleep

import scrapy
from lxml import html
from goszakup import const
from goszakup import helper
import pdb

from goszakup.items import LotItem


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

        row_expansion_key = ""

        if tender_type == "products":
            form = const.PRODUCT_LOTS_FORM
        else:
            form = const.SERVICE_LOTS_FORM

        form[const.VIEWSTATE_KEY] = helper.get_viewstate(response_html)

        for i in range(helper.count_lots(response_html)):
            form[row_expansion_key] = str(i)

            for lot_item in helper.fetch_lots(response_html, i, tender_type, main_id):
                yield lot_item
