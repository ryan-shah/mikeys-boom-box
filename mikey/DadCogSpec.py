import unittest
import DadCog

class MockMessage:

    def __init__(self, author, content):
        self.author = author
        self.content = content

class MockMessageAuthor:

    def __init__(self, author):
        self.id = author
        self.bot = False

class TestDadCogMethods(unittest.TestCase):

    def test_single_quote(self):
        test_user = "josh"

        # https://www.cl.cam.ac.uk/~mgk25/ucs/quotes.html
        single_quotes = ["\u0027", "\u0060", "\u00B4", "\u2018", "\u2019"]

        test_strings = [f"I{single_quote}m a normal single quote" for single_quote in single_quotes]

        expected_string = f"Hi a normal single quote, I thought you were <@{test_user}>."
        
        mock_messages = [MockMessage(MockMessageAuthor(test_user), test_string) for test_string in test_strings]

        for mock_message in mock_messages:
            with self.subTest(mock_message=mock_message.content):
                self.assertEqual(DadCog.dadJoke(mock_message), expected_string)

    def test_punction(self):
        test_user = "test"

        punct = [".", "?", "!", ","]
        
        base_test = "I'm hungry"
        advanced_test = "I'm hungry, thirsty, and tired!"
        
        test_strings = [f"I'm hungry{char}" for char in punct]
        test_strings.append(base_test)
        test_strings.append(advanced_test)

        expected_string = f"Hi hungry, I thought you were <@{test_user}>."

        mock_messages = [MockMessage(MockMessageAuthor(test_user), test_string) for test_string in test_strings]

        for mock_message in mock_messages:
            with self.subTest(mock_message=mock_message.content):
                self.assertEqual(DadCog.dadJoke(mock_message), expected_string)

if __name__ == '__main__':
    unittest.main()