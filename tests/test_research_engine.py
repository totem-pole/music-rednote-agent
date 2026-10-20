import unittest
from research_engine import plan,canonical,extract_document,conflicts
class ResearchTests(unittest.TestCase):
 def test_eight_rounds(self):
  q=plan("陈淑桦","一生守候")
  self.assertEqual(len(set(x["round"] for x in q)),8)
  self.assertTrue(any("rateyourmusic.com" in x["query"] for x in q))
 def test_canonical(self):
  self.assertEqual(canonical("http://example.org/a/#fragment"),"https://example.org/a")
 def test_local_block(self):
  with self.assertRaises(ValueError):canonical("http://127.0.0.1/secrets")
 def test_html_extract(self):
  self.assertEqual(extract_document("<script>BAD</script><p>唱片</p>"),"唱片")
 def test_conflicts(self):
  items=[{"id":"a","subject":"record","property":"tracks","edition":"digital","value":11},
         {"id":"b","subject":"record","property":"tracks","edition":"digital","value":12}]
  self.assertEqual(len(conflicts(items)),1)
if __name__=="__main__":unittest.main()
