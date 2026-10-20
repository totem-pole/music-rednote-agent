import json,subprocess
cmd=["mcporter","call","exa.web_search_exa","--args",json.dumps({"query":"Say Sue Me Where We Were Together 2018 review","numResults":3}),"--output","json","--timeout","25000"]
try:
 p=subprocess.run(cmd,check=False,capture_output=True,text=True,timeout=35)
 print("EXIT",p.returncode)
 print("STDOUT",p.stdout[:3200].replace("\x00",""))
 print("STDERR",p.stderr[:800].replace("\x00",""))
except Exception as e:print("ERROR",str(e))
