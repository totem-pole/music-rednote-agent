import json,unittest
from unittest.mock import patch
from aftertone.writer import call_llm,build_prompt
class WriterTests(unittest.TestCase):
 def test_requires_model_credentials(self):
  with self.assertRaises(ValueError):call_llm({},"https://api.example.org","","model")
 def test_rejects_insecure_endpoint(self):
  with self.assertRaises(ValueError):call_llm({},"http://example.org","key","model")
 def test_fake_llm_response_parses(self):
  class Response:
   def __enter__(self):return self
   def __exit__(self,*args):return False
   def read(self,max_bytes):
    return json.dumps({"choices":[{"message":{"content":json.dumps({"title":"Album","body":"Evidence-grounded draft","tags":["#review"],"claim_ids_used":["a"],"unresolved_issues":[]})}}]}).encode()
  with patch("aftertone.writer.urllib.request.urlopen",return_value=Response()) as fake:
   result=call_llm({"facts":[{"id":"a"}]},"https://api.example.org","test-secret","demo-model")
   self.assertEqual(result["title"],"Album")
   request=fake.call_args.args[0]
   self.assertNotIn("test-secret",request.data.decode())
 def test_prompt_only_uses_verified(self):
  claims=[{"id":"ok","type":"FACT","status":"VERIFIED"},{"id":"bad","type":"FACT","status":"UNVERIFIED"}]
  x=build_prompt([],claims,[])
  self.assertEqual([c["id"] for c in x["facts"]],["ok"])
if __name__=="__main__":unittest.main()
