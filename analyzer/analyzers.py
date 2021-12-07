# Python SL
import gzip
import io
import json
import logging
import statistics
from collections import deque, namedtuple
from string import Template
from typing import Iterable

# internal
from analyzer.regex import LOG_RECORD_RE


# Record(href: str, request_time: str)
Record = namedtuple('Record', ['href', 'request_time'])


def is_gzip_file(file_path: str) -> bool:
    '''
    Return True if dealing with .gz file
    '''
    return file_path.split('.')[-1] == 'gz'


def get_log_records(
        log_path: str,
        errors_limit: int = None) -> Iterable[Record] or None:
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
        try:
            while True:
                rec = parse_log_record(
                    next(reader(log_file))
                )
                if rec:
                    result.append(rec)
                    records += 1
                    _hrefs.add(rec.href)
                else:
                    errors += 1
        except StopIteration:
            pass
        except Exception:
            logging.exception('Exception during log record parsing: ')
            return

    if errors_limit and all(
        records > 0,
        (errors / float(records)) > float(errors_limit)
    ):
        raise RuntimeError('Errors limit exceeded')

    logging.debug(f'Total records found: {records}, unique: {len(_hrefs)}')
    logging.debug(f'Resulting list length: {len(result)}')
    logging.debug(f'Total errors occurred: {errors}')
    return result


def reader(file: object) -> str:
    '''
    Generator function to lie-by-line reading of large file.
    '''
    line = file.readline()
    while len(line):
        yield line.decode('utf-8')


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
    else:
        return


def median(values_list: Iterable) -> float or None:
    return None if not values_list else statistics.median(values_list)


def mean(values_list: Iterable) -> float or None:
    return None if not values_list else statistics.mean(values_list)


def maximum(values_list: Iterable) -> float or None:
    return None if not values_list else max(values_list)


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
        dct['time_avg'] = round(mean(dct['time_lst']), 5)
        dct['time_max'] = maximum(dct['time_lst'])
        dct['time_med'] = round(median(dct['time_lst']), 5)
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
