import os
import shutil
import unittest

from rfc.rfc import RFCDownloader


class TestDownloader(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.downloader = RFCDownloader()
        self.remove_data()
        RFCDownloader.STORAGE_PATH = "/tmp/rfc_python_test/"
        RFCDownloader.RFC_BULK = "https://www.rfc-editor.org/in-notes/tar/RFCs0001-0500.tar.gz"  # So we don't actually download the whole BULK file

    @staticmethod
    def remove_data():
        full_path = os.path.expanduser(RFCDownloader.STORAGE_PATH)
        if os.path.exists(full_path):
            shutil.rmtree(full_path)

    def test_internet_connection(self):
        self.assertTrue(self.downloader.is_connected(), "No internet connection, cannot continue tests")

    def test_data_available(self):
        self.assertFalse(self.downloader.is_data_present(), "Data shouldn't be present on the system at this point")
        self.downloader.update_bulk()
        self.assertTrue(self.downloader.is_data_present(), "Data should be present")


if __name__ == "__main__":
    unittest.main()
