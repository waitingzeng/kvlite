import sys
if '' not in sys.path:
    sys.path.append('')
sys.path.append('..')

import unittest

import kvlite 
from kvlite import SqliteCollection
from kvlite import SqliteCollectionManager

from kvlite import cPickleSerializer
from kvlite import CompressedJsonSerializer

class KvliteSqliteTests(unittest.TestCase):

    def setUp(self):
        URI = 'sqlite:///tmp/testdb.sqlite'

        self.collection_name = 'kvlite_test'
        self.manager = SqliteCollectionManager(URI)
        
        if self.collection_name not in self.manager.collections():
            self.manager.create(self.collection_name)
            
        collection_class = self.manager.collection_class
        self.collection = collection_class(self.manager, self.collection_name)

    def tearDown(self):
        
        if self.collection_name in self.manager.collections():
            self.manager.remove(self.collection_name)
        self.collection.close()
    
    def test_put_get_delete_count_one(self):
        
        k = self.collection.get_uuid()
        v = 'test_put_one'
        self.collection.put(k, v)
        self.assertEqual(self.collection.get(k), v)
        self.assertEqual(self.collection.count, 1)
        self.collection.delete(k)
        self.assertEqual(self.collection.count, 0)
        self.collection.commit()

    def test_put_get_delete_count_many(self):
        
        ks = list()
        for i in xrange(100):
            k = self.collection.get_uuid()
            v = 'test_{}'.format(i)
            self.collection.put(k, v)
            ks.append(k)
        
        kvs = [kv[0] for kv in self.collection.items()]
        self.assertEqual(len(kvs), 100)

        kvs = [kv for kv in self.collection.keys()]
        self.assertEqual(len(kvs), 100)

        self.assertEqual(self.collection.count, 100)
        for k in ks:
            self.collection.delete(k)
        self.assertEqual(self.collection.count, 0)
        self.collection.commit()

    def test_long_key(self):
        
        self.assertRaises(RuntimeError, self.collection.get, '1'*256)
        self.assertRaises(RuntimeError, self.collection.put, '1'*256, 'long_key')
        self.assertRaises(RuntimeError, self.collection.delete, '1'*256)

    def test_use_different_serializators(self):
        URI = 'sqlite:///tmp/testdb.sqlite'
        collection_name = 'diffser'

        manager = SqliteCollectionManager(URI)
        if collection_name not in manager.collections():
            manager.create(collection_name)

        collection_class = manager.collection_class
        collection = collection_class(manager, collection_name, CompressedJsonSerializer)
        
        collection.put(u'1', u'diffser')
        collection.commit()
        collection.close()

        manager = SqliteCollectionManager(URI)
        collection_class = manager.collection_class
        collection = collection_class(manager, collection_name, cPickleSerializer)
        
        self.assertRaises(RuntimeError, collection.get, u'1')
        collection.put(u'1', u'diffser')
        collection.commit()
        collection.close()

        manager = SqliteCollectionManager(URI)
        collection_class = manager.collection_class
        collection = collection_class(manager, collection_name, CompressedJsonSerializer)
        
        self.assertRaises(RuntimeError, collection.get, u'1')
        collection.close()

    def test_use_different_serializators_for_many(self):
        URI = 'sqlite:///tmp/testdb.sqlite'
        collection_name = 'diffser'

        manager = SqliteCollectionManager(URI)
        if collection_name not in manager.collections():
            manager.create(collection_name)

        collection_class = manager.collection_class
        collection = collection_class(manager, collection_name, CompressedJsonSerializer)
        
        collection.put(u'1', u'diffser1')
        collection.put(u'2', u'diffser2')
        collection.put(u'3', u'diffser3')
        collection.commit()
        collection.close()

        manager = SqliteCollectionManager(URI)
        collection_class = manager.collection_class
        collection = collection_class(manager, collection_name, cPickleSerializer)
        with self.assertRaises(RuntimeError):
            res = [(k,v) for k,v in collection.items()]
        
        collection.put(u'1', u'diffser1')
        collection.put(u'2', u'diffser2')
        collection.put(u'3', u'diffser3')
        collection.commit()
        collection.close()

        manager = SqliteCollectionManager(URI)
        collection_class = manager.collection_class
        collection = collection_class(manager, collection_name, CompressedJsonSerializer)
        
        with self.assertRaises(RuntimeError):
            res = [(k,v) for k,v in collection.items()]
        collection.close()


    def test_incorrect_key(self):
        
        self.assertRaises(RuntimeError, self.collection.get, (1,2,3))        
        
if __name__ == '__main__':
    unittest.main()        

