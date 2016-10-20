#!/usr/bin/env python
"""
Name :          supercli/argparseclr.py
Created :       August 28 2016
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   Convenience classes built overtop of the builtin argparse module
                with an emphasis on readability, and convenience.

                * argument colouring
                * rst-syntax-highlighting
                * logging enabled by default, default arguments for verbosity etc.
                * toggleable developer arguments (logformat,auto pdb-post-mortem,..)
________________________________________________________________________________
"""
## builtins
from   __future__    import unicode_literals
from   __future__    import absolute_import
import sys
import argparse
import datetime
import subprocess
import shlex
import os
## external
from   pygments               import highlight
from   pygments.lexers.markup import RstLexer
from   pygments.formatters    import TerminalFormatter
import colorama
## custom
from   .logging      import SetLog
from   .excepttools  import wrap_excepthook_pdb_postmortem
from   .autocomplete import ZshCompleter


OPTIONAL     = '?'
ZERO_OR_MORE = '*'
ONE_OR_MORE  = '+'
PARSER       = 'A...'
REMAINDER    = '...'
loc          = locals

#!TODO: argument validation. everywhere.

#!TODO: add autocompletion arg-types to take advantage of
#!      zsh's _file, _iface, .. etc.

#!TODO: unittests all around... and use to learn tox

#!TODO: --gen-autocomp is documented as allowing the user to
#!      specify which completer they want to use. Presently only using ZSH,
#!      but we need to handle this argument properly once we introduce bash
#!      completion



class LegibleHelpFormatter(argparse.RawTextHelpFormatter):
    """
    More Readable, Formattable argparse args help-line.

    * Reduces visual-clutter in argument examples
    * Newlines `\n` are used in all help lines
    * ReStructuredText in help is formatted/colourized using pygments
      (even on windows!)

    instead of:          -s [METAVAR, ...], --short-var [METAVAR, ...]
    you get:             -s, --short [METAVAR, ..]


    Original Source:
        http://stackoverflow.com/questions/23936145/python-argparse-help-message-disable-metavar-for-short-options
    """
    def __init__(self,*args,**kwds):
        super( LegibleHelpFormatter, self ).__init__(*args,**kwds)

    def _format_action_invocation(self, action):
        white='\033[37m'
        norm='\033[0m'
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            metavar  = '{white}{metavar}{norm}'.format(**locals())
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if Optional does take a value, it is listed after instead of twice
            #   -s, --long [METAVAR, ...]
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)

                for option_string in action.option_strings:
                    parts.append('%s' % option_string)

                parts[-1] += ' %s'%args_string

            metavar = ', '.join(parts)
            metavar  = '{white}{metavar}{norm}'.format(**locals())
            return metavar

    def _split_lines(self, text, width):
        """
        Raw formatted help line (so that you can use newlines)
        and additional spacing before/after help
        """

        ## For future modifications, this wraps the original call
        #return argparse.HelpFormatter._split_lines(self, text, width)

        retval = text.splitlines()
        return retval

    def _format_args(self, action, default_metavar):
        get_metavar = self._metavar_formatter(action, default_metavar)
        if action.nargs is None:
            result = '%s' % get_metavar(1)
        elif action.nargs == OPTIONAL:
            result = '[%s]' % get_metavar(1)
        elif action.nargs == ZERO_OR_MORE:
            result = '[%s [%s ...]]' % get_metavar(2)
        elif action.nargs == ONE_OR_MORE:
            #result = '%s [%s ...]' % get_metavar(2)
            result = '[%s ...]' % get_metavar(1)
        elif action.nargs == REMAINDER:
            result = '...'
        elif action.nargs == PARSER:
            result = '%s ...' % get_metavar(1)
        else:
            formats = ['%s' for _ in range(action.nargs)]
            result = ' '.join(formats) % get_metavar(action.nargs)
        return result


