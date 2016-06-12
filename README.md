# rfc_reader
The CLI RFC reader for linux :
- Allows one to update a list of local RFC documents
- Allows to open a RFC with any given program (default: `$PAGER` or `less`)


## Usage : (`rfc --help` or `rfc -h` to invoke)
```shell
usage: rfc [-h] [--update] [--pager PAGER] RFC_NUMBER

rfc is the python RFC reader. It stores a local copy of all the RFC documents
and allows one to search a read through them.For more info and contact : See
https://github.com/monsieurh/rfc_reader

positional arguments:
  RFC_NUMBER            Opens the RFC_NUMBER for reading

optional arguments:
  -h, --help            show this help message and exit
  --update              Updates the local copy of RFC documents with the
                        latest (weekly) publication of the IETF
  --pager PAGER, -p PAGER
                        Uses the given program to open RFC documents. Default
                        program is env var $PAGER or `less` if not found

Released under GPLv3

```

## Behavior :
rfc_reader will download and/or update all RFC txt documents in `~/.rfc`. 

The program then allows to open a RFC document by invoking :

`rfc <number>` where <number> is the identifier of the RFC.

or :
`rfc -p <program> <number>` so the docment is opened by <program>

## Examples :
`rfc 2119` opens the Key words RFC in the default `$PAGER` program (usually `less`)

`rfc -p gedit 2119` opens the same document in gedit

## Future :
- Keyword and title based searches and filters
- Scheduled updates (as opposed to manual)