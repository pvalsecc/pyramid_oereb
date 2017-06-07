# -*- coding: utf-8 -*-
import datetime
import pytest
from shapely.geometry import Point, Polygon
from shapely.wkt import loads

from pyramid_oereb.lib.records.documents import DocumentRecord
from pyramid_oereb.lib.records.geometry import GeometryRecord
from pyramid_oereb.lib.records.office import OfficeRecord
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from pyramid_oereb.lib.records.theme import ThemeRecord
from pyramid_oereb.lib.records.view_service import ViewServiceRecord


def test_get_fields():
    expected_fields = [
        'type',
        'canton',
        'municipality',
        'fosnr',
        'metadata_of_geographical_base_data',
        'land_registry_area',
        'limit',
        'number',
        'identdn',
        'egrid',
        'subunit_of_land_register',
        'plan_for_land_register',
        'public_law_restrictions',
        'references'
    ]
    fields = RealEstateRecord.get_fields()
    assert fields == expected_fields


def test_mandatory_fields():
    with pytest.raises(TypeError):
        RealEstateRecord()


def test_init():
    record = RealEstateRecord('test_type', 'BL', 'Nusshof', 1, 100,
                              loads('POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'))
    assert isinstance(record.type, str)
    assert isinstance(record.canton, str)
    assert isinstance(record.municipality, str)
    assert isinstance(record.fosnr, int)
    assert isinstance(record.land_registry_area, int)
    assert isinstance(record.limit, Polygon)
    assert record.metadata_of_geographical_base_data is None
    assert record.number is None
    assert record.identdn is None
    assert record.egrid is None
    assert record.subunit_of_land_register is None


def test_to_extract():
    office = OfficeRecord('Office')
    point = Point((0, 0))
    point_wkt = point.wkt
    polygon = loads('POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))')
    geometry = GeometryRecord('runningModifications', datetime.date(1985, 8, 29), geom=point, office=office)
    document = DocumentRecord('runningModifications', datetime.date(1985, 8, 29), u'Document', office)
    view_service = ViewServiceRecord('http://www.test.url.ch', 'http://www.test.url.ch')
    plr = PlrRecord(ThemeRecord('code', dict()), 'Content', 'runningModifications',
                    datetime.date(1985, 8, 29), office, view_service=view_service, geometries=[geometry])
    record = RealEstateRecord('test_type', 'BL', 'Nusshof', 1, 100, polygon,
                              public_law_restrictions=[plr], references=[document])

    assert record.to_extract() == {
        'type': 'test_type',
        'canton': 'BL',
        'municipality': 'Nusshof',
        'fosnr': 1,
        'land_registry_area': 100,
        'limit': polygon.wkt,
        'plan_for_land_register': {
            'link_wms': 'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&STYLES=default&'
                        'SRS=EPSG:21781&BBOX=475000,60000,845000,310000&WIDTH=740&HEIGHT=500&'
                        'FORMAT=image/png&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb',
            'legend_web': 'https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetLegendGraphic&VERSION=1.1.1&'
                          'FORMAT=image/png&LAYER=ch.bav.kataster-belasteter-standorte-oev.oereb'
        },
        'public_law_restrictions': [
            {
                'content': 'Content',
                'theme': {
                    'code': 'code',
                    'text': []
                },
                'legal_state': 'runningModifications',
                'responsible_office': {
                    'name': 'Office'
                },
                'view_service': {
                    'link_wms': 'http://www.test.url.ch',
                    'legend_web': 'http://www.test.url.ch'
                },
                'geometries': [
                    {
                        'legal_state': 'runningModifications',
                        'geom': point_wkt,
                        'office': {
                            'name': 'Office'
                        }
                    }
                ]
            }
        ],
        'references': [
            {
                'legal_state': 'runningModifications',
                'title': 'Document',
                'responsible_office': {
                    'name': 'Office'
                }
            }
        ]
    }