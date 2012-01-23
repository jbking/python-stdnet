from hashlib import sha1

from stdnet.lib import RedisScript, read_lua_file, get_script

from .base import TestCase


to_charlist = lambda x: [x[c:c + 1] for c in range(len(x))]
binary_set = lambda x : set(to_charlist(x))


class test_script(RedisScript):
    script = (read_lua_file('utils/redis.lua'),
              '''return {1,2,3,4,5,6}''')


class ScriptingCommandsTestCase(TestCase):
    tag = 'script'
    default_run = False

    def testEvalSimple(self):
        self.client = self.get_client()
        r = self.client.eval('return {1,2,3,4,5,6}')
        self.assertTrue(isinstance(r,list))
        self.assertEqual(len(r),6)
        
    def testTable(self):
        self.client = self.get_client()
        r = self.client.eval('return {name="mars", mass=0.11, orbit = 1.52}')
        self.assertTrue(isinstance(r,list))
        self.assertEqual(len(r), 0)
        
    def testDelPattern(self):
        c = self.get_client()
        items = ('bla',1,
                 'bla1','ciao',
                 'bla2','foo',
                 'xxxx','moon',
                 'blaaaaaaaaaaaaaa','sun',
                 'xyyyy','earth')
        c.execute_command('MSET', *items)
        N = c.delpattern('bla*')
        self.assertEqual(N,4)
        self.assertFalse(c.exists('bla'))
        self.assertFalse(c.exists('bla1'))
        self.assertFalse(c.exists('bla2'))
        self.assertFalse(c.exists('blaaaaaaaaaaaaaa'))
        self.assertEqual(c.get('xxxx'),b'moon')
        N = c.delpattern('x*')
        self.assertEqual(N,2)
    
    def testScript(self):
        script = get_script('test_script')
        self.assertTrue(script.script)
        sha = sha1(script.script.encode('utf-8')).hexdigest()
        self.assertEqual(script.sha1,sha)
        
    def testEvalSha(self):
        self.assertEqual(self.client.script_flush(),True)
        r = self.client.script_call('test_script')
        self.assertEqual(r,[1,2,3,4,5,6])
        r = self.client.script_call('test_script')
        self.assertEqual(r,[1,2,3,4,5,6])
    