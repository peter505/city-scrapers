# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
import json
import pytz
from datetime import datetime


class CapsSpider(scrapy.Spider):
    name = 'caps'
    long_name = 'Chicago Police'
    allowed_domains = ['https://home.chicagopolice.org/wp-content/themes/cpd-bootstrap/proxy/miniProxy.php?https://home.chicagopolice.org/get-involved-with-caps/all-community-event-calendars/']
    start_urls = ['https://home.chicagopolice.org/wp-content/themes/cpd-bootstrap/proxy/miniProxy.php?https://home.chicagopolice.org/get-involved-with-caps/all-community-event-calendars/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/<Chrome Rev> Mobile Safari/<WebKit Rev>'
    }

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        data = json.loads(response.body_as_unicode())

        for item in data:
            yield {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': self._parse_name(item),
                'description': self._parse_description(item),
                'classification': 'CAPS community event',
                'start_time': self._parse_start(item),
                'end_time': self._parse_end(item),
                'all_day': False,
                'status': 'confirmed',
                'location': self._parse_location(item),
                'url': self._parse_url(response),
            }

        # self._parse_next(response) yields more responses to parse if necessary.
        # uncomment to find a "next" url
        # yield self._parse_next(response)

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        next_url = None  # What is next URL?
        return scrapy.Request(next_url, callback=self.parse)

    def _parse_id(self, item):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        return item['calendarId']

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'Not classified'

    def _parse_status(self, item):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        return {
            'url': None,
            'name': item['location'],
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return item['title']

    def _parse_description(self, item):
        """
        Parse or generate event name.
        """
        return item['eventDetails']

    def _format_time(self, time):
        tz = pytz.timezone('America/Chicago')  # 2016-01-05T14:00:00
        dt = tz.localize(datetime.strptime(time, "%Y-%m-%dT%H:%M:%S"), is_dst=None)
        return dt.isoformat()

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        return self._format_time(item['start'])

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        try:
            return self._format_time(item['end'])
        except TypeError:
            return None

    def _parse_url(self, response):
        """
        Parse url.
        """
        return response.url