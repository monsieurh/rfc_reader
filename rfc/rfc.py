#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from urllib.request import urlopen


class RFCReader(object):
    pass


class RFCDownloader(object):
    RFC_HOME = "http://www.rfc-editor.org"
    RFC_BULK = "https://www.rfc-editor.org/in-notes/tar/RFC-all.tar.gz"
    STORAGE_PATH = "~/.rfc"

    def download_bulk(self):
        full_path = self._get_storage_path()
        if not os.path.exists(full_path):
            os.mkdir(full_path)

    def is_connected(self):
        try:
            urlopen(self.RFC_HOME)
            return True
        except Exception as e:
            return False

    def is_data_present(self):
        return os.path.exists(self._get_storage_path())

    def _get_storage_path(self):
        return os.path.expanduser(self.STORAGE_PATH)


class RFCSearcher(object):
    pass
