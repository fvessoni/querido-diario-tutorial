#  source ../../../.venv/bin/activate
#  scrapy crawl sp_paulinia

import datetime
import re

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider
import scrapy

# from bs4 import BeautifulSoup


class SpPauliniaSpider(BaseGazetteSpider):
    name = "sp_paulinia_v2"
    TERRITORY_ID = "2905206"
    start_date = datetime.date(2010, 1, 4)
    allowed_domains = ["www.paulinia.sp.gov.br"]
    start_urls = ["http://www.paulinia.sp.gov.br/semanarios"]
    i = 0

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse_years)


    def parse_years(self, response):
        self.i += 1
        years = response.css("div.col-md-1").extract()

        regex_year = re.compile(r">20\d{2}<")
        regex_href = re.compile(r"ctl00(.*?)',")
        for year in years:
            year_parsed = regex_year.search(year)
            href_parsed = regex_href.search(year)
            self.logger.warning("|%d| YEAR: ||%s|| EVENTTARGET: ||%s||",
                                self.i,
                                year_parsed.group()[1:5],
                                href_parsed.group()[:-2].replace('%24', '$'))

            yield scrapy.FormRequest.from_response(
                response,
                formdata={'__EVENTTARGET': href_parsed.group()[:-2].replace('%24', '$')},
                callback = self.parse
            )

    def parse(self, response):
        editions = response.xpath(
            "//div[@class='container body-content']//div[@class='row']//a[contains(@href, 'AbreSemanario')]"
        )
        for edition in editions:
            final_url = edition.xpath("./@href").get()
            link_pdf = "http://www.paulinia.sp.gov.br/semanarios/" + final_url

            # Vamos separar as três informações da string "29/01/2021 - 1582 - Edição Normal"
            full_desc = edition.xpath("./text()").get()
            sep = " - "
            gazette_date = datetime.datetime.strptime(
                full_desc.split(sep)[0], "%d/%m/%Y"
            ).date()
            edition_number = full_desc.split(sep)[1]
            is_extra_edition = full_desc.split(sep)[2].strip() == "Edição Extra"

            self.logger.warning("LINK_PDF: ||%s||", link_pdf)


            yield Gazette(
                date=gazette_date,
                edition_number=edition_number,
                file_urls=[link_pdf],
                is_extra_edition=is_extra_edition,
                power="executive",
            )


        #__EVENTTARGET: ctl00$corpo$lnkItem4
        #__EVENTARGUMENT:
        #__VIEWSTATE:
        #__VIEWSTATEGENERATOR: C751677A
        #__EVENTVALIDATION:


