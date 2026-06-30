import os,json,sys,urllib.request,urllib.error
H={'X-Access-Key':os.environ['HOG_ACCESS_KEY'],'X-Secret-Key':os.environ['HOG_SECRET_KEY'],'Content-Type':'application/json'}
BASE='https://developer.thehog.ai'
slug=sys.argv[1]; rawfile=sys.argv[2]
r=urllib.request.Request(BASE+'/api/v1/platform/scrapers/linkedin/company',data=json.dumps({'identifier':slug}).encode(),headers=H,method='POST')
try:
    resp=urllib.request.urlopen(r); d=json.load(resp); code=resp.status
except urllib.error.HTTPError as e:
    code=e.code; d={'_http_error':e.code,'_body':e.read().decode('utf-8','replace')}
open(rawfile,'w',encoding='utf-8').write(json.dumps(d))
data=d.get('data',{}) if isinstance(d.get('data'),dict) else {}
out={'http':code,'name':data.get('name'),'employee_count':data.get('employee_count') or data.get('employeeCount'),'staff_count':data.get('staff_count'),'industry':data.get('industry'),'tagline':data.get('tagline')}
sys.stdout.buffer.write((json.dumps(out,ensure_ascii=False)+"\n").encode('utf-8','replace'))
desc=(data.get('description') or '')[:400]
sys.stdout.buffer.write(("DESC: "+desc+"\n").encode('utf-8','replace'))
