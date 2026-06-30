import os,json,sys,time,urllib.request,urllib.error
H={'X-Access-Key':os.environ['HOG_ACCESS_KEY'],'X-Secret-Key':os.environ['HOG_SECRET_KEY'],'Content-Type':'application/json'}
BASE='https://developer.thehog.ai'
def req(path,method='GET',body=None):
    r=urllib.request.Request(BASE+path,data=(json.dumps(body).encode() if body else None),headers=H,method=method)
    try: return urllib.request.urlopen(r).status, json.load(urllib.request.urlopen(urllib.request.Request(BASE+path,data=(json.dumps(body).encode() if body else None),headers=H,method=method)))
    except urllib.error.HTTPError as e: return e.code,{'_err':e.read().decode('utf-8','replace')}
lurl=sys.argv[1]; rawfile=sys.argv[2]
r=urllib.request.Request(BASE+'/api/enrichments',data=json.dumps({'identifier':{'linkedin_url':lurl},'fields':['contact.email','work_email']}).encode(),headers=H,method='POST')
try:
    resp=urllib.request.urlopen(r); code=resp.status; d=json.load(resp)
except urllib.error.HTTPError as e:
    code=e.code; d={'_http_error':e.code,'_body':e.read().decode('utf-8','replace')}
# handle async 202
if isinstance(d,dict) and d.get('id') and d.get('status') in ('queued','processing') and 'work_email' not in (d.get('data') or {}):
    oid=d['id']
    for i in range(20):
        rr=urllib.request.Request(BASE+'/api/enrichments/'+oid,headers=H)
        try: d=json.load(urllib.request.urlopen(rr))
        except Exception as e: break
        if d.get('status') in ('succeeded','failed','completed'): break
        time.sleep(2.5)
open(rawfile,'w',encoding='utf-8').write(json.dumps(d))
data=d.get('data',d) if isinstance(d.get('data'),dict) else d
we=(data.get('work_email') if isinstance(data,dict) else None) or (data.get('contact',{}) if isinstance(data,dict) else {})
print('HTTP',code,'| work_email:', (data.get('work_email') if isinstance(data,dict) else None), '| contact.email:', (data.get('contact',{}) or {}).get('email') if isinstance(data,dict) else None, '| status:', d.get('status'))
