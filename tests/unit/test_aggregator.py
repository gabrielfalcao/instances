#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from instances.data.aggregators import VisitorAggregator

fake_visitor = lambda country_code, time: {
    "geo": {
        "city": "Brooklyn",
        "region_name": "NY",
        "area_code": 718,
        "time_zone": "America/New_York",
        "dma_code": 501,
        "metro_code": "New York, NY",
        "country_code3": "USA",
        "latitude": 40.71109999999999,
        "postal_code": "11211",
        "longitude": -73.9469,
        "country_code": country_code,
        "country_name": "United States",
        "continent": "NA",
    },
    "time": time,
}


def test_visitor_aggregator_by_country():
    ("VisitorAggregator#by_country() should return the visitors grouped by country code")
    # Given some visitors
    visitors = [
        fake_visitor("US", 100),
        fake_visitor("US", 10),
        fake_visitor("US", 1000),
        fake_visitor("US", 1),
        fake_visitor("BR", 200),
        fake_visitor("BR", 20),
        fake_visitor("MX", 400),
    ]

    # When I aggreate them
    by_country = VisitorAggregator(visitors).by_country()

    # Then they should be grouped by country
    by_country.should.equal({
        "US": [
            fake_visitor("US", 1),
            fake_visitor("US", 10),
            fake_visitor("US", 100),
            fake_visitor("US", 1000),
        ],
        "BR": [
            fake_visitor("BR", 20),
            fake_visitor("BR", 200),
        ],
        "MX": [
            fake_visitor("MX", 400),
        ],
    })
