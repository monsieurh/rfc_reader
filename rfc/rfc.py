#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import os
import re
import shutil
import sys
import tarfile

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

__version__ = "1.0"


class Config(object):
    LOCAL_STORAGE_PATH = os.path.expanduser(os.getenv('XDG_DATA_HOME', "~/.local/share/rfc"))
    INDEX_NAME = "rfc-index.txt"


class RFCIndexReader(object):
    START_LINE_REGEX = re.compile("^[0-9]+")

    def __init__(self):
        self._path = os.path.join(Config.LOCAL_STORAGE_PATH, Config.INDEX_NAME)
        self.kb = set()
        self._parse_index()

    def _parse_index(self):
        docstring = None
        with open(self._path) as opened_file:
            for line in opened_file:
                if self._is_start_line(line):
                    if docstring:  # If there was no separation line with the previous entry
                        self._register_index(docstring)
                    docstring = line

                elif self._is_end_line(line) and docstring:
                    self._register_index(docstring)
                    docstring = None

                elif self._is_content_line(line) and docstring:
                    docstring += line

            if docstring:  # If the index doesn't end with an empty line
                self._register_index(docstring)

    def _register_index(self, docstring):
        self.kb.add(RFCDocument(docstring))

    def _is_start_line(self, line):
        return self.START_LINE_REGEX.match(line)

    @staticmethod
    def _is_end_line(line):
        return len(line) <= 2  # CR, LF, or both

    def _is_content_line(self, line):
        return not self._is_end_line(line) and not self._is_start_line(line)

    def find(self, keyword):
        return [doc for doc in self.kb if doc.contains(keyword)]


class RFCDocument(object):
    ID_REGEX = re.compile("^[0-9]+")

    def __init__(self, index_string):
        self.desc = index_string
        self.id = self._parse_id()

    def _parse_id(self):
        return int(self.ID_REGEX.findall(self.desc)[0])

    def contains(self, search_string):
        return search_string.lower() in self.desc.lower()

    def __str__(self):
        return self.desc


class RFCDownloader(object):
    RFC_HOME = "http://www.rfc-editor.org"
    RFC_BULK = "https://www.rfc-editor.org/in-notes/tar/RFC-all.tar.gz"
    RFC_INDEX = "https://www.ietf.org/download/rfc-index.txt"

    def update(self):
        full_path = Config.LOCAL_STORAGE_PATH
        if os.path.exists(full_path):
            shutil.rmtree(full_path)
        os.mkdir(full_path)
        self._update_bulk(full_path)
        self._update_index(full_path)

    def _update_bulk(self, full_path):
        self._download_file(self.RFC_BULK, full_path)
        self._uncompress_bulk_file()

    def _update_index(self, full_path):
        self._download_file(self.RFC_INDEX, full_path)

    def is_connected(self):
        # noinspection PyBroadException
        try:
            urlopen(self.RFC_HOME)
            return True
        except Exception:
            return False

    @staticmethod
    def is_data_present():
        return os.path.exists(Config.LOCAL_STORAGE_PATH) and len(os.listdir(Config.LOCAL_STORAGE_PATH)) > 0

    @staticmethod
    def _download_file(url, dest):
        print("Downloading %s" % url)
        file_name = url.split('/')[-1]
        u = urlopen(url)
        f = open(os.path.join(dest, file_name), 'wb')
        meta = u.info()
        file_size = RFCDownloader._find_content_len(meta)

        print("{0} : {1:.2f}MB".format(file_name, file_size/1024/1024))

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"[%3.2f%%]" % (file_size_dl * 100. / file_size)
            status += chr(8) * (len(status) + 1)
            print(status, end="\r")
        f.close()

    @staticmethod
    def _find_content_len(meta):
        """
        Handles urllib/urllib2 compatibility
        :return: size of the file in bytes
        :rtype: int
        """

        if hasattr(meta, '_headers'):
            file_size = 1
            # noinspection PyProtectedMember
            for header in meta._headers:
                if header[0] == "Content-Length":
                    file_size = int(header[1])
                    break

        elif hasattr(meta, "getheaders") and meta.getheaders('Content-Length'):
            file_size = int(meta.getheaders("Content-Length")[0])

        else:
            file_size = 1

        return file_size

    def _uncompress_bulk_file(self):
        print("Extracting archive")
        file_name = self.RFC_BULK.split('/')[-1]
        archive_path = os.path.join(Config.LOCAL_STORAGE_PATH, file_name)
        with tarfile.open(archive_path) as tar_file:
            for tar_file_member in tar_file.getmembers():
                if tar_file_member.name.endswith('.txt'):
                    self._uncompress_file_member(tar_file, tar_file_member)
        os.remove(archive_path)

    def _uncompress_file_member(self, tar_file, tar_file_member):
        contents = tar_file.extractfile(tar_file_member)
        with open(os.path.join(Config.LOCAL_STORAGE_PATH, os.path.basename(tar_file_member.name)), 'wb') as handle:
            handle.write(contents.read())


