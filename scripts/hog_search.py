import os,json,time,sys,urllib.request
H={'X-Access-Key':os.environ['HOG_ACCESS_KEY'],'X-Secret-Key':os.environ['HOG_SECRET_KEY'],'Content-Type':'application/json'}
BASE='https://developer.thehog.ai'
def post(path,body):
    req=urllib.request.Request(BASE+path,data=json.dumps(body).encode(),headers=H,method='POST')
    return json.load(urllib.request.urlopen(req))
def get(path):
    req=urllib.request.Request(BASE+path,headers=H)
    return json.load(urllib.request.urlopen(req))
def web_search(query,rawfile,max_results=10):
    r=post('/api/v1/search',{'type':'web_search','query':query,'max_results':max_results})
    sid=r['id']
    for i in range(25):
        d=get('/api/v1/search/'+sid)
        if d.get('status')=='succeeded':
            open(rawfile,'w',encoding='utf-8').write(json.dumps(d))
            return d.get('results',[])
        if d.get('status')=='failed':
            open(rawfile,'w',encoding='utf-8').write(json.dumps(d)); return []
        time.sleep(2.5)
    return []
if __name__=='__main__':
    q=sys.argv[1]; rawfile=sys.argv[2]
    res=web_search(q,rawfile)
    for x in res:
        sys.stdout.buffer.write((x.get('url','')[:95]+' || '+x.get('title','')[:60]+chr(10)).encode('utf-8','replace'))
