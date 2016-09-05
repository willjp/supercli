#!/usr/bin/env python
"""
Name :          supercli/autocomplete.py
Created :       Sept 04 2016
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   Autocompletion script-generators for various
                languages.
________________________________________________________________________________
"""


class ZshCompleter(object):
    def __init__(self,parser,cli_command):
        ## Attributes
        self.parser         = parser
        self.subparsers_obj = parser.subparsers_obj
        self.cli_command    = cli_command


        self._validate_args()

    def _validate_args(self):
        """
        Ensures arguments will not break Execution
        """

        from . import argparsetools

        parser         = self.parser
        subparsers_obj = self.subparsers_obj
        cli_command    = self.cli_command

        #if not isinstance( parser, argparsetools.ReadbleArgumentParser ):
        #    raise TypeError(
        #        "`parser` argument must be an instance of `ReadableArgumentParser`\n"
        #        "(additional attrs/methods added to retrieve info from parser/subparsers) \n"
        #    )
        #if not isinstance( cli_command, basestring ):
        #    raise TypeError(
        #        "`cli_command` must be in the form of a string. It references the CLI command that is being completed"
        #    )
        #if not any( subparsers_obj==None, isinstace( subparsers_obj, argparsetools.ReadableArgumentParser_SubparsersProxy ) ):
        #    raise TypeError(
        #        "subparsers_obj attribute must be either Nonetype or an instance of ReadableArgumentParser_SubparsersProxy"
        #    )


    def get(self):
        """
        Generates and returns text for a complete zsh autocompletion script
        """
        parser  = self.parser
        comptxt = ''

        subparsers = self._get_subparsers()


        if subparsers:
            comptxt = self._get_comptxt_w_subparsers(subparsers)
        else:
            comptxt = self._get_comptxt_no_subparsers(parser)

        return comptxt

    def _get_subparsers(self):
        """
        Builds a dictionary of subparsers.

        ___________________________________________________________________
        OUTPUT:
        ___________________________________________________________________
            subparsers = {
                'display' : {
                                'title'    : 'display',
                                'help'     : 'commands related to displaying wallpapers',
                                'instance' : <subparser instance>,
                            }
                ...
                }
        """
        subparsers     = {}
        parser         = self.parser
        subparsers_obj = self.subparsers_obj


        if parser.subparsers_obj:
            for subparser in subparsers_obj.get_subparsers():
                info = subparser.get_info()
                subparsers[ info['title'] ] = info

        return subparsers

    def _get_comptxt_header(self):

        cli_command = self.cli_command

        now    = datetime.datetime.now()
        nowstr = now.strftime('%b %d %Y')

        comptxt = (
            '#compdef %(cli_command)s                                                                    \n'
            '########################################################################################### \n'
            '# Name :          _%(cli_command)s                                                          \n'
            '# Created :       %(nowstr)s                                                                \n'
            '# Author :        Will Pittman (readableargparse)                                           \n'
            '# Contact :       willjpittman@gmail.com                                                    \n'
            '#_________________________________________________________________________________________  \n'
            '# Description :   ZSH autocompletion script for command: "%(cli_command)s".                 \n'
            '#                                                                                           \n'
            '#                 To enabe autocompletion in zsh, add the following lines                   \n'
            '#                 to your ~/.zshrc file:                                                    \n'
            '#                                                                                           \n'
            '#                      autoload -U compinit                                                 \n'
            '#                      compinit                                                             \n'
            '#_________________________________________________________________________________________  \n'
            '########################################################################################### \n'
            '                                                                                            \n'
        ) % locals()

        return comptxt

    def _get_comptxt_w_subparsers(self,subparsers):
        """
        Generates zsh autocompletion script if
        the script uses argparse subparsers.
        """
        cli_command = self.cli_command

        comptxt  = self._get_comptxt_header()
        comptxt += '_%(cli_command)s() {                         \n' % locals()
        comptxt += '    local context state line expl implementation \n'
        comptxt += '    local -a subcmds                             \n'
        comptxt += '                                                 \n'
        comptxt += '                                                 \n'
        comptxt += '    subcmds=( %s ) \n\n' % ' '.join([ subparser for subparser in subparsers ])

        comptxt += (
            "    _arguments -C                              \\\n"
            "        {-h,--help}'[show help information]'   \\\n"
            "        '1:subcommand:compadd -a subcmds'      \\\n"
            "        '*:: :->subcmd' && return                \n"
            "                                                 \n"
            "    service=\"$words[1]\"                        \n"
            "    curcontext=\"${curcontext%:*}-$service:\"    \n"
            "                                                 \n"
            "    case $service in                             \n"
            )
        for subparser in subparsers:
            comptxt +=(
                '    (%(title)s)                             \n'
                '        _arguments -A "-*"                \\\n'
            ) % subparsers[subparser]
            comptxt += self._parse_parser_args( **subparsers[subparser], indent=12 )

        comptxt +=(
            '    (*)\n'
            '        _message "unknown sub-command: $service" \n'
            '        ;;                                       \n'
            '    esac                                         \n'
            '}                                                \n'
            '                                                 \n'
            '_%(cli_command)s "$@"                            \n'
            ) % locals()


        return comptxt

    def _parse_parser_args(self, parser_instance, title=None, help=None, indent=0):
        """
        creates zsh '_arguments' line for each flag attached to a
        parser/subparser instance
        """
        completer_lines = []
        arguments       = parser_instance._actions

        for arg in arguments:
            completer_lines.append( self._parse_argument(arg) )
        completer_lines.append( ';;\n' )

        if indent:
            completer_lines = [ ' '*indent + line     for line in completer_lines ]


        ret = '\\\n'.join( completer_lines )

        return ret

    def _parse_argument(self,arg):
        """
        Writes a single zsh autocomp '_arguments' line.
        """

        flags = arg.option_strings
        help  = self._escape_argument_conts( arg.help )

        if len(flags) > 1:
            flagstr = ','.join(flags)
            argstr  = "{"+ flagstr +"}'["+ help +"]'"%locals()
        else:
            argstr = "'"+ flags[0]  +"["+ help +"]'".format(**locals())


        #self._parse_argument_nargs(arg)
        #self._parse_argument_datatype(arg)

        return argstr

    def _escape_argument_conts(self, string ):
        string = string.replace('\n',' ')
        string = string.replace("'", "\\'")
        string = string.replace("\\", "\\\\'")
        string = string.strip()
        return string

    def _parse_argument_nargs(self,arg):
        pass

    def _parse_argument_datatype(self,arg):
        pass


    def write(self,outfile=None):
        """
        __________________________________________________________________________________________________________________
        INPUT:
        __________________________________________________________________________________________________________________
        outfile | '/usr/share/zsh/functions/Completion/Unix/_myprogram' | (opt) | the location you'd like to write your
                |                                                       |       | zsh completer script to.
                |                                                       |       | (If not supplied, saves to current directory)
        """
        cli_command = self.cli_command

        ## output location
        if not outfile:
            outfile = '_{cli_command}'.format(**loc())
        else:
            if not os.path.isdir( os.path.dirname(outfile) ):
                os.makedirs( os.path.dirname(outfile) )

        ## obtain and write autocomp
        comptxt     = self.get()
        with open( outfile, 'w' ) as fw:
            fw.write( comptxt )

        print('zsh autocompletion script written to: "%s"' % outfile )

        return comptxt

    def get_os_zshcompleter_dir(self):
        """
        You cannot access $fpath from python's os.environ, and the actual
        fpath directories vary depending on the operating system. So this is an extremely
        ackward workaround to find an $fpath location that actually exists.

        __WARNING__: This is extremely sensitive to the environment it is run in.
                     That makes using this script unpredictable. Use at your own discretion.
        """
        raw_fpath = subprocess.check_output(['zsh','-c','echo $fpath'], universal_newlines=True)
        fpath     = shlex.split( raw_fpath.strip() )

        first_existing_fpath = None
        unix_fpath           = None


        for path in fpath:
            if os.path.isdir( path ):
                if not first_existing_fpath:
                    first_existing_fpath = path
                if os.path.split( path )[-1] in ('Unix','unix'):
                    unix_fpath = path
                    break

        if unix_fpath:
            path = unix_fpath
        elif first_existing_fpath:
            path = first_existing_fpath
        else:
            raise IOError('Unable to find a location on the $fpath to save autocompletion script to')

        return path



if __name__ == '__main__':
    pass
