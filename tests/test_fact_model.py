import unittest
from aftertone.fact_model import produce_candidates
class ModelClaimTests(unittest.TestCase):
 def test_exact_quote_required(self):
  src={"id":"a","url":"https://example.org"};doc="In 2018 the band's album was officially released on its record label."
  model=lambda p:{"claims":[{"claim":"Released 2018","subject":"album","predicate":"year","value":"2018","edition":"original","quote":"In 2018 the band's album was officially released"}]}
  result=produce_candidates(src,doc,model)
  self.assertEqual(len(result["located"]),1)
  self.assertEqual(result["located"][0]["status"],"QUOTE_LOCATED")
 def test_hallucinated_quote_rejected(self):
  model=lambda p:{"claims":[{"claim":"false","quote":"A fabricated quote not in the actual document!"}]}
  result=produce_candidates({"id":"a","url":"https://example.org"},"actual real page",model)
  self.assertEqual(len(result["rejected"]),1)
 def test_invalid_schema_raises(self):
  with self.assertRaises(ValueError):produce_candidates({"id":"a","url":"https://example.org"},"text",lambda p:{"oops":5})
if __name__=="__main__":unittest.main()
