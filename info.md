# CSS selectors

next_page = response.css('.ui-paginator-next[aria-label="Next Page"]').get()

all_tenders = response.css('[data-ri]')
tender_num = response.css('[role="gridcell"]')[0].css('td::text')[-1].get().strip()
tender_org_name = response.css('[role="gridcell"]')[1].css('td::text')[-1].get().strip()
tender_type = response.css('[role="gridcell"]')[2].css('td::text')[-1].get().strip()
tender_product_name = response.css('[role="gridcell"]')[3].css('td::text')[-1].get().strip()
tender_url = response.css('[role="gridcell"]')[4].xpath('a/@href').extract_first()
tender_method = response.css('[role="gridcell"]')[5].css('td::text')[-1].get().strip()
tender_sum = response.css('[role="gridcell"]')[6].css('td::text')[1].css('td::text')[-1].get().strip()
tender_start_date = response.css('[role="gridcell"]')[7].css('td::text')[-1].get().strip()
tender_end_date = response.css('[role="gridcell"]')[8].css('td::text')[-1].get().strip()

# Информация о лотах
## Товары. 7 столбцов:
1. Номер лота
2. Наименование лота
3. Сумма
4. Адрес и Место поставки
5. Условие поставки
6. Условие поставки
7. Сроки поставки товара 

## Работы. 6 столбцов:
1. Номер лота (L001-01)
2. Наименование лота
3. Сумма
4. Адрес и Место работ / услуг 
5. Срок выполнения работ 
6. График работ / услуг 

## Услуги. 6 столбцов
1. Номер лота (L001-01)
2. Наименование лота
3. Сумма
4. Адрес и Место работ / услуг 
5. Срок выполнения работ 
6. График работ / услуг 
