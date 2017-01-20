# vim: ft=rst
Version History
===============

0.0.a1:  
-------
   * first commit

0.0.a2:  
-------
   * corrections to setup.py 
     * so works under windows.
     * so packages can be installed from pypi package
       in addtion to from source.
 
0.0.a3:
-------
   * BREAKS COMPATIBILITY WITH PREVIOUS VERSIONS

   * updated documentation to better demonstrate how to use library.
     ex:
     `import supercli.logging` instead of `from supercli.logging import SetLog`
     This keeps it obvious which modules these are wrapping.

   * `autocomplete.get_zsh_completionpath` changed to `get_zsh_completer_dir`.
     now uses `$fpath` to find the standardized `functions/Completion/Unix`
     instead of trying to find bsd/archlinux specific locations.

   * CLI interface changes:
     * `--log-file`           >> `--logfile`
     * `--logfile-only`       >> `--silent`
     * `--log-longformat`     >> `--log-longfmt`
     * `--regen-autocomplete` >> `--gen-autocomp`
   
   * `--regen-autocompletion` >> `--gen-autocomp` no longer allows you to set the command-name to autocomplete.
     as an argument. Instead it accepts a list of completers to generate (no arguments),
     or allows you to specify exactly what types of autocompleters to use.

   * `argparse.ArgumentParser()__init__()` s argument: `cli_commandname` has been
     renamed to `autocomp_cmd`


0.0.a4:
-------
   * loglevel can be set with an integer


