import os
import shutil
import sys
import unittest

import rfc
from rfc.rfc import Config, RFCDownloader, main, NoRFCFound


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


P_BUFFER_FILE = "/tmp/out.txt"


class TestApp(unittest.TestCase):
    def setUp(self):
        Config.LOCAL_STORAGE_PATH = "/tmp/rfc_python_test/"
        if os.path.exists(Config.LOCAL_STORAGE_PATH):
            shutil.rmtree(Config.LOCAL_STORAGE_PATH)

        self.print_buffer = None
        self._exit_value = None

        self._reset_print_buffer()
        rfc.rfc.exit_wrapper = self._exit_wrapper_override

    def test_rfc_not_found(self):
        self._create_fake_storage_folder()
        main(["42"])
        buffer = self._reset_print_buffer()
        self.assertTrue("RFC number 42 not found, check your input or re-run with the --update flag" in buffer)
        self.assertEqual(self._exit_value, 0)

    def test_keyword(self):
        self._create_fake_storage_folder()
        self._create_fake_index(Config.LOCAL_STORAGE_PATH)
        main(["-k", "RFC"])
        buffer = self._reset_print_buffer()
        self.assertTrue("RFC" in buffer)
        self.assertEqual(self._exit_value, 0)

        main(["-k", "there is no rfc with that string in the index"])
        buffer = self._reset_print_buffer()
        self.assertEqual(len(buffer), 0)
        self.assertEqual(self._exit_value, 0)

    def test_no_rfc(self):
        self.assertFalse(os.path.exists(Config.LOCAL_STORAGE_PATH))
        RFCDownloader.is_connected, self._is_connected_override = self._is_connected_override, RFCDownloader.is_connected
        RFCDownloader.RFC_BULK = "What ?"
        try:
            main(["42"])
        except Exception:
            pass
        buffer = self._reset_print_buffer()
        self.assertTrue("No RFC documents found !" in buffer)
        self.assertTrue("Downloading" in buffer)
        RFCDownloader.is_connected, self._is_connected_override = self._is_connected_override, RFCDownloader.is_connected

    def test_no_rfc_no_internet(self):
        self.assertFalse(os.path.exists(Config.LOCAL_STORAGE_PATH))
        RFCDownloader.RFC_HOME = "http://not_a_valid_url.wtf/"
        try:
            main(["42"])
        except NoRFCFound:
            pass
        buffer = self._reset_print_buffer()
        self.assertTrue("No RFC documents found !" in buffer)
        self.assertTrue("No internet connection" in buffer)
        self.assertEqual(self._exit_value, -1)

    def _get_print_buffer_content(self):
        if os.path.exists(P_BUFFER_FILE):
            with open(P_BUFFER_FILE, "r") as f:
                return f.read()

    def _reset_print_buffer(self):
        """
        Used to catch print statements to a buffer so we can check them
        """
        if self.print_buffer:
            self.print_buffer.close()

        content = self._get_print_buffer_content()
        self.print_buffer = open(P_BUFFER_FILE, "w+")
        sys.stdout = self.print_buffer
        sys.stderr = self.print_buffer
        return content

    def _is_connected_override(self):
        return True

    def _exit_wrapper_override(self, ret_code=0):
        self._exit_value = ret_code

    @staticmethod
    def _create_fake_storage_folder():
        os.mkdir(Config.LOCAL_STORAGE_PATH)
        touch(os.path.join(Config.LOCAL_STORAGE_PATH, "rfc666.txt"))

    def _create_fake_index(self, path):
        with open(os.path.join(path, Config.INDEX_NAME), "w") as index:
            index.write("42\tRFC about the answer to life, universe and everything\n")
            index.write("666\tDoomsdat RFC, do not read\n")


if __name__ == "__main__":
    unittest.main()
