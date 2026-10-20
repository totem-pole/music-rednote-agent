import unittest
from aftertone.engine import make_plan,safe_url,plain,wiki,mb,sources_from,conflict,corroboration,audit
class EngineTests(unittest.TestCase):
 def test_rounds(self):
  p=make_plan("陈淑桦","一生守候");self.assertEqual(len({x["round"] for x in p["tasks"]}),8);self.assertGreaterEqual(len(p["tasks"]),32)
 def test_safe_url(self):
  for x in ("http://example.org/","https://localhost/a","https://127.0.0.1/","https://example.org:8888/"):
   with self.assertRaises(ValueError):safe_url(x)
 def test_html(self):self.assertEqual(plain("<script>BAD</script><p>good</p>"),"good")
 def test_wiki_mock(self):
  out=wiki("a",fetch=lambda _:{"query":{"search":[{"title":"Album","snippet":"hello"}]}})
  self.assertEqual(out[0]["role"],"DISCOVERY_ONLY")
 def test_mb_mock(self):
  out=mb("a","b",fetch=lambda _:{"release-groups":[{"id":"123","title":"Album"}]})
  self.assertEqual(out[0]["publisher"],"MusicBrainz")
 def test_dedup(self):
  out=sources_from([{"url":"https://example.org/a#x"},{"url":"https://example.org/a#y"}],"q")
  self.assertEqual(len(out),1)
 def test_conflict(self):
  arr=[{"type":"FACT","subject":"a","predicate":"date","edition":"first","value":"1990"},{"type":"FACT","subject":"a","predicate":"date","edition":"first","value":"1991"}]
  self.assertEqual(len(conflict(arr)),1)
 def test_provenance(self):
  src=[{"id":"a","status":"READ","origin_chain":"press"},{"id":"b","status":"READ","origin_chain":"press"}]
  self.assertEqual(corroboration([{"id":"1","type":"FACT","source_ids":["a","b"]}],src)[0]["independent_chains"],1)
 def test_no_false_publish(self):
  self.assertFalse(audit(make_plan("a","b"),[],[])["publishable"])
if __name__=="__main__":unittest.main()
