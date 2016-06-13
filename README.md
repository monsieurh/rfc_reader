# rfc_reader
The CLI RFC reader :
- Open any published RFC with your favorite program
- Quickly search through RFC summaries with `rfc -k <keyword>`
- Full offline access `~/.rfc/`

## Installation :
Either clone the repo and run 
```shell
python setup.py install
```
or simply use pip :
```shell
pip install rfc_reader
```

## Usage : 
Type `rfc -h` or `rfc --help` to invoke the following help :

```shell
usage: rfc [-h] [--update] [--pager PAGER] [-k KEYWORD] [--version]
           [RFC_NUMBER]

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
  -k KEYWORD, --keyword KEYWORD
                        Prints the summary of all known RFC documents matching
                        the keyword and exits
  --version             show program's version number and exit

Released under GPLv3


```

## Behavior :
rfc_reader will download and/or update all RFC txt documents from [rfc-editor-website](https://www.rfc-editor.org/) and store them in `~/.rfc/`. 

## Examples :
`rfc 2119` opens the Key words RFC in the default `$PAGER` program (usually `less`)

`rfc -p gedit 2119` opens the same document in gedit

`rfc -k UDP` outputs the summary of all RFC documents including the word 'UDP'
