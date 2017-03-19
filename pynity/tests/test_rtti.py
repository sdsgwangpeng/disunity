import logging
import tempfile
import os
import unittest

import pynity
import pynity.rtti as rtti
import pynity.ioutils as ioutils

class TestStringTable(unittest.TestCase):

    class_id = 1
    signature = "4.6.1f1"
    hash = "0123456789abcdef"
    data = b"dummy"

    @classmethod
    def setUpClass(cls):
        logging.getLogger().setLevel(logging.ERROR)

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tdb = rtti.Database(self.tmpdir.name)
        self.tdb.version = 15
        self.tdb.order = ioutils.LITTLE_ENDIAN

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_add(self):
        self.assertRaises(rtti.TypeException, self.tdb.open, self.class_id, self.hash)
        self.assertTrue(self.tdb.add(self.data, self.class_id, self.hash))

        with self.tdb.open(self.class_id, self.hash) as fp:
            self.assertEqual(fp.read(), self.data)

    def test_add_old(self):
        self.assertRaises(rtti.TypeException, self.tdb.open_old, self.class_id, self.signature)
        self.assertTrue(self.tdb.add_old(self.data, self.class_id, self.signature))

        # direct match
        with self.tdb.open_old(self.class_id, self.signature) as fp:
            self.assertEqual(fp.read(), self.data)

        # close match
        with self.tdb.open_old(self.class_id, "4.6.1f2") as fp:
            self.assertEqual(fp.read(), self.data)

        # vague match
        with self.tdb.open_old(self.class_id, "4.6.0f1") as fp:
            self.assertEqual(fp.read(), self.data)

        # no match
        self.assertRaises(rtti.TypeException, self.tdb.open_old, self.class_id, "4.5.0f1")

    def test_add_all(self):
        path_base = os.path.dirname(__file__)
        path_resources = os.path.join(path_base, "resources", "serialized")
        path_serialized = os.path.join(path_resources, "v15_r5.2.3f1_typed.assets")

        with pynity.SerializedFile(path_serialized) as sf:
            self.assertEqual(self.tdb.add_all(sf), 29)