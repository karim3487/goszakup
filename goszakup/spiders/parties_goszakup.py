import pdb
from pprint import pprint
from time import sleep


from goszakup import const as const

import scrapy


class PartiesGoszakupSpider(scrapy.Spider):
    name = "parties_goszakup"
    allowed_domains = ["zakupki.gov.kg"]
    start_urls = ["http://zakupki.gov.kg/popp/view/services/registry/suppliers.xhtml"]

    def parse(self, response):
        offset = 0
        pdb.set_trace()
        viewstate = response.xpath(
            "//input[@name='javax.faces.ViewState']/@value"
        ).get()
        form = const.PARTIES_FORM_DETAIL
        form["javax.faces.ViewState"] = viewstate

        while offset < 20:
            form[f"table:{offset}:j_idt86"] = f"table:{offset}:j_idt86"
            if f"table:{offset - 1}:j_idt86" in form:
                form.pop(f"table:{offset - 1}:j_idt86")
            pprint(form)
            yield scrapy.FormRequest(
                response.url,
                formdata=form,
                callback=self._process_party_page,
                cookies={"zakupki_locale": "ru"},
            )
            offset += 1
            sleep(2)

    def _process_party_page(self, response):
        party_name = response.xpath(const.PARTY_NAME).get()
        print("party_name:", party_name)

        party = {"party_name": party_name}

        yield party
