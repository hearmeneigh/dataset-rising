import unittest

from database.entities.post import PostEntity
from dataset.utils.balance import balance_selections
from dataset.utils.selection_source import SelectionSource


class BalanceTestCase(unittest.TestCase):
    def test_single_file(self):
        posts = [PostEntity(), PostEntity(), PostEntity()]

        s = SelectionSource('/some/file:*', skip_load=True)
        s.posts = posts
        balance_selections([s])
        self.assertEqual(len(s.posts), 3)

        s = SelectionSource('/some/file:100%', skip_load=True)
        s.posts = posts
        balance_selections([s])
        self.assertEqual(len(s.posts), 3)

        s = SelectionSource('/some/file', skip_load=True)
        s.posts = posts
        balance_selections([s])
        self.assertEqual(len(s.posts), 3)

    def test_multiple_files_wildcard(self):
        s1 = SelectionSource('/some/file:*', skip_load=True)
        s2 = SelectionSource('/some/file2:*', skip_load=True)

        s1.posts = [PostEntity() for _ in range(10)]
        s2.posts = [PostEntity() for _ in range(15)]

        balance_selections([s1, s2])

        self.assertEqual(s1.ratio, 0.4)
        self.assertEqual(s2.ratio, 0.6)
        self.assertEqual(len(s1.posts), 10)
        self.assertEqual(len(s2.posts), 15)

    def test_multiple_files_fixed(self):
        s1 = SelectionSource('/some/file:20%', skip_load=True)
        s2 = SelectionSource('/some/file2:80%', skip_load=True)

        s1.posts = [PostEntity() for _ in range(10)]
        s2.posts = [PostEntity() for _ in range(15)]

        balance_selections([s1, s2])

        self.assertEqual(s1.ratio, 0.2)
        self.assertEqual(s2.ratio, 0.8)
        self.assertEqual(len(s1.posts), 4)
        self.assertEqual(len(s2.posts), 15)

    def test_multiple_files_wildcard_and_percentage(self):
        s1 = SelectionSource('/some/file:20%', skip_load=True)
        s2 = SelectionSource('/some/file2:*', skip_load=True)
        s3 = SelectionSource('/some/file3:15%', skip_load=True)

        s1.posts = [PostEntity() for _ in range(10)]
        s2.posts = [PostEntity() for _ in range(25)]
        s3.posts = [PostEntity() for _ in range(15)]

        balance_selections([s1, s2, s3])

        self.assertEqual(s1.ratio, 0.2)
        self.assertEqual(s2.ratio, 0.65)
        self.assertEqual(s3.ratio, 0.15)
        self.assertEqual(len(s1.posts), 8)
        self.assertEqual(len(s2.posts), 25)
        self.assertEqual(len(s3.posts), 6)

    def test_multiple_files_wildcard_and_nothing(self):
        s1 = SelectionSource('/some/file:*', skip_load=True)  # dynamic
        s2 = SelectionSource('/some/file2:*', skip_load=True)  # dynamic
        s3 = SelectionSource('/some/file3', skip_load=True)  # unknown

        s1.posts = [PostEntity() for _ in range(10)]
        s2.posts = [PostEntity() for _ in range(25)]
        s3.posts = [PostEntity() for _ in range(15)]

        balance_selections([s1, s2, s3])

        self.assertEqual(s1.ratio, 0.2)
        self.assertEqual(s2.ratio, 0.5)
        self.assertEqual(s3.ratio, 0.3)
        self.assertEqual(len(s1.posts), 10)
        self.assertEqual(len(s2.posts), 25)
        self.assertEqual(len(s3.posts), 15)

    def test_multiple_files_wildcard_and_nothing_2(self):
        s1 = SelectionSource('/some/file', skip_load=True)
        s2 = SelectionSource('/some/file2:*', skip_load=True)
        s3 = SelectionSource('/some/file3', skip_load=True)

        s1.posts = [PostEntity() for _ in range(10)]
        s2.posts = [PostEntity() for _ in range(25)]
        s3.posts = [PostEntity() for _ in range(15)]

        balance_selections([s1, s2, s3])

        self.assertEqual(s1.ratio, 0.2)
        self.assertEqual(s2.ratio, 0.5)
        self.assertEqual(s3.ratio, 0.3)
        self.assertEqual(len(s1.posts), 10)
        self.assertEqual(len(s2.posts),  25)
        self.assertEqual(len(s3.posts), 15)

    def test_multiple_files(self):
        s1 = SelectionSource('/some/file', skip_load=True)
        s2 = SelectionSource('/some/file2', skip_load=True)

        s1.posts = [PostEntity() for _ in range(10)]
        s2.posts = [PostEntity() for _ in range(25)]

        balance_selections([s1, s2])

        self.assertAlmostEqual(s1.ratio, 0.2857, places=4)
        self.assertAlmostEqual(s2.ratio, 0.71428571, places=4)
        self.assertEqual(len(s1.posts), 10)
        self.assertEqual(len(s2.posts),  25)

