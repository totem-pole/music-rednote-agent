import tempfile,json,unittest
from pathlib import Path
from aftertone.capture import capture
class CaptureTests(unittest.TestCase):
 def test_captured_document_is_marked_read_but_not_verified(self):
  with tempfile.TemporaryDirectory() as tmp:
   f=Path(tmp)
   (f/"sources.json").write_text(json.dumps([{"id":"a","url":"https://pitchfork.com/reviews/albums/test","title":"Test","publisher":"Pitchfork","status":"DISCOVERED_NOT_READ"}]))
   r=capture(f,1,fetch=lambda _: "<html><article><p>"+("In 2018 this record was released by the band. "*20)+"</p></article></html>")
   self.assertEqual(r["read"],1)
   self.assertEqual(r["claims_automatically_verified"],0)
   self.assertTrue((f/"pages/a.txt").exists())
 def test_unapproved_domain_skipped(self):
  with tempfile.TemporaryDirectory() as tmp:
   f=Path(tmp)
   (f/"sources.json").write_text(json.dumps([{"id":"x","url":"https://example.org/s","title":"x","status":"DISCOVERED_NOT_READ"}]))
   r=capture(f,1,fetch=lambda _: "must not be called")
   self.assertEqual(r["attempted_read"],0)
if __name__=="__main__":unittest.main()
