import unittest
from aftertone.provenance import locate_quote,inspect_claims,source_independence
class ProvenanceTests(unittest.TestCase):
 def test_quote_offset(self):
  t="a"*25+"Original artist interview states this fact."+"z"
  e=locate_quote(t,"Original artist interview states this fact.")
  self.assertEqual(t[e["start"]:e["end"]],"Original artist interview states this fact.")
 def test_unlocated_is_unverified(self):
  c=[{"id":"1","evidence":[{"source_id":"a","quote":"A quote that is not present anywhere."}]}]
  x=inspect_claims(c,[{"id":"a","status":"READ"}],{"a":"Nothing useful here."})
  self.assertEqual(x[0]["status"],"UNVERIFIED")
 def test_domains_are_not_independent_by_default(self):
  c={"verified_spans":[{"source_id":"a"},{"source_id":"b"}]}
  s=[{"id":"a","origin_chain":"press-release"},{"id":"b","origin_chain":"press-release"}]
  self.assertFalse(source_independence(c,s)["cross_verified"])
 def test_missing_origin_chain_not_auto_verified(self):
  c={"verified_spans":[{"source_id":"a"},{"source_id":"b"}]}
  s=[{"id":"a","independence_group":"site1"},{"id":"b","independence_group":"site2"}]
  self.assertFalse(source_independence(c,s)["cross_verified"])
if __name__=="__main__":unittest.main()
