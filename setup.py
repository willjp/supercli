#!/usr/bin/env python
from distutils.core import setup, Extension, Command
import setuptools
import os
import sys
import re
import shutil
import fnmatch
import logging

loc    = locals
logger = logging.getLogger(__name__)

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


class Configure( object ):
    """
    Collects information to be used by setuptools setup() function
    """
    def __init__(self, pkgname):
        """
        version_history:
            0.1.0:     first-release
        """
        self._pkgname      = pkgname
        self._pkgpath      = None     ## path to directory containing setup.py
        self._package_data = {}       ## setup.py's package_data variable
        self._pkgversion   = None     ## package's version (according to __init__.py's '__version__')
        self.__version__   = '0.1.0'  ## this class's version-num
        self.main()

    def main(self):
        self._get_pkgpath()
        self._get_pkg_version()

    def _get_pkgpath(self):
        """ returns path to directory containing setup.py
        (unable to use path to determine package-name, tox uses non-standard path-names) """
        cwd     = os.path.realpath(__file__).replace('\\','/')
        pkgpath = os.path.dirname( cwd ).replace('\\','/')
        pkgname = cwd.split('/')[-2]
        if '-' in pkgname:
            pkgname = '-'.join( pkgname.split('-')[:-1] )

        self._pkgpath = pkgpath

        return pkgpath

    def _get_pkg_version(self):
        """
        obtains __version__ value from package's __init__.py
        """
        pkgpath = self._pkgpath
        pkgname = self._pkgname
        pkginit = '{pkgpath}/{pkgname}/__init__.py'.format(**locals())

        if not os.path.isfile( pkginit ):
            raise IOError('expected __init___ file not found at: %s' % pkginit)


        with open( pkginit, 'r' ) as fr:
            for line in fr:
                if re.match( '^[ \t]*__version__[ \t]*=.*?$', line ):
                    version = re.sub( '^[ \t]*__version__[ \t]*=[ \t]*', '', line )
                    version = version.strip()
                    version = version.replace('"','')
                    version = version.replace("'",'')
                    self._pkgversion = version
                    return version
        raise RuntimeError('unable to find a value for __version__ in : %s' % pkginit )

    ## package_data
    def set_packagedata(self, package_data):
        self._package_data = package_data

    def add_packagedata(self, path=None, matches=None, recursive=False ):
        """
        Add a directory to a dictionary formatted for setuptools.setup()'s package_data
        argument.

        Due to the ackward restrictions of setuptools, each key must be a python-package
        (containing __init__.py).
        __________________________________________________________________________________________
        INPUT:
        __________________________________________________________________________________________
        matches      | ['*.rst', '*.txt', ...] |       | a list of fnmatch.fnmatch matches
                     |                         |       | to filenames you want inserted in
                     |                         |       |
        pkgpath      | 'tests'                 | (opt) | the directory relative to your srctree
                     |                         |       | that you want to add matches under.
                     |                         |       | If not provided, default is directly from
                     |                         |       | src-tree
                     |                         |       |
        recursive    | True, False             | (opt) | If you want to add files recursively
                     |                         |       |
        """
        package_data = self._package_data
        pkgname      = self._pkgname
        pkgpath      = self._pkgpath

        ## Get pkgpath
        if not path:
            path = '{pkgpath}/{pkgname}'.format(**loc())
        else:
            path = '{pkgpath}/{pkgname}/{path}'.format(**loc())


        ## Validation
        if not os.path.isdir( path ):
            raise IOError('path does not exist: "%s"' % path )

        if not hasattr( matches , '__iter__' ):
            raise TypeError('matches must be an iterable list of fnmatch style matches')



        ## Add to package_data
        if not recursive:
            relpath = self._get_relpath( path )

            if relpath not in package_data:
                package_data[ relpath ] = []
            for match in matches:
                if match not in package_data[ relpath ]:
                    package_data[ relpath ].append( match )


        elif recursive:
            nearest_python_package = path

            for (root, dirs, files) in os.walk( path, topdown=False):
                if '__init__.py' in os.listdir( root ):
                    nearest_python_package = root


                relpath   = self._get_relpath( root )
                relpath   = relpath.replace('/','.')
                match_str = '[/]*{nearest_python_package}[/]*'.format(**loc())
                match_dir = re.sub( match_str, '', root )
                #print( path )
                #print( match_dir )
                #import ipdb;ipdb.set_trace()

                #!NOTE: need to make nearest_python_package abbreviated


                for match in matches:
                    for _file in files:
                        if fnmatch.fnmatch( '{root}/{_file}'.format(**loc()), match ):

                            if nearest_python_package not in package_data:
                                package_data[ nearest_python_package ] = []

                            if match_dir:
                                match = '{match_dir}/{match}'.format(**loc())

                            if match not in package_data[ nearest_python_package ]:
                                package_data[ nearest_python_package ].append( match )

                            break

        return package_data

    def _get_relpath(self, path, nearest_pkg=None ):
        """
        returns relative path from pkgpath (dir with setup.py)

        _________________________________________________________________________________________________
        INPUT:
        _________________________________________________________________________________________________
        nearest_pkg  | '/full/path/to/python/package' | (opt) | path to the nearest python package
                     |                                |       | that the path is parented under. This part
                     |                                |       | of the path will be stripped out.
        """
        pkgpath = self._pkgpath
        pkgname = self._pkgname


        root_pkg    = '{pkgpath}/{pkgname}'.format(**loc())
        check_paths = path.replace( root_pkg, '' ).split('/')

        ## Determine the most deeply nested dir containing
        ## the file __init__.py
        nearest_pkg = root_pkg
        if check_paths:
            check_path = root_pkg
            for path_segment in check_paths:
                check_path += '/{path_segment}'.format(**loc())

                if '__init__.py' in check_path:
                    nearest_pkg = check_path



        ## Get the remaining difference between the provided
        ## path, and the root-package.
        relpath = nearest_pkg.replace( root_pkg, '' )

        if relpath != '':
            if relpath[-1] in ('/','\\'):
                relpath = relpath[ : -1]

        if relpath != '':
            if relpath[0] in ('/','\\'):
                relpath = relpath[ 1: ]


        return relpath

    ## misc
    def read(self,fname):
        """ reads a file (filepath rooted to dir containing setup.py """
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

    def summary(self):
        print('############### SUMMARY ##################')
        print('##########################################')
        print('name:         %s ' % self._pkgname )
        print('pkgpath:      %s ' % self._pkgpath)
        print('version:      %s ' % self._pkgversion )
        print('package_data: %s ' % repr(self._package_data))
        print('##########################################')
        print('##########################################')
        print('\n\n')



# =========
# configure
# =========
logging.basicConfig()
cfg = Configure( pkgname='supercli' )
#cfg.add_packagedata( '',      ['*.txt','*.rst'], recursive=True )
#cfg.add_packagedata( 'tests', ['*.py'],          recursive=True )
cfg.add_packagedata( 'examples', ['*'],          recursive=True )

cfg.summary()

setup(
    name         = cfg._pkgname,
    version      = cfg._pkgversion,
    author       = 'Will Pittman',
    author_email = 'willjpittman@gmail.com',
    url          = 'https://github.com/willjp/supercli',
    license      = 'BSD',

    description      = 'Toolkit to quickly create readable, user-friendly CLI interfaces with automatic shell-autocompletion',
    long_description = cfg.read('README.rst'),

    keywords         = 'supercli cli color colour argparse logging interface',
    install_requires = ['colorama','pygments','six'],
    packages         = setuptools.find_packages(),
    zip_safe         = False,
    #include_package_data = True,

    package_data     = cfg._package_data,
    cmdclass         = { 'clean': CleanCommand  },

    classifiers      = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',

        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: BSD',
    ],
)

