import os,json,sys,urllib.request,urllib.error
H={'X-Access-Key':os.environ['HOG_ACCESS_KEY'],'X-Secret-Key':os.environ['HOG_SECRET_KEY'],'Content-Type':'application/json'}
BASE='https://developer.thehog.ai'
def post(path,body):
    req=urllib.request.Request(BASE+path,data=json.dumps(body).encode(),headers=H,method='POST')
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return {'_http_error':e.code,'_body':e.read().decode('utf-8','replace')}
user=sys.argv[1]; rawfile=sys.argv[2]
d=post('/api/v1/platform/scrapers/linkedin/profile',{'username':user})
io=open(rawfile,'w',encoding='utf-8'); io.write(json.dumps(d)); io.close()
data=d.get('data',{}) if isinstance(d.get('data'),dict) else {}
out={'http_error':d.get('_http_error'),'full_name':data.get('full_name'),'headline':data.get('headline'),'current_company':data.get('current_company'),'location':data.get('location'),'about_len':len(data.get('about') or '')}
exp=data.get('experience') or []
if exp: out['exp0']=exp[0]
sys.stdout.buffer.write((json.dumps(out,ensure_ascii=False)[:1200]+"\n").encode('utf-8','replace'))
about=(data.get('about') or '')[:600]
sys.stdout.buffer.write(("ABOUT: "+about+"\n").encode('utf-8','replace'))
