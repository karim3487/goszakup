import re
from time import sleep

import scrapy
from lxml import html

from goszakup import const
from goszakup import helper
from goszakup import items


class MainGoszakupSpider(scrapy.Spider):
    name = "main_goszakup"
    start_urls = ["http://zakupki.gov.kg/popp/view/order/list.xhtml"]

    def parse(self, response):
        # Extract j_ids for "LINKS_FORM"
        j_ids = response.css('div[id^="j_idt"][class^="ui-tooltip"]').attrib["id"]
        numbers = re.findall(r"\d+", j_ids)
        j_id1, j_id2 = numbers[0], numbers[1]

        # Update j_ids in const.py
        helper.update_variable("const.py", "J_ID1", j_id1)
        helper.update_variable("const.py", "J_ID2", j_id2)

        viewstate = helper.get_viewstate(html.fromstring(response.body))
        form = const.LINKS_FORM
        form["javax.faces.ViewState"] = viewstate

        for offset in range(2000, 2010, const.ROWS_NUMBER):
            form[const.LINKS_OFFSET_KEY] = str(offset)
            yield scrapy.FormRequest(
                response.url,
                formdata=form,
                callback=self._fetch_links,
                cookies={"zakupki_locale": "ru"},
            )
            sleep(2)

    def _fetch_links(self, response):
        response_post_html = html.fromstring(response.body)

        for tender in helper.fetch_tenders(response_post_html):
            url = const.TENDER_LINK + tender["tender_id"]
            yield tender
            yield scrapy.Request(
                url,
                callback=self._process_tender_page,
                cb_kwargs={"main_id": tender["id"]},
                cookies={"zakupki_locale": "ru"},
            )

    def _process_tender_page(self, response, main_id):
        response_html = html.fromstring(response.body)
        tender_type = helper.determine_tender_type(response_html)

        # Extract j_idts for "SERVICE_LOTS_FORM" and "PRODUCT_LOTS_FORM"
        j_idt1 = response.css('input[name^="j_idt"][value^="j_idt"]')[-1]
        j_idt1 = int(re.findall(r"\d+", j_idt1.attrib["value"])[0])
        j_idt2 = response.css('div[id^="j_idt"][class^="ui-tabs"]')
        j_idt2 = int(re.findall(r"\d+", j_idt2.attrib["id"])[0])

        # Update j_ids in const.py
        helper.update_variable("const.py", "J_IDT1_BIDS", j_idt1)
        helper.update_variable("const.py", "J_IDT2_BIDS", j_idt2)

        detail_lot_form = (
            const.PRODUCT_LOTS_FORM
            if tender_type == "products"
            else const.SERVICE_LOTS_FORM
        )
        row_expansion_key = (
            f"j_idt{const.J_IDT2_BIDS}:lotsTable_expandedRowIndex"
            if tender_type == "products"
            else f"j_idt{const.J_IDT2_BIDS}:lotsTable2_expandedRowIndex"
        )

        bids_form = const.BIDS_FORM

        viewstate = helper.get_viewstate(response_html)
        detail_lot_form[const.VIEWSTATE_KEY] = bids_form[
            const.VIEWSTATE_KEY
        ] = viewstate

        self.cid = int(
            response.css('form[id^="j_idt"]')[0].attrib["action"].split("=")[-1]
        )

        for i in range(helper.count_lots(response_html)):
            yield from helper.fetch_lots(response_html, i, tender_type, main_id)
            detail_lot_form[row_expansion_key] = str(i)
            yield scrapy.FormRequest(
                const.VIEW_URL + f"?cid={self.cid}",
                formdata=detail_lot_form,
                callback=self._process_lot_page,
                cb_kwargs={
                    "lot_index": i,
                    "main_id": main_id,
                    "response_html": response_html,
                },
                cookies={"zakupki_locale": "ru"},
            )

        if "Протокол" in response.text:
            yield scrapy.FormRequest(
                const.VIEW_URL + f"?cid={self.cid}",
                formdata=bids_form,
                callback=self._process_bids_page,
                cb_kwargs={"main_id": main_id},
                cookies={"zakupki_locale": "ru"},
            )

    def _process_bids_page(self, response, main_id):
        bids_page_html = html.fromstring(response.body)
        row_elements = bids_page_html.xpath("//tbody[@id='submissions_data']/tr")
        number_of_rows = len(row_elements)

        if (
            number_of_rows == 1
            and row_elements[0].xpath("normalize-space(.)")
            == "Не найдено ни одной записи."
        ):
            yield None
        else:
            yield from helper.process_proposal_page(
                response, main_id, self._process_tenderers_page
            )

    def _process_tenderers_page(self, response, main_id, bid_id):
        inn = response.css(".contentC::text")[0].get()
        bid_detail_tenderers = items.BidDetailTenderers(
            main_id=main_id, bid_id=bid_id, id=f"KG-INN-{inn}"
        )
        yield bid_detail_tenderers

    def _process_lot_page(self, response, lot_index, main_id, response_html):
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

        for i, product_name in enumerate(product_names):
            item = items.ItemItem(
                main_id=main_id,
                lot_index=lot_index,
                item_index=i,
                quantity=helper.to_int(helper.clear_field(quantities[i])),
                unit_id=1,
                unit_name=helper.clear_field(unit_names[i]),
                unit_value_empty=False,
                unit_value_amount=helper.to_int(
                    helper.lot_gen_info(response_html, lot_index + 1, 3)
                ),
                unit_value_currency="KGS",
                classification_id=helper.clear_field(product_codes[i]),
                classification_scheme="OKGZ",
                classification_description=helper.clear_field(product_name),
            )

            yield item
