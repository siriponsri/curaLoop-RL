"""Offline safety smoke tests. Run: python -m unittest scripts.test_fetch_oa_papers"""
import unittest
from scripts.fetch_oa_papers import permission_ok, official_url, valid_pdf


class DownloaderTests(unittest.TestCase):
    def test_license(self):
        self.assertTrue(permission_ok('CC BY'))
        self.assertTrue(permission_ok('CC BY 4.0'))
        self.assertTrue(permission_ok('CC0'))
        self.assertFalse(permission_ok('All rights reserved'))
        self.assertFalse(permission_ok('CC BY-NC'))
        self.assertTrue(permission_ok('CC BY-NC', include_nc=True))
        self.assertFalse(permission_ok('CC BY-NC-ND', include_nc=True))
        self.assertFalse(permission_ok('CC BY-SA 4.0'))
        self.assertFalse(permission_ok('CC BY-ND 4.0'))
        self.assertFalse(permission_ok('CC BY-NC-SA 4.0', include_nc=True))
        self.assertFalse(permission_ok('CC BY-UNKNOWN'))

    def test_ftp_to_https(self):
        url = '/ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_pdf/01/02/example.pdf'
        self.assertEqual(official_url(url), 'https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_pdf/01/02/example.pdf')
        with self.assertRaises(ValueError):
            official_url('https://unknown.example/a.pdf')

    def test_pdf_signature(self):
        self.assertFalse(valid_pdf(b'<html>unavailable</html>'))
        self.assertTrue(valid_pdf(b'%PDF-1.4' + b' ' * 2100 + b'%%EOF'))


if __name__ == '__main__':
    unittest.main()
