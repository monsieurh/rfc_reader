#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import tarfile
from urllib.request import urlopen


class RFCReader(object):
    pass


class RFCDownloader(object):
    RFC_HOME = "http://www.rfc-editor.org"
    RFC_BULK = "https://www.rfc-editor.org/in-notes/tar/RFC-all.tar.gz"
    STORAGE_PATH = "~/.rfc"

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
        return os.path.expanduser(self.STORAGE_PATH)

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


class RFCSearcher(object):
    pass