class _SubparsersProxy(object):
    def __init__(self, parser, default_parser, *args, **kwds):
        self.parser         = parser
        self.default_parser = default_parser


        ## Attributes
        self.default_subparsers = []
        self.subparsers         = []

        self.subparsers_obj         = super( ArgumentParser, parser ).add_subparsers(*args,**kwds)
        self.default_subparsers_obj = default_parser.add_subparsers(*args,**kwds)

    def add_parser(self,*args,**kwds):

        help  = ''
        title = ''



        ## Default Subparser
        default_subparser = self.default_subparsers_obj.add_parser(*args,**kwds)
        self.default_subparsers.append( default_subparser )



        ## Colourize text, and remember specific
        ## arguments for use in autocompletion scripts
        if 'help' in kwds:
            help         = kwds['help']
            kwds['help'] = colourize_text(kwds['help'])

        if 'title' in kwds:  title = kwds['title']
        else:                title = args[0]

        ret_subparser = self.subparsers_obj.add_parser(
                                _default_parser = default_subparser           ,
                                autocomp_cmd    = self.parser.autocomp_cmd ,
                                *args,**kwds
                              )


        ## set attributes on subparser
        def get_info():
            return {
                'title'    : title         ,
                'help'     : help          ,
                'parser_instance' : ret_subparser ,
            }
        ret_subparser.get_info = get_info



        ## remember subparser
        self.subparsers.append( ret_subparser )

        return ret_subparser

    def get_subparsers(self):
        return self.subparsers


