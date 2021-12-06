# PSL
import unittest
from datetime import datetime
import os

# internal modules
from log_analyzer import config
from analyzer.utils import get_latest_log_info, load_conf, merge_configs
from analyzer.analyzers import get_log_records, create_report, render_template


class UnitTests(unittest.TestCase):

    def setUp(self):
        self.fixture_data_path = 'tests/test_data'
        self.fixture_config = 'test_config.ini'
        self.fixture_logpath = 'tests/test_data/log'
        self.fixture_file_to_parse = '/'.join((
            self.fixture_logpath,
            'nginx-access-ui.log-20170630'
        ))
        self.fixture_report_path = '/'.join((
            'tests/test_data/reports',
            'test_report.html'
        ))

    def test_config_loading(self):
        test_config_path = '/'.join(
                (self.fixture_data_path, self.fixture_config)
            )
        self.assertTrue(
            os.path.isfile(test_config_path),
            f'Could not find test_config.ini file in {test_config_path}'
        )
        conf = load_conf(
            '/'.join(
                (self.fixture_data_path, self.fixture_config)
            )
        )
        self.assertEqual(conf.get('TEST_VAR'), '12345')

    def test_config_precedence(self):
        default_config = {'Foobar': 2, 'Parrot': 1}
        file_config = {'Parrot': 123, 'KingArthur': 1}
        conf = merge_configs(default_config, file_config)
        self.assertEqual(conf.get('Parrot'), 123)
        self.assertEqual(conf.get('Foobar'), 2)
        self.assertEqual(conf.get('KingArthur'), 1)

    def test_latest_log_finding(self):
        latest_file = get_latest_log_info(
            self.fixture_logpath
        )
        self.assertEqual(
            latest_file.file_date,
            datetime.strptime('20170630', '%Y%m%d')
        )

    def test_log_reader_functionality(self):
        latest_file = self.fixture_file_to_parse
        records = get_log_records(latest_file)
        self.assertEqual(len(records), 16)
        rec = records[10]
        self.assertEqual(rec.href, '/api/1/banners/?campaign=2765576')
        self.assertEqual(rec.request_time, '0.216')

    def test_create_report(self):
        records = get_log_records(self.fixture_file_to_parse)
        report = create_report(records, max_records=1000)
        self.assertTrue(len(report))
        self.assertEqual(len(report[-1].keys()), 8)

    def test_render_template(self):
        records = get_log_records(self.fixture_file_to_parse)
        report = create_report(records, max_records=1000)
        render_template(
            report=report,
            report_file_path=self.fixture_report_path,
            template_path=config['REPORT_TEMPLATE']
            )
        self.assertTrue(
            os.path.isfile(self.fixture_report_path))
