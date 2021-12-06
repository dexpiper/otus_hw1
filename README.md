# Log analyzer

Parses ngingx logs, provides nice html reports

### Table of contents
1. [Examples of use](#examples)
2. [List of config vars](#list-of-config-vars)
3. [Testing](#testing)

### Examples

##### Basic

1. *cd* to the dir with the log_analyzer
2. Put logs in log folder or configure path to it in *config/config.ini* (LOG_DIR)
3. Run:

`$ python3 log_analyzer.py`

4. Latest report would be placed in *./reports*

##### Advanced

By default, log_analyzer would use "config" dictionary inside the file and merge its contents with *config/config.ini* file (config file would override the dictionary).

You can either rewrite config.ini file or specify other config on the start. Usage:

`$ python3 log_analyzer.py --config <path_to_config>`

The specified config would override build-in dictionary, *config.ini* from config dir would not be loaded.

Config should be stored in a configuration file that python *configparser* can parse [(more info)](https://docs.python.org/3/library/configparser.html). There should be exactly one section in file with all the vars inside. You can pick any valid section name.

### List of config vars

- REPORT_SIZE:      *max URLs in report* (default: 1000)
- REPORT_DIR:       *default directory to store ready reports* (default: ./reports)
- REPORT_TEMPLATE:  *path to html-template for the reports* (default: ./config/report.html)
- LOG_DIR:          *path to folder with nginx logs* (default: ./log)
- LOGLEVEL:         *numeric log level: DEBUG = 10, INFO = 20* (default: 10)
- LOGFILE:          *path to save logging output into a file. Warning: if set, logging output will not propagate into stdout, only would come as file* (default: None)
- ERRORS_LIMIT:     *error limit to quit analyzing* (default: None)

### Testing

To run unit tests, run:

`$ python3 tests.py`

Optional arg -v (--verbose) can be used to get a more verbose answer.

Example report result can be obtained in */reports/report-2017.06.30.html*
