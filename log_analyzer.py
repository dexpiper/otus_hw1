#!/usr/bin/env python3

# Python SL
import argparse
import configparser
import gzip
import io
import json
import logging
import os
import re
import statistics
import sys
from collections import deque, namedtuple
from datetime import datetime
from string import Template
from typing import Callable, Iterable

# internal
from regex import LOG_RECORD_RE


# default config
config = {
    'REPORT_SIZE': 1000,
    'REPORT_DIR': './reports',
    'REPORT_TEMPLATE': './config/report.html',
    'LOG_DIR': './log',
    'LOGFILE': None,
    'LOGLEVEL': 10,
    'ERRORS_LIMIT': None

}

# Record(href: str, request_time: str)
Record = namedtuple('Record', ['href', 'request_time'])

# DateNamedFileInfo(file_path: str, file_date: datetime.datetime object)
DateNamedFileInfo = namedtuple(
    'DateNamedFileInfo', ['file_path', 'file_date']
    )


def load_conf(conf_path: str) -> dict:
    '''
    Loading config
    '''
    if os.path.isfile(conf_path):
        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read(conf_path, encoding='utf8')
        return parser[parser.sections()[0]]
    else:
        raise FileNotFoundError


def setup_logger(log_path: str,
                 loglevel: int = 20) -> None:
    '''
    Setup logging settings
    '''
    log_path = log_path.strip() or None
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


