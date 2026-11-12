const {chromium}=require('playwright'),path=require('path');
(async()=>{const b=await chromium.launch();const pg=await b.newPage();
await pg.goto('file://'+path.resolve('anim.html'));
const r=await pg.evaluate(()=>{const kw=[];for(const[t0,txt,y,keys]of FR){if(!txt)continue;const W=txt.split(' '),T=wtimes(W,t0);W.forEach((w,i)=>{if(keys.includes(norm(w)))kw.push([+toReal(T[i]).toFixed(3),w])})}
 return {cuts:CUTS,kw,phr:FR.filter(f=>f[1]).map(f=>+toReal(f[0]).toFixed(3)),hits:HITS.map(h=>[+h[0].toFixed(3),h[1]]),dur:DUR,ins:INSL.map(([a,c])=>({t:+toReal(a-1e-6).toFixed(3),len:LEN(c),half:HALF(c),q:CUTQ(c)})),end:toReal(SC[SC.length-1].s)}});
require('fs').writeFileSync(process.argv[2],JSON.stringify(r));console.log(JSON.stringify(r));await b.close()})();
