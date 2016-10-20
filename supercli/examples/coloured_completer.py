#!/usr/bin/env python
import supercli.argparse
import logging
logger = logging.getLogger(__name__)


def cli_interface():
    """
    A simple dummy interface that shows off colours, and default arguments.
    """
    ansi_escape_codes = make_rainbow_text('*ANSI_ESCAPE_CODES*')
    description=(
        '_________________________________________________________________________________   \n'
        '``supercli.argparse.ArgumentParser`` is a subclass of the builtin `argparse`        \n'
        'module. I have tried to make the CLI interface more readable, and I have built      \n'
        'in the arguments that I use most frequently. On top of that, I have built in        \n'
        'some hidden arguments (useful for testing, but hidden from user so they are not     \n'
        'overwhelmed with options they will never use).                                      \n'
        '                                                                                    \n'
        '  * newlines are valid/used (but text still wraps if not enough room)               \n'
        '  * Colourized `ReStructuredText` syntax-highlighting (on Windows too!!)            \n'
        '  * Feel free to use {ansi_escape_codes} (on Windows too!!)                         \n'
        '  * LogHandler Reused if same python session (ex: IPython)                          \n'
        '  * all parsers receive a standard set of flags:                                    \n'
        '                                                                                    \n'
        '                                                                                    \n'
        '       `--verbose`             (logging.DEBUG)                                      \n'
        '       `--very-verbose`        (logging.DEBUG with custom filters disabled)         \n'
        '                                                                                    \n'
        '       ``extended_logopts:``                                                        \n'
        '           `--log-longfmt`         (detailed multiline log entries)                 \n'
        '           `--logfile`             (write to a file in addition to stdout)          \n'
        '           `--silent`              (disable logging to stdout)                      \n'
        '                                                                                    \n'
        '       ``developer_opts: (hidden by default)``                                      \n'
        '           `--pdb`                 (pdb/ipdb post-mortem automatically on crash)    \n'
        '           `--default-parser`      (display help with default argparse settings)    \n'
        '           `--gen-autocomp`        (generates autocompletion scripts. (ex: zsh,etc) \n'
        '                                                                                    \n'
        '                                                                                    \n'
        '_________________________________________________________________________________   \n'
        '_________________________________________________________________________________   \n'
    ).format(**locals())


    parser     = supercli.argparse.ArgumentParser( description=description, autocomp_cmd='coloured_completer' )
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
    return args

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
    args = cli_interface()

    logging.info('This is just a sample interface - it is not bound to a command.')
    logging.info('')
    logging.info('Try re-running this using following `hidden` flags: ')
    logging.info('   coloured_completer.py --devlog ')
    logging.info('   coloured_completer.py --pdb    ')
    logging.info('   coloured_completer.py --gen-autocomp')
    logging.info('   coloured_completer.py --default-parser --help')
    logging.info('')
    logging.info('For user-exposed arguments, use the help flag: ')
    logging.info('   coloured_completer.py --help  ')
    logging.info('')
    logging.info('For help on hidden dev arguments use --fullhelp')
    logging.info('   coloured_completer.py --fullhelp')
    logging.info('')
    logging.info('info text')
    logging.warning('warning text')
    logging.error('error text')
    logging.debug('debug text')


    if hasattr( args, 'pdb' ):
        if args.pdb:
            logger.warning("You used the flag `--pdb`. I'm raising an exception so you can see what it does")
            assert 0 == 1

            print('this will never get run, because the above assertion is not true')

