import unittest

from rfc.rfc import RFCDownloader


class TestDownloader(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.downloader = RFCDownloader()

    def test_internet_connection(self):
        self.assertTrue(self.downloader.is_connected(), "No internet connection, cannot continue tests")

    def test_data_available(self):
        self.assertFalse(self.downloader.is_data_present(), "Data shouldn't be present on the system at this point")
        self.downloader.download_bulk()
        self.assertTrue(self.downloader.is_data_present(), "Data should be present")


if __name__ == "__main__":
    unittest.main()
