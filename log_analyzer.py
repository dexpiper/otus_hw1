#!/usr/bin/env python3

# Python SL
import argparse
import logging
import os

# internal modules
from analyzer.utils import (get_latest_log_info, merge_configs,
                            setup_logger, load_conf)
from analyzer.analyzers import get_log_records, create_report, render_template


# default config
config = {
    'REPORT_SIZE': 1000,
    'REPORT_DIR': './reports',
    'REPORT_TEMPLATE': './config/report.html',
    'LOG_DIR': './log',
    'LOGFILE': None,
    'LOGLEVEL': 10,
    'DEFAULT_CONFIG_PATH': './config/config.ini',
    'ERRORS_LIMIT': None

}


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


if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config', help='Config file path',
        default=config['DEFAULT_CONFIG_PATH']
    )
    args = parser.parse_args()

    # loading config
    file_config = load_conf(args.config, default_config=config)

    if file_config:
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