def get_latest_log_info(files_dir: str) -> DateNamedFileInfo:
    '''
    Iterate over files in given directory, parse their names and
    return the file with the latest date in a namedtuple:

    result = get_latest_log_info(dir)
    path_to_file = result.file_path
    the_date = result.file_date

    where result.file_date is a datetime.datetime object.
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
        try:
            date = datetime.strptime(
                match.group('date'),
                '%Y%m%d'
            )
        except ValueError:
            logging.info(
                f'Could not extract datetime object from {match.group("date")}'
                f': str {date} does not match format "%Y%m%d"'
            )
            continue

        if latest_file_info and date <= latest_file_info.file_date:
            continue

        latest_file_info = DateNamedFileInfo(
            file_path='/'.join((files_dir, filename)),
            file_date=date
        )
    return latest_file_info


def merge_configs(default_config: dict, file_config: dict) -> dict:
    '''
    Merge two dicts with config. Resulting config would be a
    sum of the two. File config vars would have priority over
    the default config ones.
    '''
    return {**dict(default_config), **dict(file_config)}


def is_gzip_file(file_path: str) -> bool:
    '''
    Return True if dealing with .gz file
    '''
    return file_path.split('.')[-1] == 'gz'


def parse_log_record(log_line: str) -> Record or None:
    '''
    Parse given log line, get its URL and request time
    and give away in a namedtuple Record.
    '''
    r = LOG_RECORD_RE
    match = r.match(log_line)
    if match:
        href = match.group('href')
        request_time = match.group('time')
        return Record(href=href, request_time=request_time)


def get_log_records(
        log_path: str,
        errors_limit: int = None,
        parser: Callable = parse_log_record) -> Iterable[Record] or None:
    '''
    Open file, parse it line-by-line and return a list with all parsed
    records. Using fast deque() instead of simple list.
    '''
    open_fn = gzip.open if is_gzip_file(log_path) else io.open
    errors = 0
    records = 0
    result = deque()
    _hrefs = set()
    with open_fn(log_path, mode='rb') as log_file:
        for line in log_file:
            try:
                rec = parser(line.decode('utf-8'))
            except Exception as exc:
                logging.info('Cannot parse line: %s' % exc)
            if rec:
                result.append(rec)
                records += 1
                _hrefs.add(rec.href)
            else:
                errors += 1

    if errors_limit and all(
        records > 0,
        (errors / float(records)) > float(errors_limit)
    ):
        raise RuntimeError('Errors limit exceeded')

    logging.debug(f'Total records found: {records}, unique: {len(_hrefs)}')
    logging.debug(f'Resulting list length: {len(result)}')
    logging.debug(f'Total errors occurred: {errors}')
    return result


def create_report(records: Iterable,
                  max_records: str or int) -> Iterable[dict]:
    '''
    Analyze parsed records and create a list of all
    URLs with data for the report
    '''
    logging.info('Creating report, please wait...')
    max_records = int(max_records)
    total_records = 0
    total_time = 0
    int_data = {}
    result = []

    for href, response_time in records:
        response_time = float(response_time)
        total_time += response_time

        if href not in int_data:
            total_records += 1
            int_data[href] = dict(
                url=href,
                count=1,
                count_perc=0,
                time_sum=response_time,
                time_perc=0,
                time_avg=0,
                time_max=0,
                time_med=0,
                time_lst=[response_time]
            )
        else:
            try:
                int_data[href]['count'] += 1
                int_data[href]['time_sum'] = round(
                    (int_data[href]['time_sum'] + response_time),
                    3
                )
                int_data[href]['time_lst'].append(response_time)
            except KeyError:
                logging.info('KeyError during report creation')
                pass
    # end for

    for _, dct in int_data.items():
        dct['count_perc'] = round(
            (dct['count'] / total_records) * 100, 5)
        dct['time_perc'] = round(
            (dct['time_sum'] / total_time) * 100, 5)
        dct['time_avg'] = round(
            statistics.mean(dct['time_lst'] or [0]),
            5  # rounding precision
        )
        dct['time_max'] = max(dct['time_lst'] or [0])
        dct['time_med'] = round(
            statistics.median(dct['time_lst'] or [0]),
            5  # rounding precision
        )
        del dct['time_lst']
        result.append(dct)

    result = sorted(
        result,
        key=lambda result: result['time_sum'], reverse=True
    )
    return result[:max_records]


def render_template(report: Iterable[dict],
                    report_file_path: str,
                    template_path: str) -> None:
    '''
    Render and write down ready report in html file
    '''
    json_report = json.dumps(report)
    with open(template_path, mode='rb') as temp_file:
        contents = temp_file.read().decode('utf-8')
        t = Template(contents)
        ready_report_contents = t.safe_substitute(table_json=json_report)
    with open(report_file_path, mode='w+') as ready_file:
        ready_file.writelines(ready_report_contents)


def main(config: dict) -> None:
    '''
    Main logic. Call within try block.
    '''
    # resolving an actual log
    latest_log_info = get_latest_log_info(config['LOG_DIR'])
    if not latest_log_info:
        logging.info('No log files yet')
        return

    report_date_string = latest_log_info.file_date.strftime('%Y.%m.%d')
    report_filename = 'report-{}.html'.format(report_date_string)
    report_file_path = os.path.join(
        config['REPORT_DIR'],
        report_filename
    )

    logging.info(f'{report_filename}, {report_file_path}')

    if os.path.isfile(report_file_path):
        logging.info('Looks like everything is up-to-date')
        return

    # report creation
    latest_path = os.path.normpath(latest_log_info.file_path)
    logging.info(
        f'Collecting data from "{latest_path}"')
    log_records = get_log_records(
        latest_log_info.file_path,
        config.get('ERRORS_LIMIT')
    )
    report_data = create_report(
        log_records,
        config['REPORT_SIZE']
    )

    render_template(
        report=report_data,
        report_file_path=report_file_path,
        template_path=config['REPORT_TEMPLATE']
    )

    logging.info(
        'Report saved to {}'.format(
            os.path.normpath(report_file_path)
        )
    )
    logging.info('Task accomplished successfully')


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config', help='Config file path',
        default='./config/config.ini'
    )
    args = parser.parse_args()

    try:
        file_config = load_conf(args.config)
    except Exception:
        logging.error(f'Cannot read provided {args.config} config file')
        sys.exit(1)

    # merging default config with file config
    # while file config has priority
    logging.debug('Merging configs')
    config = merge_configs(
        default_config=config,
        file_config=file_config
    )

    setup_logger(
        config['LOGFILE'],
        loglevel=config['LOGLEVEL'])
    logging.info('Logging and config setup OK')

    try:
        main(config)
    except Exception:
        logging.exception('Exception during main function: ')
        raise
