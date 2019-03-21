# -*- coding: utf-8 -*-
import os
import csv
import datetime
from urllib import parse
from brreg.items import CompanyItem
from scrapy.spiders import CrawlSpider


def _get_today():
    now = datetime.datetime.now()
    return now.strftime("%d.%m.%Y")


BRANCHES = {
    65: 'A Agriculture, forestry and fishing',
    66: 'B Mining and quarrying',
    67: 'C Manufacturing',
    68: 'D Electricity, gas, steam and air conditioning supply',
    69: 'E Water supply. sewerage, waste management and remediation activities',
    70: 'F Construction',
    71: 'G Wholesale and retail trade. repair of motor vehicles and motorcycles',
    72: 'H Transportation and storage',
    73: 'I Accommodation and food service activities',
    74: 'J Information and communication',
    75: 'K Financial and insurance activities',
    76: 'L Real estate activities',
    77: 'M Professional, scientific and technical activities',
    78: 'N Administrative and support service activities',
    79: 'O Public administration and defence. compulsory social security',
    80: 'P Education',
    81: 'Q Human health and social work activities',
    82: 'R Arts, entertainment and recreation',
    83: 'S Other service activities',
    84: 'T Activities of household as employers. undifferentiated goods- and services-producing activities of '
        'households for own account',
    85: 'U Activities of extraterritorial organisations and bodies'
}


class W2(CrawlSpider):
    name = "w2"
    allowed_domains = ['brreg.no']

    def __init__(self, date_from='', date_to='', *args, **kwargs):
        super(W2, self).__init__(*args, **kwargs)
        url = 'https://w2.brreg.no/kunngjoring/kombisok.jsp'
        self.date_from = date_from or _get_today()
        self.start_urls = [
            f'{url}?datoFra={self.date_from}&datoTil={date_to}&id_niva1=51&id_bransje1={branch_id}'
            for branch_id in BRANCHES.keys()
        ]

        if os.path.exists("data/today.csv"):
            os.remove("data/today.csv")
        else:
            self.logger.warn("today.csv does not exist")

    def parse(self, response):
        date = self.date_from
        rows = response.xpath('//tr')

        branch = BRANCHES.get(int(dict(parse.parse_qsl(parse.urlsplit(response.url).query)).get('id_bransje1')))

        with open('data/today.csv', mode='a') as employee_file:

            w2_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            for row in rows:

                href = row.xpath('td/p/a/@href').extract_first()

                if not href:
                    continue

                col = row.xpath('td/p//text()').extract()[1:]

                company = CompanyItem(
                    date=date,
                    company=col[0].replace('\n', '').strip(),
                    url=f'https://w2.brreg.no/kunngjoring/{href}',
                    branch=branch[2:],
                    announcement=col[2].replace('\n', '').strip(),

                    id=col[1].replace('\n', '').strip()
                )
                yield company
                self.logger.info(company)
                w2_writer.writerow(company.values())
