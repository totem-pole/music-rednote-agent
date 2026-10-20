import unittest
from aftertone.evidence import parse_html,permitted_url,retrieve_article,claim_candidates,similarity_report,quality_gate
class EvidenceTests(unittest.TestCase):
 def test_html(self):
  page=parse_html("<html><head><title>Music</title><script>evil</script></head><body><article><p>Useful narrative</p></article><footer>hidden</footer></body></html>")
  self.assertEqual(page["title"],"Music")
  self.assertIn("Useful narrative",page["text"])
  self.assertNotIn("hidden",page["text"])
 def test_allowlist(self):
  with self.assertRaises(ValueError):permitted_url("https://localhost/admin",["example.org"])
  with self.assertRaises(ValueError):permitted_url("https://bad-example.org/article",["example.org"])
  self.assertEqual(permitted_url("https://news.example.org/item",["example.org"]),"https://news.example.org/item")
 def test_fetch_mock(self):
  d=retrieve_article("https://example.org/a",["example.org"],fetch=lambda _: "<article><p>"+("album facts and recording notes "*8)+"</p></article>")
  self.assertEqual(d["status"],"READ")
 def test_candidates_are_unverified(self):
  c=claim_candidates("这张唱片发行于1990年，录制过程由不同的制作人参与。","src")
  self.assertEqual(c[0]["type"],"UNVERIFIED")
 def test_similarity(self):
  d="这张唱片曾经带来非常独特的音乐体验和城市文化回忆"
  x=similarity_report(d,[{"id":"a","text":d}])
  self.assertTrue(x["alerts"])
  self.assertFalse(x["certifies_originality"])
 def test_gate(self):
  s=[{"id":"a","status":"DISCOVERED_NOT_READ"}]
  c=[{"id":"1","type":"FACT","source_ids":["a"]}]
  result=quality_gate(c,s,[],False)
  self.assertFalse(result["ready_for_publication"])
  self.assertEqual(len(result["failures"]),3)
if __name__=="__main__":unittest.main()
