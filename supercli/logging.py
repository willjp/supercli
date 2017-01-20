#!/usr/bin/env python
"""
Name :          supercli/logging.py
Created :       Sept 04 2016
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   A set of tools built overtop of the builtin logging module.
                (coloured logging,sensible format defaults, etc)
________________________________________________________________________________
"""
## builtins
from   __future__    import unicode_literals
from   __future__    import absolute_import
from   numbers       import Number
import logging
import sys
import re
import os
## external
import colorama
import six


loc = locals

#!TODO: Whitelist should match functions like blacklist
#!TODO: Whitelist and blacklist should be able to be used together
#!TODO: Dynamic logging widget (standard log-system)
#!TODO: Dynamic logging widget (interactive, bundles info,functions with logs)


# =======
# Filters
# =======

class Whitelist(logging.Filter):
    def __init__(self, whitelist):
        import logging
        self.whitelist = [ logging.Filter(entry)  for entry in whitelist ]

    def filter(self, record):
        return any( entry.filter(record) for entry in self.whitelist )


class Blacklist(logging.Filter):
    def __init__(self, blacklist ):

        self.blacklist = [ '*%s*' % entry   for entry in blacklist ]

    def filter(self, record):
        """
        If filter does not match any entry in blacklist,
        then log it.
        """
        import fnmatch

        record_modpath = '%s.%s' % (record.name, record.funcName)

        match_found = False
        for entry in self.blacklist:
            if fnmatch.fnmatch( record_modpath, entry ):
                match_found = True
                return 0

        return 1



# ==============
# LogHander Mgmt
# ==============

