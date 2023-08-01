BASE_TENDER_URL = "http://zakupki.gov.kg/popp/view/order/"
DEFAULT_OFFSET = 21200
ROWS_NUMBER = 10

MAX_OFFSET = 50000

MAIN_URL = "http://zakupki.gov.kg/popp"
LIST_URL = "http://zakupki.gov.kg/popp/view/order/list.xhtml"
HOME_URL = "http://zakupki.gov.kg/popp/home.xhtml"
VIEW_URL = "http://zakupki.gov.kg/popp/view/order/view.xhtml"
CONTEST_URL = "http://zakupki.gov.kg/popp/view/contest.xhtml"

TENDER_LINK = "http://zakupki.gov.kg/popp/view/order/view.xhtml?id="
VIEWSTATE_KEY = "javax.faces.ViewState"

OCDS_PREFIX = "ocds-h7i0z4"

J_ID1 = 124
J_ID2 = 125

LINKS_FORM = {
    "javax.faces.partial.ajax": "true",
    "javax.faces.source": f"j_idt{J_ID1}:j_idt{J_ID2}:table",
    "javax.faces.partial.execute": f"j_idt{J_ID1}:j_idt{J_ID2}:table",
    "javax.faces.partial.render": f"j_idt{J_ID1}:j_idt{J_ID2}:table",
    "javax.faces.behavior.event": "page",
    "javax.faces.partial.event": "page",
    f"j_idt{J_ID1}:j_idt{J_ID2}:table_pagination": "true",
    f"j_idt{J_ID1}:j_idt{J_ID2}:table_first": "",
    f"j_idt{J_ID1}:j_idt{J_ID2}:table_rows": str(ROWS_NUMBER),
    f"j_idt{J_ID1}:j_idt{J_ID2}:table_skipChildren": "true",
    f"j_idt{J_ID1}:j_idt{J_ID2}:table_encodeFeature": "true",
    f"j_idt{J_ID1}": f"j_idt{J_ID1}",
    f"j_idt{J_ID1}:j_idt{J_ID2}:table_rppDD": ["10", "10"],
    f"j_idt{J_ID1}:j_idt{J_ID2}:table_selection": "",
    f"j_idt{J_ID1}:j_idt{J_ID2}_activeIndex": "0",
    "javax.faces.ViewState": "",
}

LINKS_OFFSET_KEY = f"j_idt{J_ID1}:j_idt{J_ID2}:table_first"
LINKS_ROWS_NUMBER_KEY = f"j_idt{J_ID1}:j_idt{J_ID2}:table_rows"

# TENDER
TENDER_FULL_NUMBERS_PATH = "//td[1]//text()"
TENDER_NAMES = "//td[4]//text()"
TENDER_TYPES = "//td[3]//text()"
TENDER_ENTITIES = "//td[2]//text()"
TENDER_METHODS = "//td[6]//text()"
TENDER_SUMS = "//td[7]//text()"
TENDER_PUBLICATION_DATES = "//td[8]//text()"
TENDER_DEADLINE_DATES = "//td[9]//text()"

SEARCH_FIELD_KEY = "tv1:search-field"

SEARCH_FORM = {
    "tv1:j_idt68": "tv1:j_idt68",
    SEARCH_FIELD_KEY: "",
    "tv1:j_idt71": "Найти",
}

RESULTS_FORM = {
    "j_idt104": "j_idt104",
    "j_idt104:j_idt105:table_rppDD": "10",
    "j_idt104:j_idt105:table_selection": "",
    "j_idt104:j_idt105_activeIndex": "0",
    "j_idt104:j_idt105:table:0:evaluation_findings": "j_idt104:j_idt105:table:0:evaluation_findings",
}

PRODUCT_LOTS_FORM = {
    "javax.faces.partial.ajax": "true",
    "javax.faces.source": "j_idt78:lotsTable",
    "javax.faces.partial.execute": "j_idt78:lotsTable",
    "javax.faces.partial.render": "j_idt78:lotsTable",
    "j_idt78:lotsTable": " j_idt78:lotsTable",
    "j_idt78:lotsTable_rowExpansion": "true",
    "j_idt78:lotsTable_expandedRowIndex": "0",
    "j_idt78:lotsTable_encodeFeature": "true",
    "j_idt78:lotsTable_skipChildren": "true",
    "j_idt76": "j_idt76",
    "j_idt78:tender-doc-explanation-table_rppDD": "10",
    "j_idt78:tender-doc-explanation-table_selection": "",
    "j_idt78_activeIndex": "0",
    "javax.faces.ViewState": "",
}

SERVICE_LOTS_FORM = {
    "javax.faces.partial.ajax": "true",
    "javax.faces.source: j_idt78": "lotsTable2",
    "javax.faces.partial.execute": "j_idt78:lotsTable2",
    "javax.faces.partial.render": "j_idt78:lotsTable2",
    "j_idt78:lotsTable2: j_idt78": "lotsTable2",
    "j_idt78:lotsTable2_rowExpansion": "true",
    "j_idt78:lotsTable2_expandedRowIndex": "0",
    "j_idt78:lotsTable2_encodeFeature": "true",
    "j_idt78:lotsTable2_skipChildren": "true",
    "j_idt76": "j_idt76",
    "j_idt78:tender-doc-explanation-table_rppDD": "10",
    "j_idt78:tender-doc-explanation-table_selection": "",
    "j_idt78_activeIndex": "0",
    "javax.faces.ViewState": "",
}

PARTICIPANTS_FORM = {
    "j_idt76": "j_idt76",
    "j_idt78:tender-doc-explanation-table_rppDD": "10",
    "j_idt78:tender-doc-explanation-table_selection": "",
    "j_idt78_activeIndex": "0",
    "j_idt78:contest": "j_idt78:contest",
}

# PARTIES
PARTIES_FORM = {
    "javax.faces.partial.ajax": "true",
    "javax.faces.source": "table",
    "javax.faces.partial.execute": "table",
    "javax.faces.partial.render": "table",
    "javax.faces.behavior.event": "page",
    "javax.faces.partial.event": "page",
    "table_pagination": "true",
    "table_first": "10",
    "table_rows": "10",
    "table_skipChildren": "true",
    "table_encodeFeature": "true",
    "form": "form",
    "j_idt66": "",
    "j_idt69": "",
    "ownershipType_focus": "",
    "ownershipType_input": "",
    "status_focus": "",
    "status_input": "",
    "table_rppDD": "10",
    "table_selection": "",
    "&javax.faces.ViewState": "-3170255911656275907%3A-6712369373119391444",
}

PARTIES_FORM_DETAIL = {
    "form": "form",
    "j_idt66": "",
    "j_idt69": "",
    "ownershipType_focus": "",
    "ownershipType_input": "",
    "status_focus": "",
    "status_input": "",
    "table_rppDD": "10",
    "table_selection": "",
    "javax.faces.ViewState": "",
    # "table:0:j_idt86": "table:0:j_idt86"
}

PARTY_NAME = "/html/body/div[3]/div/form/div/table/tbody/tr[1]/td[2]//text()"


INPUT_DATE_FORMAT = "%d.%m.%Y %H:%M"
