#!/usr/bin/env python
"""
Name :          supercli/excepttools.py
Created :       Sept 1 2016
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   A collection of tools related to handling exceptions.
________________________________________________________________________________
"""
## builtins
from   __future__    import unicode_literals
from   __future__    import absolute_import
import sys
import six
import logging

loc    = locals
logger = logging.getLogger(__name__)



_pdb_pm_registered = False
def wrap_excepthook_pdb_postmortem( force=False ):
    """
    Wraps the existing sys.excepthook, so that every time
    an unhandled exception occurs, pdb (or ipdb if available)
    starts automatically in post-mortem mode.

    concept taken from: http://stackoverflow.com/questions/8415463/adding-function-to-sys-excepthook
    """
    try:                    import ipdb as pdb
    except(ImportError):    import pdb
    global _pdb_pm_registered


    if _pdb_pm_registered and not force:
        return

    orig_excepthook = sys.excepthook

    def error_catcher( *exc_info):
        logexcept( exc_info, raise_except=False )
        pdb.pm()

    sys.excepthook = error_catcher
    _pdb_pm_registered = True

def logexcept( exc_info=None, lv='error', raise_except=True, handled=False ):
    """
    log an exception/traceback from sys.exc_info()

    _____________________________________________________________________________________
    INPUT:
    _____________________________________________________________________________________
    exc_info     | sys.exc_info()     | (opt) | the exception as obtained by sys.exc_info.
                 |                    |       |
    lv           | 'error','warn',... | (opt) | the loglevel you'd like to log the exception as
                 |                    |       |
    handled      | True/False         | (opt) | When parsing user-commands, you don't always want to
                 |                    |       | raise an exception, but printing a handled exception is misleading to the user.
                 |                    |       | This changes the log message to indicate that the exception has been handled.
                 |                    |       |
    raise_except | True/False         | (opt) | raise the exception after logging. (False by default)
                 |                    |       |
    """
    import traceback
    import sys
    import six


    ## Automatically grab exception info
    if not exc_info:
        exc_info = sys.exc_info()


    ## Change message to not mislead user
    if handled:
        msg = 'Exception Encountered and Handled: \n'
    else:
        msg = 'Unhandled Exception Encountered: \n'



    ## Log the Error (at a variable level)
    exc_txt       = repr(exc_info[1])
    str_traceback = '\n'.join(traceback.format_tb( exc_info[2] ))
    getattr( logger, lv )( '\n{msg}{str_traceback}\n{exc_txt}'.format(**loc()) )

    if raise_except:
        six.reraise( *exc_info )


if __name__ == '__main__':
    def EXAMPLES():
        import loggingTools
        loggingTools.Setlog('vo')
        try:
            raise RuntimeError('testing logging')
        except( RuntimeError ):
            logexcept( sys.exc_info(), raise_except=False )

    EXAMPLES()


