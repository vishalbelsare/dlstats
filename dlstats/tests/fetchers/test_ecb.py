import unittest
from unittest.mock import MagicMock, patch, Mock
from dlstats.fetchers import ecb
from dlstats import constants
from dlstats.tests.base import BaseDBTestCase
import pickle
import pkgutil
import sdmx
import datetime
from collections import OrderedDict


CATEGORIES = {
    'name': 'Concepts',
    'subcategories':[
        {'name': 'Example subcategory 1',
         'subcategories': [
             {'name': 'Example subcategory 1_1',
              'flowrefs': ['1_1_1']},
             {'name': 'Example subcategory 1_2',
              'flowrefs': ['1_2_1','1_2_2']}
         ]},
        {'name': 'Example subcategory 2',
         'subcategories': [
             {'name': 'Example subcategory 2_1'},
             {'name': 'Example subcategory 2_2',
              'flowrefs': ['2_2_1']}
         ]}
    ]}

DATAFLOWS = dict()
DATAFLOWS['1_1_1'] = {'ECB_TEST': ('ECB', '1.0', {'en': 'Name of 1_1_1'})}
DATAFLOWS['1_2_1'] = {'ECB_TEST': ('ECB', '1.0', {'en': 'Name of 1_2_1'})}
DATAFLOWS['1_2_2'] = {'ECB_TEST': ('ECB', '1.0', {'en': 'Name of 1_2_2'})}
DATAFLOWS['2_2_1'] = {'ECB_TEST': ('ECB', '1.0', {'en': 'Name of 2_2_1'})}

CODES = dict()

CODES = {'TEST':{'FREQ': {'M': 'Monthly',
         'Q': 'Quarterly'},
       'OTHER_DIM': {'O1': 'Option 1',
         'O2': 'Option',
         'O3': 'Option'}}}

RAW_DATA = dict()
RAW_DATA['2_2_1'] = dict()
RAW_DATA['2_2_1']['M'] = ({'M.O1':['1','2','3','4','5'],
                           'M.O2':['2','3','4','5','6']},
                          {'M.O1':['1999-01','1999-02','1999-03',
                                   '1999-04','1999-05'],
                           'M.O2':['1999-02','1999-03','1999-04',
                                   '1999-05','1999-05']},
                          {'M.O1':[{'OBS_STATUS':'A'},{'OBS_STATUS':'A'},
                                   {'OBS_STATUS':'A'},{'OBS_STATUS':'A'},
                                   {'OBS_STATUS':'A'}],
                           'M.O2':[{'OBS_STATUS':'F'},{'OBS_STATS':'A'},
                                   {'OBS_STATS':'A'},{'OBS_STATS':'A'},
                                   {'OBS_STATS':'A'}]},
                          {'M.O1':OrderedDict([('FREQ','M'),('OTHER_DIM','O1')]),
                           'M.O2':OrderedDict([('FREQ','M'),('OTHER_DIM','O2')])}
                         )
RAW_DATA['2_2_1']['Q'] = ({'Q.O1':['5','4','3','2','1'],
                           'Q.O2':['6','5','4','3','2']},
                          {'Q.O1':['2014-Q1','2014-Q2','2014-Q3',
                                   '2014-Q4','2015-Q1'],
                           'Q.O2':['2015-Q1','2015-Q2','2015-Q3',
                                   '2015-Q4','2016-Q1']},
                          {'Q.O1':[{'OBS_STATS':'F'},{'OBS_STATUS':'A'},
                                   {'OBS_STATUS':'A'},{'OBS_STATUS':'A'},
                                   {'OBS_STATUS':'A'}],
                           'Q.O2':[{'OBS_STATS':'A'},{'OBS_STATS':'A'},
                                   {'OBS_STATS':'A'},{'OBS_STATS':'A'},
                                   {'OBS_STATS':'A'}]},
                          {'Q.O1':OrderedDict([('FREQ','Q'),('OTHER_DIM','O1')]),
                           'Q.O2':OrderedDict([('FREQ','Q'),('OTHER_DIM','O2')])}
                         )

def dataflows(flowref):
    return DATAFLOWS[flowref]

def codes(key_family):
    return CODES[key_family]

def get_categories(self):
    return CATEGORIES

def raw_data(flowref, key):
    return RAW_DATA[flowref][list(key.values())[0]]


