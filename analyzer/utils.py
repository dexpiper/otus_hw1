import os
from collections import namedtuple
import configparser
import logging
import re
from datetime import datetime


DateNamedFileInfo = namedtuple(
    'DateNamedFileInfo', ['file_path', 'file_date']
    )


def load_conf(conf_path, default_config=None):
    '''
    Loading config
    '''
    if os.path.isfile(conf_path):
        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read(conf_path, encoding='utf8')
        if not parser.sections():
            logging.error(
                'Section name should be defined in .ini config file'
            )
            return default_config
        return parser[parser.sections()[0]]
    else:
        logging.error(f'Config file with name {conf_path} was not found')
        return default_config


def setup_logger(log_path, loglevel=20):
    '''
    Setup logging settings
    '''
    log_path = None if log_path in (
            '', ' ', '   ', None, False
        ) else log_path
    if log_path:
        log_dir = os.path.split(log_path)[0]
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        elif not log_dir:
            log_path = '/'.join(('.', log_path))

    # configuring
    logging.basicConfig(filename=log_path, level=int(loglevel),
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S', force=True)


def get_latest_log_info(files_dir):
    '''
    '''
    if not os.path.isdir(files_dir):
        logging.error(
            f'Directory with log files {files_dir} has not been found'
        )
        return None

    latest_file_info = None
    for filename in os.listdir(files_dir):
        match = re.match(
            r'^nginx-access-ui\.log-(?P<date>\d{8})(\.gz)?$',
            filename
        )
        if not match:
            continue

        # if match:
        logging.info(
            f'Match found! {match.group("date")}'
        )
        date = datetime.strptime(
            match.group('date'),
            '%Y%m%d'
        )
        if latest_file_info:
            if date <= latest_file_info.file_date:
                continue

        # if no latest_file_info or new date is > old date
        latest_file_info = DateNamedFileInfo(
            file_path='/'.join((files_dir, filename)),
            file_date=date
        )
    return latest_file_info


def merge_configs(default_config, file_config):
    return {**dict(default_config), **dict(file_config)}
