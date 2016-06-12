#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import re
import sys
import tarfile
from urllib.request import urlopen


class Config(object):
    LOCAL_STORAGE_PATH = "~/.rfc"


class RFCDownloader(object):
    RFC_HOME = "http://www.rfc-editor.org"
    RFC_BULK = "https://www.rfc-editor.org/in-notes/tar/RFC-all.tar.gz"

    def update_bulk(self):
        full_path = self._get_storage_path()
        if not os.path.exists(full_path):
            os.mkdir(full_path)
        self._download_file(self.RFC_BULK, full_path)
        self._uncompress_bulk_file()

    def is_connected(self):
        try:
            urlopen(self.RFC_HOME)
            return True
        except Exception as e:
            return False

    def is_data_present(self):
        path = self._get_storage_path()
        return os.path.exists(path) and len(os.listdir(path)) > 0

    def _get_storage_path(self):
        return os.path.expanduser(Config.LOCAL_STORAGE_PATH)

    @staticmethod
    def _download_file(url, dest):
        file_name = url.split('/')[-1]
        u = urlopen(url)
        f = open(os.path.join(dest, file_name), 'wb')
        meta = u.info()
        file_size = 0
        for header in meta._headers:
            if header[0] == "Content-Length":
                file_size = int(header[1])
                break

        print("Downloading: %s Bytes: %s" % (file_name, file_size))

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
            print(status)
        f.close()

    def _uncompress_bulk_file(self):
        file_name = self.RFC_BULK.split('/')[-1]
        archive_path = os.path.join(self._get_storage_path(), file_name)
        with tarfile.open(archive_path) as tar_file:
            tar_file.extractall(self._get_storage_path())
        os.remove(archive_path)


class RFCNotFoundException(Exception):
    pass


class NoRFCFound(Exception):
    pass


class RFCSearcher(object):
    FILE_REGEX = re.compile("rfc[0-9]+\.txt")
    NUM_REGEX = re.compile('\d+')

    def __init__(self, scan_path=Config.LOCAL_STORAGE_PATH):
        super().__init__()
        self._path = os.path.expanduser(scan_path)
        self._known_documents = set()
        self._scan()
        if len(self._known_documents) == 0:
            raise NoRFCFound()

    def is_available(self, rfc_number):
        return rfc_number in self._known_documents

    def open(self, rfc_number):
        if not self.is_available(rfc_number):
            raise RFCNotFoundException("RFC %d not found" % rfc_number)
        os.path.join(self._path)
        os.system("less -s %s" % self._get_file_path(rfc_number))

    def _scan(self):
        for file_name in os.listdir(self._path):
            if self.FILE_REGEX.match(file_name):
                for num in self.NUM_REGEX.findall(file_name):
                    self._known_documents.add(int(num))

    def _get_file_path(self, rfc_number):
        return os.path.join(self._path, "rfc%d.txt" % rfc_number)


def update_docs():
    downloader = RFCDownloader()
    if not downloader.is_connected():
        print("No internet connection to update, exiting...", file=sys.stderr)
        exit(-1)
    downloader.update_bulk()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", required=False, default=False, action='store_true',
                        help="Updates the local copy of RFC documents with the latest (weekly) publication of the IETF")
    parser.add_argument(metavar='RFC_NUMBER', type=int, nargs=1, dest="RFC_NUMBER",
                        help="Opens the RFC_NUMBER for reading")
    # TODO: Handle this
    # parser.add_argument("--pager", "-p")

    config = parser.parse_args()

    if config.update:
        update_docs()

    try:
        reader = RFCSearcher()
    except NoRFCFound:
        print("No RFC documents found, downloading full archive from IETF site...", file=sys.stderr)
        update_docs()

    finally:
        number = config.RFC_NUMBER[0]
        try:
            # noinspection PyUnboundLocalVariable
            reader.open(number)
        except RFCNotFoundException:
            print("RFC number %d not found, check your input or re-run with the --update flag" % number,
                  file=sys.stderr)