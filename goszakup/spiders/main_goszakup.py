import re
from pprint import pprint
from time import sleep

import scrapy
from lxml import html
from goszakup import const
from goszakup import helper
import pdb



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
            yield tender


