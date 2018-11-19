"""
Utility to lint travis-ci.org .travis.yml files by requesting linting from
the travis-ci-org website.

This avoids having to install lots and lots of Ruby and other stuff just to
lint the file.
"""
from __future__ import print_function
import argparse
import json
import logging
from yamllint import linter
from yamllint.config import YamlLintConfig
import requests

log = logging.getLogger(__name__)    # pylint: disable=invalid-name


# Requests (urllib3) generates a lot of warnings which we don't care about so
# disable them.  Note also that the import structure that gets to urllib3
# confuses pylint so we have to disable the watning.
requests.packages.urllib3.disable_warnings()    # pylint: disable=no-member

URI_LINTER = 'https://api.travis-ci.org/lint'
KEY = 'key'
LEVEL = 'level'
MESSAGE = 'message'
ERROR = 'error'
WARNING = 'warning'
LINT = 'lint'
WARNINGS = 'warnings'


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class GenericLintException(Error):
    """Exception raised if generic lint errors are found.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        super(GenericLintException, self).__init__()
        self.message = message

    def __str__(self):
        return self.message


class TravisCiLintException(Error):
    """Exception raised if Travis-CI lint errors are found.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        super(TravisCiLintException, self).__init__()
        self.message = message

    def __str__(self):
        return self.message


class LoggingFormatter(logging.Formatter):
    """ Custom formatter that doesn't show exception stack. """

    def formatException(self, _exc_info):
        """ Return not exception information. """
        return ''


# import yamllint
def argparser():
    """
    Build an arguments parser.

    :returns: An arguments parser.
    :rtype: Parser
    """
    parser = argparse.ArgumentParser(
        description="Lint a .travis.yml file")
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="verbose output of progress")
    parser.add_argument(
        "-d", "--debug", action="store_true",
        help=argparse.SUPPRESS)
    parser.add_argument(
        "filename", action="store", nargs="?", default=".travis.yml",
        help="name of the file to lint (default: .travis.yml)")

    return parser


def main():
    """
    Mainline script which does the following.
    - Parses arguments
    - Reads the .travis.yml file assuming YAML
    - Passes the file contents to travis-ci.org linter
    - Displays the results.
    """

    # Parse command line arguments.
    parser = argparser()
    args = parser.parse_args()

    # First lint the file as a generic YAML file.
    try:
        log.setLevel(logging.WARNING)
        if args.verbose:
            log.setLevel(logging.INFO)
        if args.debug:
            log.setLevel(logging.DEBUG)
            log.debug('Debugging enabled')

        log.info('Performing generic YAML linting...')
        with open(args.filename, 'r') as yaml_file:
            log.debug('File %s opened successfully', args.filename)
            results = linter.run(yaml_file, YamlLintConfig('{}'))
            invalid = False
            log.debug('Linter returned results')
            for problem in results:
                msg = '%(fn)s:%(line)s:%(col)s: [%(level)s] %(msg)s' % {
                    'fn': args.filename,
                    'line': problem.line,
                    'col': problem.column,
                    'level': problem.level,
                    'msg': problem.message}

                if problem.level == ERROR:
                    log.debug('Gneric YAML error discovered')
                    invalid = True

                logging.warning(msg)

            if invalid:
                raise GenericLintException(
                    'One or more generic lint errors detected.')

            # It's valid generic YAML so now try as Trvis-CI YAML.
            log.info('Performing Travis-CI YAML lint...')

            # Rewind YAML file back to the start and then pass to the Travis-CI
            # lint webpage.
            yaml_file.seek(0, 0)
            log.info('POSTing to Travis-CI linter...')

            # Pass the YAML to the travis-ci.org linter.
            json_result = requests.post(
                URI_LINTER, data={'content': yaml_file.read()})
            log.debug('POST to Travis-CI linter completed')

            # The results are returned as JSON.
            result = json.loads(json_result.text)

            if not result[LINT]:
                raise TravisCiLintException(
                    'Travis-CI did not return a lint result.')

            for msg_type in result[LINT]:
                for report in result[LINT][msg_type]:
                    message = ''
                    if report[KEY]:
                        message = (
                            'in %s \'section\': ' % '.'.join(report[KEY]))
                    message = message + report[MESSAGE]

                    # print("%s" % str(report[MESSAGE]))
                    msg = '%(fn)s:%(line)s:%(col)s: [%(level)s] %(msg)s' % {
                        'fn': args.filename,
                        'line': 0,
                        'col': 0,
                        'level': msg_type,
                        'msg': message}
                    log.warning(msg)

            if WARNINGS in result[LINT] and result[LINT][WARNINGS]:
                raise TravisCiLintException(
                    'One or more Travis-CI lint errors detected.')

            log.info('File is clean!')

    except (GenericLintException, TravisCiLintException) as exc:
        log.exception(exc)

    except Exception as exc:        # pylint: disable=broad-except
        log.exception('Error opening file: %s: %s', args.filename, str(exc))


if __name__ == '__main__':
    sh = logging.StreamHandler()    # pylint: disable=invalid-name
    sh.setFormatter(LoggingFormatter())
    log.addHandler(sh)
    main()