class ECBCategoriesDBTestCase(BaseDBTestCase):
    def setUp(self):
        BaseDBTestCase.setUp(self)
        self.fetcher = ecb.ECB(db=self.db)
        self.maxDiff = None
    @patch('sdmx.ecb.dataflows',dataflows)
    @patch('dlstats.fetchers.ecb.ECB.get_categories',get_categories)
    def test_categories(self):
        reference =[{'categoryCode': '1_1_1',
                     'docHref': None,
                     'exposed': True,
                     'name': 'Name of 1_1_1',
                     'provider': 'ECB'},
                    {'categoryCode': '1_2_1',
                     'docHref': None,
                     'exposed': True,
                     'name': 'Name of 1_2_1',
                     'provider': 'ECB'},
                    {'categoryCode': '1_2_2',
                     'docHref': None,
                     'exposed': True,
                     'name': 'Name of 1_2_2',
                     'provider': 'ECB'},
                    {'categoryCode': '2_2_1',
                     'docHref': None,
                     'exposed': True,
                     'name': 'Name of 2_2_1',
                     'provider': 'ECB'},
                    {'categoryCode': 'Concepts',
                     'docHref': None,
                     'exposed': True,
                     'name': 'Concepts',
                     'provider': 'ECB'},
                    {'categoryCode': 'Example subcategory 1',
                     'docHref': None,
                     'exposed': True,
                     'name': 'Example subcategory 1',
                     'provider': 'ECB'},
                    {'categoryCode': 'Example subcategory 1_1',
                     'docHref': None,
                     'exposed': True,
                     'name': 'Example subcategory 1_1',
                     'provider': 'ECB'},
                    {'categoryCode': 'Example subcategory 1_2',
                     'docHref': None,
                     'exposed': True,
                     'name': 'Example subcategory 1_2',
                     'provider': 'ECB'},
                    {'categoryCode': 'Example subcategory 2',
                     'docHref': None,
                     'exposed': True,
                     'name': 'Example subcategory 2',
                     'provider': 'ECB'},
                    {'categoryCode': 'Example subcategory 2_2',
                     'docHref': None,
                     'exposed': True,
                     'name': 'Example subcategory 2_2',
                     'provider': 'ECB'}]
        self.fetcher.upsert_categories()
        #We exclude ObjectIDs because their values are not determinitstic. We
        #can't test these elements
        results = self.db[constants.COL_CATEGORIES].find(
            {"provider": self.fetcher.provider_name},
            {'_id': False, 'children': False, 'lastUpdate':False})
        results = [result for result in results]
        self.assertEqual(results, reference)


class ECBDatasetDBTestCase(BaseDBTestCase):
    def setUp(self):
        self.maxDiff = None
        BaseDBTestCase.setUp(self)
        self.fetcher = ecb.ECB(db=self.db)
    @patch('sdmx.ecb.codes', codes)
    @patch('sdmx.ecb.dataflows', dataflows)
    @patch('sdmx.ecb.raw_data', raw_data)
    @patch('dlstats.fetchers.ecb.ECB.get_categories', get_categories)
    def test_upsert_dataset(self):

        reference = [{'attributes': {},
                      'datasetCode': '2_2_1',
                      'dimensions': {'FREQ': 'M', 'OTHER_DIM': 'O1'},
                      'endDate': 352,
                      'frequency': 'M',
                      'key': 'M.O1',
                      'name': 'M-O1',
                      'provider': 'ECB',
                      'startDate': 348,
                      'values': ['1', '2', '3', '4', '5']},
                     {'attributes': {},
                      'datasetCode': '2_2_1',
                      'dimensions': {'FREQ': 'M', 'OTHER_DIM': 'O2'},
                      'endDate': 352,
                      'frequency': 'M',
                      'key': 'M.O2',
                      'name': 'M-O2',
                      'provider': 'ECB',
                      'startDate': 349,
                      'values': ['2', '3', '4', '5', '6']},
                     {'attributes': {},
                      'datasetCode': '2_2_1',
                      'dimensions': {'FREQ': 'Q', 'OTHER_DIM': 'O1'},
                      'endDate': 180,
                      'frequency': 'Q',
                      'key': 'Q.O1',
                      'name': 'Q-O1',
                      'provider': 'ECB',
                      'startDate': 176,
                      'values': ['5', '4', '3', '2', '1']},
                     {'attributes': {},
                      'datasetCode': '2_2_1',
                      'dimensions': {'FREQ': 'Q', 'OTHER_DIM': 'O2'},
                      'endDate': 184,
                      'frequency': 'Q',
                      'key': 'Q.O2',
                      'name': 'Q-O2',
                      'provider': 'ECB',
                      'startDate': 180,
                      'values': ['6', '5', '4', '3', '2']}]

        self.fetcher.upsert_categories()
        self.fetcher.upsert_dataset('2_2_1')
        results = self.db[constants.COL_SERIES].find(
            {"provider": self.fetcher.provider_name},
            {'_id': False, 'releaseDates': False})
        results = [result for result in results]
        self.assertEqual(results, reference)

if __name__ == '__main__':
    unittest.main()