class ArgumentParser(argparse.ArgumentParser):
    """
    Enhanced ArgumentParser with more Readable arguments, ReStructuredText Colours.
    Also, Newline characters are no longer stripped.

    ArgumentParser Subclass that uses LegibleHelpFormatter by default,
    and parsers automatically receive arguments to control loglevel.


    text_formatting:

        * newline characters can be used in help/description-arguments

        * syntax-highlights ReStructuredText by default.
          ( Terminal 8Colour mode - I find this more consistently readable )
          ( with non-standard terminal colourschemes                       )


    arguments:
        --pdb  pdb (or ipdb if available) post-mortem on unhandled-exception
        -v     loglevel debug
        -vv    loglevel devug with all filters disabled

    ____________________________________________________________________
    INPUT:
    ____________________________________________________________________
    description | 'this does ...'   | (opt) | The main description at the top of
                |                   |       | the help message.
                |                   |       |
    lexer       | pygments.lexers.* | (opt) | The lexer you would like to use to
                |                   |       | do syntax highlighting in your help
                |                   |       | documentation.
                |                   |       | (ReStructuredText by default)
    """
    def __init__(self,
                 description      = None,

                 ## autocompletion
                 autocomp_cmd     = None,     ## for autocompleter

                 ## syntaxhighlight opts
                 helpline_lexer     = RstLexer,
                 helpline_formatter = TerminalFormatter,

                 ## parser arguments
                 extended_logopts = False,
                 developer_opts   = False,

                 ## logging opts
                 loghandlers      = None,

                 _default_parser  = None,
                 *args, **kwds
              ):
        """

        argparse.ArgumentParser subclass that:

            * Uses Coloured ReStructuredText syntaxhighlighting in argument descriptions.
            * Newlines and ANSI escape-sequences are valid within argument descriptions (for readability)
            * Displays Colours on Windows
            * Less metavar clutter in argument-display
            * Automaticlly generates ZSH autocompletion script from parser/subparsers
            * Provides a standard set of default arguments:
                all:
                * --verbose             (logging.DEBUG)
                * --very-verbose        (logging.DEBUG with custom filters disabled)

                extended_logopts:
                * --logfile  <filepath>  (logs to a logfile in addition to stdout)
                * --silent               (disables logging to stderr)
                * --log-longfmt          (2x lines used for each logrecord. Lots of info for debugging)

                developer_opts:
                * --dev                 (replaces timestamp with __name__ and lineno in log entries)
                * --pdb                 (enters pdb/ipdb in post-mortem automatically on crash)
                * --default-parser      (display help without colours or custom formatting- default argparse settings)
                * --gen-autocomp  (regenerates autocomplete scripts. (ex: if you have changed arguments)
        ____________________________________________________________________________________________________
        INPUT:
        ____________________________________________________________________________________________________
        description         | 'Prog Does this...'       | (opt) | description of program.
                            |                           |       |
        autocomp_cmd        | 'wallmgr'                 |       | the name of the SHELL command that will be used
                            |                           |       | to run this CLI Interface
                            |                           |       | (used in generation of autocompleter scripts)
                            |                           |       |
        helpline_lexer      | pygments.lexers.*         | (opt) | lexer to use (RstLexer by default)
                            |                           |       |
        helpline_formatter  | pygments.formatters.*     | (opt) | formatter to use (TerminalFormatter by default)
                            |                           |       |
                            |                           |       |
                            |                           |       |
        extended_logopts    | True, False               | (opt) | by default, (-v,-vv,--pdb) arguments are added.
                            |                           |       | extended_logopts provides more options
                            |                           |       | (but is more crowded): (-lf, -ll, --silent)
                            |                           |       |
        developer_opts      | True, False               | (opt) | adds --dev argument (more logging info lineno, __name__, ...)
                            |                           |       |
        _default_parser     | argparse.ArgumentParser   | (int) | Internal-only argument, used by _SubparsersProxy
                            |                           |       | to pass a vanilla argparse.ArgumentParser to the
                            |                           |       | supercli ArgumentParser (in case we very specifically
                            |                           |       | need an unmodified ArgumentParser for something).
                            |                           |       |
        loghandlers         | [                         | (opt) | If the current logging setup does not suit your needs,
                            |   logging.Handler,        |       | you can build and submit your own formatted loghandlers.
                            |   logging.Handler,        |       | `-v` and `-vv` will operate on all submitted loghandlers
                            |   ...                     |       | as if they were built by this class.
                            | ]                         |       |
                            |                           |       |
        *args,**kwds        |                           |       | Anything else gets passed directly to ArgumentParser()
                            |                           |       |
        """
        ## Arguments
        self.autocomp_cmd       = autocomp_cmd
        self.helpline_lexer     = helpline_lexer
        self.helpline_formatter = helpline_formatter

        self.extended_logopts   = extended_logopts
        self.developer_opts     = developer_opts

        self.loghandlers        = loghandlers


        ## Attributes
        self.default_parser   = None
        self.used_flags       = []   ## stores every flag that has already been used.

        self.subparsers_obj   = None ## stores the subparsers obj if one exists
        self.devargs          = []
        self._extended_devargs_added = False



        ## Default argparse.ArgumentParser instance
        if _default_parser:
            self.default_parser = _default_parser
        else:
            self.default_parser   = argparse.ArgumentParser(description=description,*args,**kwds )


        ## Validation
        self._validate_args()

        description = colourize_text(description,helpline_lexer,helpline_formatter)
        super( ArgumentParser, self ).__init__(description=description,formatter_class=LegibleHelpFormatter,*args,**kwds )
        self._add_default_arguments()

    def _validate_args(self):
        if not self.autocomp_cmd:
            raise RuntimeError("Missing argument 'autocomp_cmd' ")


    def add_argument(self,*args,**kwds):
        """ reimplemented add_argument() method that colourizes text using Pygments """

        ## Default Parser
        if (args,kwds) not in self.used_flags:
            if args != ('-h','--help'):
                self.default_parser.add_argument(*args,**kwds)

        ## Readable Parser
        if 'help' in kwds:
            kwds['help']=colourize_text(
                    text      = kwds['help'],
                    lexer     = self.helpline_lexer,
                    formatter = self.helpline_formatter
                )
        retval = super( ArgumentParser, self ).add_argument(*args,**kwds)


        self.used_flags.append( (args,kwds) )
        return retval


    def add_subparsers(self,*args,**kwds):
        """
        Wraps add_subparsers in order to replace it's
        add_parser() method.
            * colourizes text
        """

        self.subparsers_obj = _SubparsersProxy(parser=self,default_parser=self.default_parser,*args,**kwds)
        return self.subparsers_obj

    def _add_default_arguments(self):

        self.add_argument(
            '--fullhelp', help="Display extended help menu with developer options",
            action='store_true',
        )

        self._add_default_logging_arguments()
        self._add_default_dev_arguments()

    def _add_default_logging_arguments(self):
        """
        Adds standardized logging arguments to the provided parser
        """

        self.add_argument(
            '-v', '--verbose', help='Prints more detailed log-information (`logging.DEBUG`)',
            action='store_true',
            )

        self.add_argument(
            '-vv', '--very-verbose', help='Same as verbose, but all log-filters are disabled.\n (All information is printed)',
            action='store_true',
            )


        if self.extended_logopts:
            self.add_argument(
                '-ll','--log-longfmt', help=("2x lines used for each logrecord. __file__,\n"
                                             "line-number, timestamp... The whole kit and kaboodle."),
                action='store_true',
                )

            self.add_argument(
                '-lf','--logfile', nargs='+', help="writes log to filepath specified after argument",
                metavar='/var/log/program.log',
                )

            self.add_argument(
                '--silent', help="Disables logging to stderr",
                action='store_true',
                )


        return self

    def _add_default_dev_arguments(self,force_create=False):
        """
        The developer options are special. They can be used
        from the commandline even if self.developer_opts is not enabled.
        ( which has the effect of making them invisible to the user, )
        ( but still useful to you                                    )
        """

        ## self.devargs is a list of all developper argument
        ## flags. If self.developper_opts == False, (so these arguments are not added)
        ## the developer flags are still available (just hidden from the help menu)
        self.devargs = [
            '--devlog','--pdb','--gen-autocomp','--default-parser'
        ]


        if any([ self.developer_opts, (force_create and not self.developer_opts)]):
            if not self._extended_devargs_added:
                self.add_argument(
                    '--devlog', help="         Replaces logged-time with the __name__ and line-number\n(useful while debugging)",
                    action='store_true',
                    )
                self.add_argument(
                    '--pdb', help=('         Automatically enters pdb (debugger) in post-mortem mode on crash\n'
                                   '(If available, uses ipdb)'),
                    action='store_true',
                )
                self.add_argument(
                    '--gen-autocomp', nargs='*', help=(
                                'Create Autocompletion script. \n'
                                'Optional arguments are the names of the shells to create autocompletion\n'
                                'scripts for. (Currently only supports zsh)'
                                ),
                    metavar = 'zsh',
                )

                self.add_argument(
                    '--default-parser', help='Display unmodified argparse output (no colours, changed formatting, etc)',
                    action='store_true',
                )
                self._extended_devargs_added = True

        return self


    def parse_args(self,*args,**kwds):
        """
        Wraps argument parsing so that logging-arguments are handled.
        """


        # ================
        # Hidden Arguments
        # ================

        cliargs = sys.argv

        ## enable (hidden) devargs options
        hidden_devargs_used = False
        if not any( flag in cliargs   for flag in ('-h','--help') ):
            if any( flag in cliargs   for flag in self.devargs ):
                self._add_default_dev_arguments(force_create=True)
                developer_args_used = True

        ## show help with all hidden commands
        if '--fullhelp' in cliargs:
            self._add_default_dev_arguments(force_create=True)
            developer_args_used = True
            sys.argv.append('--help')


        ## use default-parser on user's request
        if '--default-parser' in cliargs:
            args = self.default_parser.parse_args(*args,**kwds)
        else:
            args = super( ArgumentParser, self ).parse_args(*args,**kwds)


        # ======================
        # User-Visible Arguments
        # ======================

        def flag_used(attr):
            if hasattr( args, attr ):
                if getattr( args, attr ):
                    return True
            return False

        ## parse default arguments, and return the arguments
        ## to the caller
        if flag_used('pdb'):
            wrap_excepthook_pdb_postmortem()

        if not self.loghandlers:
            self._build_loghandler(args)
        else:
            self._setup_user_loghandlers(args)


        if '--gen-autocomp' in cliargs:
            self.create_autocompleters( writepath=None )
            sys.exit(0)

        return args

    def _build_loghandler(self,args):

        logfile   = None
        logstream = True
        logstr    = ''

        def flag_used(attr):
            if hasattr( args, attr ):
                if getattr( args, attr ):
                    return True
            return False


        if flag_used('verbose'):
            logstr += 'v'

        if flag_used('very_verbose'):
            logstr += 'vv'

        if flag_used('devlog'):
            logstr += 'd'

        if flag_used('log_longformat'):
            logstr += 'l'

        if flag_used('log_file'):
            logfile = args.log_file

        if flag_used('logfile_only'):
            logstream = False

        SetLog( logstr, logfile=logfile, logstream=logstream )

    def _setup_user_loghandlers(self,args):


        if args.verbose or args.very_verbose:

            ## set loglevel
            for loghandler in self.loghandlers:
                loghandler.setLevel( logging.DEBUG )

                ## remove logfilters
                if args.very_verbose:
                    for logfilter in loghandler.filters:
                        loghandler.removeFilter( logfilter )


    def create_autocompleters(self, writepath=None ):
        ZshCompleter( self, self.autocomp_cmd ).write( writepath )



# =========
# Functions
# =========

#!TODO: validate lexer/formatter
def colourize_text(text, lexer=RstLexer, formatter=TerminalFormatter):
    """
    Determine's terminal-environment to set pygments' formatter
    then colourizes text using pygment's reStructuredText()
    syntax highlighting capabilities.
    """
    if text:
        return highlight( text, lexer(), formatter() )

    return text



if __name__ == '__main__':
    pass


