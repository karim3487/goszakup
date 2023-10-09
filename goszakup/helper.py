import datetime
import os
import unicodedata
import re

from goszakup import const as const, items

from goszakup.items import TenderItem, LotItem


def clear_field(s):
    clean_s = s.replace("\t", "").replace("\n", "").strip()
    clean_s = unicodedata.normalize("NFKD", clean_s)
    return clean_s


def get_viewstate(response):
    return response.xpath("//input[@name='javax.faces.ViewState']/@value")[0]


def number_of_links(result):
    # result = result.replace(b'<![CDATA[', b'')
    return len(result.html.xpath("//tr[@role='row']/@data-rk"))


def determine_tender_type(tender_page):
    if len(tender_page.xpath("//div[contains(@id, 'lotsTable2')]")) == 0:
        return "products"
    else:
        return "services"


def count_lots(tender_page):
    return len(tender_page.xpath("//tbody[contains(@id, 'lotsTable')]/tr"))


def check_protocol(tender_page):
    return len(tender_page.xpath("//a[contains(@id, 'contest')]"))


def check_cancellation(tender_page):
    return len(
        tender_page.xpath("//span[@class='text red'][contains(text(),'Отменён')]")
    )


def count_participants(participants_page):
    return len(participants_page.xpath("//tbody[@id='submissions_data']/tr"))


def serialize_response_dict(dict):
    for key, value in dict.items():
        if value is not None:
            try:
                responses = []
                for response in value:
                    responses.append(response.serialize())
                dict[key] = {}
                dict[key]["l"] = responses
            except TypeError:
                dict[key] = value.serialize()
    return dict


def rehash_response_dict(dict, context):
    for key, value in dict.items():
        if value is not None:
            try:
                responses = []
                for response in value["l"]:
                    with context.http.rehash(response) as res:
                        responses.append(res)
                dict[key] = responses

            except KeyError:
                with context.http.rehash(value) as res:
                    dict[key] = res
    return dict


def to_int(plan_sum: str):
    result = 0
    if plan_sum is not None and len(plan_sum) > 0:
        try:
            result = re.findall(r"([\d,]*)", plan_sum)
            string = "".join(result)
            result = int(float(string.replace(",", ".")))
        except ValueError as ve:
            print(ve)
    return result


def lot_gen_info(tender_page, tr, td):
    result = tender_page.xpath(
        "//tbody[contains(@id, 'lotsTable')][contains(@id, '_data')]/tr[%s]/td[%s]/span[2]/text()"
        % (str(tr), str(td))
    )
    return ",".join(result)


def update_variable(filename, variable, new_value):
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, filename)
    print(base_path, file_path)
    with open(file_path, "r") as file:
        content = file.read()

    pattern = rf"{variable}\s*=\s*\d+"
    replacement = f"{variable} = {new_value}"
    updated_content = re.sub(pattern, replacement, content)

    # Открываем файл для записи обновленного содержимого
    with open(file_path, "w") as file:
        file.write(updated_content)


def fetch_tenders(response):
    rows = response.xpath("//tr")
    for row in rows:
        cols = row.xpath(".//td")
        tender_item = TenderItem()
        tender_id = clear_field(clear_field(cols[0].xpath(".//text()")[-1]))[6:]
        date = datetime.datetime.now()
        tender_date = clear_field(cols[7].xpath(".//text()")[-1])
        tender_date = to_iso_datetime(tender_date)

        tender_item["id"] = f"{const.OCDS_PREFIX}-{tender_id}-{date}"
        tender_item["tag"] = "compiled"  # TODO: update tag field
        tender_item["tender_id"] = tender_id
        tender_item["date"] = date
        tender_item["ocid"] = f"{const.OCDS_PREFIX}-{tender_id}"
        tender_item["initiationType"] = "tender"
        tender_item["tender_date"] = tender_date
        tender_item["tender_procurementSubMethodDetails"] = "standard"
        tender_item["tender_mainProcurementCategory"] = clear_field(
            cols[2].xpath(".//text()")[-1]
        )
        tender_item["tender_title"] = clear_field(cols[3].xpath(".//text()")[-1])
        tender_item["tender_status"] = "complete"
        tender_item["tender_procurementMethod"] = clear_field(
            cols[5].xpath(".//text()")[-1]
        )
        tender_item["tender_datePublished"] = tender_date
        tender_item["tender_tenderPeriod_startDate"] = tender_date
        tender_item["tender_tenderPeriod_endDate"] = to_iso_datetime(
            clear_field(cols[8].xpath(".//text()")[-1])
        )

        tender_item["tender_procurementMethodDetails"] = ""
        tender_item["tender_tenderNumber"] = ""
        tender_item["tender_enquiryPeriod_startDate"] = "1000-01-01"
        tender_item["tender_enquiryPeriod_endDate"] = "1000-01-01"
        yield tender_item


def fetch_lots(response, lot_index, tender_type, tender_id):
    lot_item = LotItem()

    lot_item["main_id"] = tender_id
    lot_item["lot_index"] = lot_index

    lot_item["title"] = clear_field(lot_gen_info(response, lot_index + 1, 2))
    if tender_type == "products":
        lot_item["deliveryDateDetails"] = clear_field(
            lot_gen_info(response, lot_index + 1, 7)
        )
        lot_item["deliveryTerms"] = clear_field(
            lot_gen_info(response, lot_index + 1, 6)
        )
    else:
        lot_item["deliveryDateDetails"] = clear_field(
            lot_gen_info(response, lot_index + 1, 5)
        )
        lot_item["deliveryTerms"] = ""  # TODO: Update deliveryTerms
    lot_item["status"] = "active"  # TODO: Update status
    lot_item["lotNumber"] = clear_field(lot_gen_info(response, lot_index + 1, 1))
    lot_item["deliveryAddress"] = clear_field(lot_gen_info(response, lot_index + 1, 4))
    lot_item["value_amount"] = to_int(lot_gen_info(response, lot_index + 1, 3))
    lot_item["value_currency"] = "KGS"

    yield lot_item


def to_iso_datetime(input_datetime):
    return datetime.datetime.strptime(
        input_datetime, const.INPUT_DATE_FORMAT
    ).isoformat()


def process_proposal_page(response_html, main_id):
    row_elements = response_html.xpath("//tbody[@id='submissions_data']/tr")

    for i, row_element in enumerate(row_elements):
        cell_with_table = row_element.xpath(".//td[3]")[0]
        inner_table = cell_with_table.xpath(".//table")[0]
        inner_table_rows = inner_table.xpath(".//tr")

        for j, inner_table_row in enumerate(inner_table_rows):
            # Extract unit value amount from the proposal row
            row_info = inner_table_row.xpath("normalize-space()")

            unit_value_amount_text = row_info.split(" ")[-1]
            if "xxxx" in unit_value_amount_text:
                unit_value_amount = 0
            else:
                unit_value_amount = to_int(unit_value_amount_text)

            # Create and yield BidDetailProposal item
            proposal_item = items.BidDetailProposal(
                main_id=main_id,
                bid_id=i + 1,
                proposal_id=j + 1,
                lot_number=row_info.split(" ")[0],
                unit_value_amount=unit_value_amount,
                unit_value_currency="KGS",
            )
            yield proposal_item

        # Create and yield BidDetailItem
        bid_detail_item = items.BidDetailItem(
            main_id=main_id,
            bid_id=i + 1,
            status="valid",
            date=datetime.datetime.now(),
        )
        yield bid_detail_item
