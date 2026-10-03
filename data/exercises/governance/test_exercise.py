"""Local authorization/cache contract only; not an Azure RBAC or ACL test."""

import unittest

from exercise import read_document


class AccessPractice(unittest.TestCase):
    def setUp(self):
        self.grants = {"public-policy": {"contoso-a", "contoso-b"}, "restricted-quote": {"contoso-a"}}
        self.cache = {}

    def test_allowed_user(self):
        self.assertIn("restricted", read_document("contoso-a", "restricted-quote", self.grants, self.cache))

    def test_denied_user_without_cache(self):
        with self.assertRaises(PermissionError):
            read_document("contoso-b", "restricted-quote", self.grants, self.cache)

    def test_denied_user_after_cache(self):
        read_document("contoso-a", "restricted-quote", self.grants, self.cache)
        with self.assertRaises(PermissionError):
            read_document("contoso-b", "restricted-quote", self.grants, self.cache)

    def test_revocation_after_cache(self):
        read_document("contoso-a", "restricted-quote", self.grants, self.cache)
        self.grants["restricted-quote"].remove("contoso-a")
        with self.assertRaises(PermissionError):
            read_document("contoso-a", "restricted-quote", self.grants, self.cache)

    def test_shared_public_document(self):
        first = read_document("contoso-a", "public-policy", self.grants, self.cache)
        self.assertEqual(first, read_document("contoso-b", "public-policy", self.grants, self.cache))


if __name__ == "__main__":
    unittest.main()
