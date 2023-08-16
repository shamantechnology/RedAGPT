"""
WIFI class testing 
"""

import unittest
from tools.wifi import WIFI
from dotenv import load_dotenv

class WIFITest(unittest.TestCase):
    def test_wifi(self):
        # load API keys
        load_dotenv()

        wifi_obj = WIFI()
        wifi_obj.run()
        self.assertIsNotNone(wifi_obj.autogpt_resp)

if __name__ == '__main__':
    unittest.main()