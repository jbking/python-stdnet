import os

from stdnet import test, getdb
from stdnet.apps.pubsub import Publisher, Subscriber

from .backend import DummyBackendDataServer


class TestPubSub(test.TestCase):
    
    def server(self):
        return getdb(self.backend.connection_string)
        
    def subscriber(self):
        s = Subscriber(self.server())
        self.assertTrue(s.server)
        return s
    
    def publisher(self):
        s = Publisher(self.server())
        self.assertTrue(s.server)
        return s
    
    def setUp(self):
        self.s = self.subscriber()
        self.p = self.publisher()
    
    def tearDown(self):
        self.s.unsubscribe()
        self.s.punsubscribe()
        
    def testDummy(self):
        p = DummyBackendDataServer('','')
        self.assertRaises(NotImplementedError, p.publish, '', '')
        
    def testClasses(self):
        s = self.subscriber()
        s = self.publisher()
        
    def testOneMessage(self):
        p = self.p
        s = self.s
        self.assertEqual(s.subscribe('test'), [b'subscribe', b'test', 1])
        self.assertEqual(s.subscription_count(), 1)
        self.assertEqual(p.publish('test', 'hello world!'), 1)
        res = list(s.pool(1))
        self.assertEqual(len(res), 1)
        data = s.get_all()
        self.assertEqual(data['test'],['hello world!'])
        