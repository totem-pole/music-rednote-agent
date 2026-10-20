import unittest,json
from aftertone.exa import parse_mcporter,search
class ExaTests(unittest.TestCase):
 def test_parse_real_response_shape(self):
  raw={"content":[{"type":"text","text":"Title: Album review\nURL: https://pitchfork.com/reviews/albums/a/\nPublished: 2018\nHighlights:\nMusic analysis.\n"}]}
  x=parse_mcporter(raw)
  self.assertEqual(len(x),1)
  self.assertEqual(x[0]["publisher"],"pitchfork.com")
 def test_server_error_not_fake_hit(self):
  self.assertEqual(parse_mcporter({"content":[{"type":"text","text":"Rate limited, no results."}]}),[])
 def test_runner(self):
  out=search("music",runner=lambda cmd: json.dumps({"content":[{"type":"text","text":"Title: Interview\nURL: https://daily.bandcamp.com/a\nPublished: 2018"}]}))
  self.assertEqual(len(out),1)
if __name__=="__main__":unittest.main()
