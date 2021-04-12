# small-tools

These are a series of scripts that I use when working with input and
output files from the
[deMon](http://www.demon-software.com/public_html/index.html) program.

- `modinp.py`
    Modifies input files by adding, changing or deleting keywords.

- `mdlocc.py`
    Manage deMon local compilations. Performs a backup of 
    `$HOME/demon/X.Y.Z/{source,object.*}` into `$HOME/demon/X.Y.Z/tags`.
    Each backup can be named or tagged. The contents of the source
    directory are used to identify the backup with a sha1 sum. A
    description may be added for better identification.
