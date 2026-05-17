const http=require('http');const fs=require('fs');const p=require('path');const ROOT=process.cwd();
http.createServer((req,res)=>{
  let url=decodeURIComponent(req.url.split('?')[0]);
  let f=p.join(ROOT,url);
  if(url==='/'||f.endsWith(p.sep))f=p.join(ROOT,'index.html');
  fs.readFile(f,(e,d)=>{
    if(e){res.writeHead(404);res.end('not found: '+url);return;}
    const ext=p.extname(f).toLowerCase();
    const mt={'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.svg':'image/svg+xml'}[ext]||'text/plain';
    res.writeHead(200,{'Content-Type':mt,'Cache-Control':'no-cache'});
    res.end(d);
  });
}).listen(8080,'127.0.0.1',()=>console.log('listening http://localhost:8080'));
