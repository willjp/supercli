
TODO
====

* create a cli-flag --fullhelp that displays --help
  without removing the hidden arguments

* logging.SetLog() needs a modular way of setting
  logs in different environments (like maya, mayapy, etc)

* Logging.WhiteList should use fnmatch on the path/func like
  logging does.

* Whitelist/Blacklist must be able to be used together.

* unittests

* look into bash autocompletion scripts

* after reading up on bash autocompletion, make use of nargs,
  and introduce a new add_argument() option that determines
  the type of argument that it expects.

  file, normal, internet iface, etc.
  ZSH has all of this, I'm not sure about other shells..