class SetLog( object ):
    def __init__(
                    self,
                    str_arg        = None,
                    lv             = 'INFO',
                    reuse          = True,
                    colorize       = True,
                    filter_type    = Blacklist,
                    filter_matches = None,
                    logfile        = None,
                    logstream      = True,
                    logfile_size   = 1000000, # 8Mb
                    debug_mode     = False,
                ):
        """
        More powerful replacement for logging.baseConfig().

            * coloured log-entries by severity (outside of maya)
            * record-filtering
            * multiple stream support (file AND/OR stream, etc)
            * file log-rotation by default (if logging to file)
            * more readable records,
            * handles maya script-editor logging



        str_arg values are designed to be used together:

            loggingTools.setlog( ''    ) ## is logging.INFO,  colourized, displays datetime
            loggingTools.setlog( 'd'   ) ## is logging.INFO,  colourized, time replaced with caller-info
            loggingTools.setlog( 'vd'  ) ## is logging.DEBUG, colourized, time replaced with caller-info
            loggingTools.setlog( 'vvd' ) ## is logging.DEBUG, unfiltered, time replaced with caller-info
            ... etc.

        ________________________________________________________________________________________________________
        INPUT:
        ________________________________________________________________________________________________________
        str_arg        | None, 'vo'                  | (opt) | short-form configuration of log. Each letter represents
                       |                             |       | a configuration option:
                       |                             |       |
                       |                             |       |   v  = 'verbose'
                       |                             |       |   vv = 'very-verbose'
                       |                             |       |   i  = 'info'
                       |                             |       |   c  = 'critical'
                       |                             |       |   w  = 'warn'
                       |                             |       |   d  = 'developper logging (caller-info instead of time)'
                       |                             |       |   l  = 'multiline logrecords'
                       |                             |       |
                       |                             |       |
                       |                             |       |
        lv             | 'INFO','DEBUG', 'WARN', ... | (opt) | the loglevel you'd like to set.
                       | 5, 10, 20, ...              |       | 'info' by default. case-insensitive.
                       |                             |       | (overridden by str_arg)
                       |                             |       |
        reuse          | True, False                 | (opt) | Try to reuse existing loghandlers if
                       |                             |       | they exist. If not set to true, in IPython/maya python sessions
                       |                             |       | we would continually creating and printing duplicates of streams.
                       |                             |       |
        colorize       | True, False                 | (opt) | colourize the log-output by severity?
                       |                             |       |
        filter_matches | none,                       |       | A list of filter-values to pass to the
                       | [ 'myfunc', 'some__name__'] | (opt) | filter of your choosing. How they are handled
                       |                             |       | depends on the filter.
                       |                             |       |
                       |                             |       | The filters above are fnmatch matches against '<import_path>.<function_name>'
                       |                             |       | in the format '*<filter_match>*'.
                       |                             |       |
                       |                             |       |
        filter_type    | WhiteList, BlackList        | (opt) | A subclass of logging.Filter that you want to
                       |                             |       | use to filter the log results. Should be the class object itself.
                       |                             |       |
        logfile        | None, '/tmp/mylog.log'      | (opt) | If logging to a file, what file you want to log to.
                       |                             |       | (otherwise, logs to a streamhandler)
                       |                             |       |
        logfile_size   | 100000000                   | (opt) | Size in bytes of logfile. Defaults to 8 Megabytes.
                       |                             |       |
        logstream      | True, False                 | (opt) | By default, we will always log to a stream. However,
                       |                             |       | you can disable the stream if for example you want to log to a file and not to stdout
                       |                             |       |
        debug_mode     | True, False                 | (opt) | Enable to Debug this class using print statements.
                       |                             |       | Not intended for production.
                       |                             |       |
        """

        ## Arguments
        self.str_arg         = str_arg
        self.lv              = lv
        self.reuse           = reuse
        self.colorize        = colorize
        self.filter_matches  = filter_matches
        self.filter_type     = filter_type
        self.logfile         = logfile
        self.logfile_size    = logfile_size
        self.logstream       = logstream
        self.debug_mode      = debug_mode

        ## Attributes
        self.is_maya = False        ## set to true if running python within maya (NOT mayapy)

        self.linefmt_norm = '[ %(asctime)s ] %(levelname)-8s: %(message)s'
        self.linefmt_dev  = '[ %(funcName)-35s ]ln%(lineno)-4s %(levelname)-8s: %(message)s'
        self.linefmt_long = '[ %(asctime)s ] %(levelname)-8s: %(message)s\n[    ln %(lineno)-4s  ]              %(name)s.%(funcName)-90s \n'
        self.datefmt      = '%Y/%m/%d |%I:%M %p|'


        self.main()

    def main(self):
        self.validate_args()
        self.is_running_mayagui()
        self.parse_strarg()
        self.create_loghandlers()
        self.colorize_log()

    def validate_args(self):
        """
        Check for problems with user arguments.
        """

        ## filter_matches
        if self.filter_matches == None:
            self.filter_matches = []
        if not hasattr( self.filter_matches, '__iter__' ):
            raise TypeError('argument filters must be iterable (list,tuple,etc)')

        ## filter_types
        if not issubclass( self.filter_type, logging.Filter ):
            raise TypeError('self.filter_type must be a subclass of logging.Filter')

        ## logfile
        if self.logfile:
            self.logfile = os.path.realpath( self.logfile ).replace( '\\','/' )

    def parse_strarg(self):
        """
        Parses str_arg, a convenient short-form way of setting loglevel,
        and modifying the log output.

        v  = 'verbose'
        vv = 'very-verbose'
        w  = 'warn'
        i  = 'info'
        c  = 'critical'
        l  = 'multiline logrecords'
        d  = 'dev-mode (replace datetime with __name__ & lineno)
        """

        self.linefmt = self.linefmt_norm

        if self.str_arg != None:

            ## log verbosity
            ##

            if isinstance( self.lv, six.text_type ):
                if   'v' in self.str_arg:     self.lv = 'DEBUG'
                elif 'w' in self.str_arg:     self.lv = 'WARN'
                elif 'i' in self.str_arg:     self.lv = 'INFO'
                elif 'c' in self.str_arg:     self.lv = 'CRITICAL'
            elif not isinstance( self.lv, Number ):
                raise TypeError('expected either a string, or a number for loglevel. received: %s' % self.lv )


            ## In your program, you might want to tone down the logging on
            #  some of the more chatty library modules. The 'vv' flag
            #  gives the user the power to disable these filters.
            if self.filter_matches:
                if 'vv' in self.str_arg:
                    self.filter_matches = []


            ## logrecord formatting
            ##
            if   'l' in self.str_arg:
                self.linefmt = self.linefmt_long
                self.datefmt = None

            elif 'd' in self.str_arg:
                self.linefmt = self.linefmt_dev


        self.logdebug( 'loglevel:    %s' % self.lv )
        self.logdebug( 'lineformat:  %s' % self.linefmt )
        self.logdebug( 'dateformat:  %s' % self.datefmt )

    def is_running_mayagui(self):
        """
        Tests if this is running from within maya (and not mayapy).
        (because maya's script editor handles python logs differently)


        sets self.is_maya


        This modules is used everywhere. To keep dependencies
        to a minimum implementing module's own logic rather
        than using libmaya.mayaUtils
        """

        self.is_maya = False

        python_bin  = sys.executable.replace('\\','/').split('/')[-1]

        if 'maya' in python_bin:
            if not 'mayapy' in python_bin:
                self.is_maya = True

    def create_loghandlers(self):
        """
        Creates a new loghandler, or
        if self.reuse, try to reuse an existing one.
        """

        handlers           = []

        ## Create Handlers
        if self.logfile:
            handlers.extend( self._create_loghandler_file() )

        if self.logstream:
            handlers.extend( self._create_loghandler_stream() )


        self.logdebug('using handlers: %s' % repr(handlers))
        self._set_loglevel()
        self._set_logformat( handlers )
        self._set_filters(   handlers )

    def _create_loghandler_stream(self):
        """
        Create/Modify a StreamHandler

        __NOTE__:  Maya does not use logging.StreamHandler, Autodesk replaced it with
                   something entirely different.
        """
        handlers = []


        ## Determine the handler type we are looking for
        if self.is_maya:
            from maya import utils
            streamhandler_type = utils.MayaGuiLogHandler
        else:
            streamhandler_type = logging.StreamHandler



        ## Find existing loghandlers
        create_handler = True
        if self.reuse:
            if logging.root.handlers:
                for handler in logging.root.handlers:

                    ## most handlers are subclasses of logging.StreamHandler
                    ## we need to test explicitly for logging.StreamHandler.
                    if type(handler) == streamhandler_type:
                        self.logdebug('Found Stream LogHandler: %s' % repr(handler) )
                        create_handler = False
                        handlers.append( handler )


        ## Create handler if necessary
        if create_handler:
            handler = streamhandler_type()
            logging.root.addHandler( handler )
            handlers.append( handler )
            self.logdebug('Created Stream LogHandler: %s' % repr(handler) )

        return handlers

    def _create_loghandler_file(self):
        """
        Create/Modify a file loghandler
        """
        import logging.handlers

        handlers = []


        ## create empty logfile if not exist
        if self.logfile:
            if not os.path.isdir( os.path.dirname( self.logfile ) ):
                os.makedirs( os.path.dirname(self.logfile) )

            if not os.path.isfile( self.logfile ):
                open( self.logfile, 'a' ).close()


        ## Search for existing RotatingFileHandlers
        create_handler = True
        if self.reuse:
            if logging.root.handlers:
                for handler in logging.root.handlers:

                    if isinstance( handler, logging.handlers.RotatingFileHandler ):
                        create_handler = False
                        handlers.append( handler )
                        self.logdebug('Found File LogHandler: %s' % repr(handler) )


        ## create a new handler if necessary (or configured)
        if create_handler:
            handler = logging.handlers.RotatingFileHandler( self.logfile, maxBytes=self.logfile_size, backupCount=1 )
            logging.root.addHandler( handler )
            handlers.append( handler )
            self.logdebug('Created File LogHandler: %s' % repr(handler) )


        return handlers

    def _set_loglevel(self):
        if isinstance( self.lv, six.text_type ):
            logging.root.level = getattr( logging, self.lv.upper() )
        else:
            logging.root.level = self.lv

    def _set_logformat( self, handlers ):

        logformat = logging.Formatter(
                fmt      = self.linefmt,
                datefmt  = self.datefmt,
            )

        for handler in handlers:
            handler.setFormatter( logformat )

    def _set_filters( self, handlers ):

        if self.filter_type and self.filter_matches:
            for handler in handlers:

                ## Delete existing filter(s)
                for _filter in handler.filters:
                    handler.removeFilter( _filter )

                ## Add the user-defined filter
                handler.addFilter(
                            self.filter_type( self.filter_matches )
                        )

    def colorize_log(self):
        """
        If user wants colorized logs, choose the most
        appropriate method of colorizing logs.
        """

        if self.colorize:
            colorama.init()
            logging.StreamHandler.emit = self._add_color_ANSI(logging.StreamHandler.emit)

    def _add_color_ANSI(self,fn):
        """
        Adds colour to logs in terminal using ansi escape sequences.
        (shamelessly borrowed from unutbu/sorin on stack-overflow)
        """
        def new(*args):
            levelno = args[1].levelno
            if(levelno>=50):
                color = '\x1b[31m' # red
            elif(levelno>=40):
                color = '\x1b[31m' # red
            elif(levelno>=30):
                color = '\x1b[33m' # yellow
            elif(levelno>=20):
                color = '\x1b[32m' # green
            elif(levelno>=10):
                color = '\x1b[35m' # pink
            else:
                color = '\x1b[0m' # normal
            args[1].msg = color + args[1].msg +  '\x1b[0m'  # normal
            return fn(*args)
        return new

    def logdebug( self, msg ):
        """
        Provides a means of debugging the logsetup (before you have a log in place)
        """
        if self.debug_mode:
            print( 'loggingTools.SetLog: %s' % msg )




if __name__ == '__main__':
    pass

