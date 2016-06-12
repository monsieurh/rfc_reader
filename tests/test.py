import os
import shutil
import unittest

from rfc.rfc import RFCDownloader, Config, RFCSearcher


def touch(fname, times=None):
    """
    Utility function
    """
    with open(fname, 'a'):
        os.utime(fname, times)


class TestDownloader(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.downloader = RFCDownloader()
        self.remove_data()
        Config.LOCAL_STORAGE_PATH = "/tmp/rfc_python_download_test/"
        RFCDownloader.RFC_BULK = "https://www.rfc-editor.org/in-notes/tar/RFCs0001-0500.tar.gz"  # So we don't actually download the whole BULK file

    @staticmethod
    def remove_data():
        full_path = os.path.expanduser(Config.LOCAL_STORAGE_PATH)
        if os.path.exists(full_path):
            shutil.rmtree(full_path)

    def test_internet_connection(self):
        self.assertTrue(self.downloader.is_connected(), "No internet connection, cannot continue tests")

        # def test_data_available(self):
        #     self.assertFalse(self.downloader.is_data_present(), "Data shouldn't be present on the system at this point")
        #     self.downloader.update_bulk()
        #     self.assertTrue(self.downloader.is_data_present(), "Data should be present")


class TestSearch(unittest.TestCase):
    def setUp(self):
        super().setUp()
        Config.LOCAL_STORAGE_PATH = "/tmp/rfc_python_read_test/"
        local_path = Config.LOCAL_STORAGE_PATH
        if not os.path.exists(local_path):
            os.mkdir(local_path)
        for rfc_num in [40, 41, 42]:
            touch(os.path.join(local_path, "rfc%d.txt" % rfc_num))

        touch(os.path.join(local_path, "not_rfc_valid_name%d.docx" % 12))

        self.searcher = RFCSearcher(local_path)

    def test_find_available_rfc(self):
        self.assertTrue(self.searcher.is_available(40))
        self.assertTrue(self.searcher.is_available(41))
        self.assertTrue(self.searcher.is_available(42))
        self.assertFalse(self.searcher.is_available(39))
        self.assertFalse(self.searcher.is_available(12))


if __name__ == "__main__":
    unittest.main()
