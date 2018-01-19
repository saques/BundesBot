import unittest
import requests
import random
from datetime import datetime
from bs4 import BeautifulSoup

class BotTest(unittest.TestCase):

    FMT = '%H:%M:%S'

    def test_upper(self):

        current = datetime.strptime("19:00:00", self.FMT)
        tgt = datetime.strptime("19:00:20", self.FMT)

        self.assertEqual((tgt-current).total_seconds(), 20)

    def test_greater(self):

        current = datetime.strptime("19:00:00", self.FMT)
        tgt = datetime.strptime("18:00:00", self.FMT)

        if current > tgt:
            tgt = tgt.replace(day=2)

        self.assertEqual((tgt-current).total_seconds(), 82800)



if __name__ == '__main__':
    unittest.main()