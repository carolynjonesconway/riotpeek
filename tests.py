import server, unittest, doctest


def load_tests(loader, tests, pattern):
    """Also run our doctests and file-based doctests."""

    tests.addTests(doctest.DocTestSuite(server))
    tests.addTests(doctest.DocFileSuite("tests.txt"))
    return tests

class IntegrationTestCase(unittest.TestCase):
    def test_home(self):
        test_client = server.app.test_client()
        result = test_client.get('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn('<h1>RiotPeek</h1>', result.data)


if __name__ == "__main__":    
    unittest.main()