class RFCNotFoundException(Exception):
    pass


class NoRFCFound(Exception):
    pass


class RFCReader(object):
    FILE_REGEX = re.compile("rfc[0-9]+\.txt")
    NUM_REGEX = re.compile('\d+')

    def __init__(self, pager=None):
        self._path = Config.LOCAL_STORAGE_PATH
        self._known_documents_ids = set()
        self._scan()
        self._pager = self._get_pager(pager)
        if len(self._known_documents_ids) == 0:
            raise NoRFCFound()

    def is_available(self, rfc_number):
        return rfc_number in self._known_documents_ids

    def open(self, rfc_number):
        if not self.is_available(rfc_number):
            raise RFCNotFoundException("RFC %d not found" % rfc_number)
        os.path.join(self._path)
        os.system("{} {}".format(self._pager, self._get_file_path(rfc_number)))

    def _scan(self):
        if not os.path.exists(self._path):
            return
        for file_name in os.listdir(self._path):
            if self.FILE_REGEX.match(file_name):
                for num in self.NUM_REGEX.findall(file_name):
                    self._known_documents_ids.add(int(num))

    def _get_file_path(self, rfc_number):
        return os.path.join(self._path, "rfc%d.txt" % rfc_number)

    @staticmethod
    def _get_pager(param_pager):
        if param_pager is not None:
            return param_pager

        system_pager = os.getenv("PAGER", None)
        if system_pager is not None:
            return system_pager

        return "less -r -s"  # Default pager


class RFCApp(object):
    def __init__(self, pager=None):
        try:
            self.reader = RFCReader(pager)
        except NoRFCFound:
            print("No RFC documents found !", file=sys.stderr)
            self._update_docs()
            self.reader = RFCReader(pager)

    def open_rfc(self, rfc_number):
        try:
            self.reader.open(rfc_number)
        except RFCNotFoundException:
            print("RFC number %d not found, check your input or re-run with the --update flag" % rfc_number,
                  file=sys.stderr)

    def search(self, keyword):
        index = RFCIndexReader()
        rfc_summaries = index.find(keyword)
        return sorted([doc for doc in rfc_summaries if self.reader.is_available(doc.id)], key=lambda doc: doc.id)

    def update(self):
        print("Downloading full archive from IETF site...")
        self._update_docs()

    @staticmethod
    def _update_docs():
        downloader = RFCDownloader()
        if not downloader.is_connected():
            print("No internet connection to update, exiting...", file=sys.stderr)
            exit_wrapper(-1)
        else:
            downloader.update()


def exit_wrapper(ret_code=0):
    exit(ret_code)


def main(arguments=None):
    parser = argparse.ArgumentParser(
        description="%(prog)s is the python RFC reader. "
                    "It stores a local copy of all the RFC "
                    "documents and allows one to search a read through them."
                    "For more info and contact : See https://github.com/monsieurh/rfc_reader",
        epilog="Released under GPLv3")
    parser.add_argument("--update", required=False, default=False, action='store_true',
                        help="Updates the local copy of RFC documents with the latest (weekly) publication of the IETF")

    parser.add_argument(metavar='RFC_NUMBER', type=int, nargs="?", dest="RFC_NUMBER",
                        help="Opens the RFC_NUMBER for reading")

    parser.add_argument("--pager", "-p", nargs=1, dest="pager", required=False, default=None,
                        help="Uses the given program to open RFC documents. "
                             "Default program is env var $PAGER or `less` if not found")

    parser.add_argument("-k", "--keyword", dest="keyword",
                        help="Prints the summary of all known RFC documents matching the keyword and exits")

    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))

    config = parser.parse_args(args=arguments)

    pager = config.pager[0] if config.pager else None

    app = RFCApp(pager)
    if config.update:
        app.update()

    if config.keyword:
        for doc in app.search(config.keyword):
            print(doc)

    if config.RFC_NUMBER:
        app.open_rfc(config.RFC_NUMBER)

    exit_wrapper(0)


if __name__ == "__main__":
    main()
