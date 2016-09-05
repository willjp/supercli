
from supercli.argparse import ArgumentParser
import logging
logger = logging.getLogger(__name__)


def cli_interface():
    """
    A simple dummy interface that shows off colours, and default arguments.
    """
    ansi_escape_codes = make_rainbow_text('*ANSI_ESCAPE_CODES*')
    description=(
        '------------------------------                                                      \n'
        'Customized `argparse` module.                                                       \n'
        '                                                                                    \n'
        '  * newlines are valid/used (but text still wraps if not enough room)               \n'
        '                                                                                    \n'
        '  * Colourized `ReStructuredText` syntax-highlighting (on Windows too!!)            \n'
        '                                                                                    \n'
        '  * Feel free to use {ansi_escape_codes} (on Windows too!!)                         \n'
        '                                                                                    \n'
        '  * LogHandler Created/Reused and Colour-Coded (lv=INFO by default)                 \n'
        '                                                                                    \n'
        '  * all parsers receive a standard set of flags:                                    \n'
        '                                                                                    \n'
        '                                                                                    \n'
        '       * `--verbose`             (logging.DEBUG)                                  \n'
        '       * `--very-verbose`        (logging.DEBUG with custom filters disabled)     \n'
        '                                                                                    \n'
        '       extended_logopts:                                                            \n'
        '       * `--ll`                  (detailed multiline log entries)                 \n'
        '       * `--log-file`            (write to a file in addition to stdout)          \n'
        '       * `--logfile-only`        (disable logging to stdout)                      \n'
        '                                                                                    \n'
        '       developer_opts:                                                              \n'
        '       * `--pdb`                 (pdb/ipdb post-mortem automatically on crash)    \n'
        '       * `--default-parser`      (display help with default argparse settings)    \n'
        '       * `--regen-autocomplete`  (regenerates autocomplete scripts. (ex: zsh,etc) \n'
        '                                                                                    \n'
        '                                                                                    \n'
        'NOTES:                                                                              \n'
        '       --regen-autocomplete, and --default-parser are intended for developers       \n'
        '       and they are available even when ``developer_opts==False``.                  \n'
        '------------------------------                                                      \n'
    ).format(**locals())


    parser     = ArgumentParser( description=description )
    subparsers = parser.add_subparsers( dest='subparser_name' )


    ## Extract subparser
    extract_parser = subparsers.add_parser('extract', help='Extract files from archive')
    extract_parser.add_argument(
        '-t','--type', help='The type of archive we are extracting from',
        metavar='tar'
    )
    extract_parser.add_argument(
        '-o','--output', help='Directory you want to extract files to',
        metavar='/home/dev/'
    )

    ## Add subparser
    add_parser = subparsers.add_parser('add', help='Add files to an archive')
    add_parser.add_argument(
        '-d','--dirs', nargs='+', help='Directories to add to the archive',
        metavar=['/home/dev/a','/home/dev/b'],
    )

    args = parser.parse_args()

def make_rainbow_text(text):
    """
    Colourizes each character in a string of text.
    """

    rainbow = [
        '\033[31m', # red
        '\033[33m', # yellow
        '\033[32m', # green
        '\033[34m', # blue
        '\033[35m', # magenta
        '\033[36m', # cyan
    ]
    normal='\033[0m'

    text_colourized = ''

    index = 0
    for char in text:
        text_colourized+= rainbow[index] + char
        if index+1 < len(rainbow):
            index +=1
        else:
            index = 0
    text_colourized += normal

    return text_colourized


if __name__ == '__main__':
    cli_interface()

    logging.info('Running the following command to see more options:')
    logging.info('  ``python coloured_completer.py --help`` ')
    logging.info('info text')
    logging.warning('warning text')
    logging.error('error text')
    logging.debug('debug text')



