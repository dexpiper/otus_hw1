#!/usr/bin/env python3
'''
Running tests.

Usage:
$ python3 tests.py [-v, --verbose]
'''
import argparse
import subprocess

#
# Running tests
#
argpars = argparse.ArgumentParser()
argpars.add_argument(
        '-v', '--verbose', help='More verbose test information',
        action='store_true'
    )
args = argpars.parse_args()

command = ['python', '-m', 'unittest']
test_path = 'tests/test_units.py'
if args.verbose:
    print('Running in verbose mode')
    command.append('-v')
command.append(test_path)

subprocess.run(command)
