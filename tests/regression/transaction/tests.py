import random

import stdnet
from stdnet import test, orm
from examples.models import SimpleModel, Dictionary
from stdnet.utils import populate

LEN = 100
names = populate('string',LEN, min_len = 5, max_len = 20)


class TestTransactions(test.TestCase):
    
    def setUp(self):
        self.orm.register(SimpleModel)
    
    def unregister(self):
        self.orm.unregister(SimpleModel)
        
    def testSave(self):
        with SimpleModel.transaction() as t:
            self.assertEqual(t.server,SimpleModel._meta.cursor)
            s = SimpleModel(code = 'test', description = 'just a test')\
                            .save(transaction = t)
            self.assertTrue(s.id)
            self.assertRaises(SimpleModel.DoesNotExist,SimpleModel.objects.get,id=s.id)
            s2 = SimpleModel(code = 'test2', description = 'just a test').save(transaction = t)

        all = list(SimpleModel.objects.all())
        self.assertEqual(len(all),2)
        v = SimpleModel.objects.get(code = 'test')
        self.assertEqual(v.description,'just a test')
        
    def testDelete(self):
        s = SimpleModel(code = 'test', description = 'just a test').save()
        self.assertEqual(SimpleModel.objects.get(id = s.id),s)
        s.delete()
        self.assertRaises(SimpleModel.DoesNotExist,
                          SimpleModel.objects.get,id=s.id)
        
    
class TestTransactionMultiFields(test.TestCase):
    pass
    
        
        
class TestMultiFieldTransaction(test.TestModelBase):
    model = Dictionary
    
    def make(self):
        with orm.transaction(self.model, name = 'create models') as t:
            self.assertEqual(t.name, 'create models')
            for name in names:
                self.model(name = name).save(t)
            self.assertFalse(t._cachepipes)
    
    def testSaveSimple(self):
        self.make()
        
    def testHashField(self):
        self.make()
        d1 = self.model.objects.get(id = 1)
        d2 = self.model.objects.get(id = 2)
        with orm.transaction(self.model) as t:
            d1.data.add('ciao','hello in Italian',t)
            d1.data.add('bla',10000,t)
            d2.data.add('wine','drink to enjoy with or without food',t)
            d2.data.add('foo',98,t)
            self.assertTrue(t._cachepipes)
            # We should have two entries in the cachepipes
            self.assertTrue(len(t._cachepipes),2)
            for c in t._cachepipes:
                self.assertEqual(len(t._cachepipes[c].pipe),2)
            
        self.assertTrue(len(t._cachepipes),2)
        for c in t._cachepipes:
            self.assertEqual(len(t._cachepipes[c].pipe),0)
            
        d1 = self.model.objects.get(id = 1)
        d2 = self.model.objects.get(id = 2)
        self.assertEqual(d1.data['ciao'],'hello in Italian')
        self.assertEqual(d2.data['wine'],'drink to enjoy with or without food')
    
    
