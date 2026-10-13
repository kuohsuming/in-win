// 摘自 board-station.html 的 3D 繪圖原型（瀏覽器 Canvas 版），供移植到 PySide6 時對照
/* ================= 3D 繪圖（平面擬合 → 殘差 → 插值曲面 → 立體板子，每 30° 輪播） ================= */
let lastData=null, lastState="";
const V3={az:0,el:15,play:true,timer:null,m:null};   // 視角固定 15°
const plate=()=>Object.assign({length:1000,width:600,thickness:5,probe_side:"below"},DEF.plate||{});
/* 白灰渲染：底色依高度（低＝灰、高＝白），再依表面法線與光源計算明暗，做出凹凸立體感 */
const SHADE={lo:140,hi:228,relief:6,light:[-0.55,0.75,0.6]};   // light：相對眼睛的 左／上／朝向眼睛
const baseGray=t=>SHADE.lo+(SHADE.hi-SHADE.lo)*Math.max(0,Math.min(1,t));
function probePoints(data){ const D=devs(), P0=plate(), pts=[];
  D.forEach((d,ri)=>{ const P=sortedProbes(d), s=STDS[d.key];
    P.forEach((p,i)=>{ const e=data.err[`${ri}-${i}`], m=data.vals[ri][i];
      pts.push({x:p.x??P0.length*(i+.5)/P.length, y:p.y??P0.width*(ri+.5)/D.length,
        label:`${(d.name||"?")[0]}${i+1}`, name:`${d.name} ${p.description}（${(d.name||"?")[0]}${i+1}）`, m:e?null:m, st:e?"err":(s?judge(s,m):"ok")}); }); });
  return pts; }
function solveLin(A,b){ const n=b.length, M=A.map((r,i)=>[...r,b[i]]);
  for(let c=0;c<n;c++){ let p=c; for(let r=c+1;r<n;r++) if(Math.abs(M[r][c])>Math.abs(M[p][c])) p=r;
    [M[c],M[p]]=[M[p],M[c]]; if(Math.abs(M[c][c])<1e-10) return null;
    for(let r=0;r<n;r++){ if(r===c) continue; const k=M[r][c]/M[c][c]; for(let j=c;j<=n;j++) M[r][j]-=k*M[c][j]; } }
  return M.map((r,i)=>r[n]/r[i]); }
/* 最小平方平面 z = a + b·x + c·y（座標以公尺計，避免數值過大） */
function fitPlane(P){ const S=[[0,0,0],[0,0,0],[0,0,0]], t=[0,0,0];
  P.forEach(p=>{ const r=[1,p.x,p.y]; for(let i=0;i<3;i++){ t[i]+=r[i]*p.z; for(let j=0;j<3;j++) S[i][j]+=r[i]*r[j]; } });
  return solveLin(S,t); }
/* 薄板樣條插值（與 scipy RBFInterpolator thin_plate_spline 同一種），只用來畫點與點之間的形狀 */
function tps(P){ const n=P.length, N=n+3, A=Array.from({length:N},()=>new Array(N).fill(0)), b=new Array(N).fill(0);
  const U=r=>r<1e-12?0:r*r*Math.log(r);
  P.forEach((p,i)=>{ P.forEach((q,j)=>A[i][j]=U(Math.hypot(p.x-q.x,p.y-q.y)));
    A[i][n]=A[n][i]=1; A[i][n+1]=A[n+1][i]=p.x; A[i][n+2]=A[n+2][i]=p.y; b[i]=p.z; });
  const w=solveLin(A,b); if(!w) return null;
  return (x,y)=>{ let z=w[n]+w[n+1]*x+w[n+2]*y; P.forEach((p,i)=>z+=w[i]*U(Math.hypot(x-p.x,y-p.y))); return z; }; }
function buildModel(data){
  const P0=plate(), L=P0.length, W=P0.width, pts=probePoints(data), ok=pts.filter(p=>p.m!=null);
  if(ok.length<3) return {pts,err:"有效量測點不足 3 點，無法畫出表面。"};
  const sg=P0.probe_side==="below"?-1:1;   // 探頭在下方：讀值越大表示該處越低
  const c=fitPlane(ok.map(p=>({x:p.x/1000,y:p.y/1000,z:sg*p.m})));
  if(!c) return {pts,err:"有效量測點排成一直線，無法擬合平面。"};
  ok.forEach(p=>p.r=(sg*p.m-(c[0]+c[1]*p.x/1000+c[2]*p.y/1000))*1000);   // µm
  const f=tps(ok.map(p=>({x:p.x/L,y:p.y/L,z:p.r})))||(()=>0);
  const nx=41, ny=Math.max(9,Math.round(40*W/L)+1), g=[];
  for(let j=0;j<ny;j++){ const row=[]; for(let i=0;i<nx;i++) row.push(f(i/(nx-1),j/(ny-1)*W/L)); g.push(row); }
  const rs=ok.map(p=>p.r), lim=Math.max(1,...g.flat().map(Math.abs),...rs.map(Math.abs));
  const Tv=0.05*L, ex=0.4*Tv/lim;           // 顯示用厚度與高度倍率（µm → 顯示單位）
  const hi=ok.reduce((a,p)=>p.r>a.r?p:a), lo=ok.reduce((a,p)=>p.r<a.r?p:a);
  return {pts,ok,g,nx,ny,L,W,Tv,ex,lim,flat:hi.r-lo.r,hi,lo,sg,mag:ex*1000};
}
function draw3d(){
  const cv=$("#v3cv"), m=V3.m; if(!cv||!m||m.err) return;
  const dpr=window.devicePixelRatio||1, cw=cv.clientWidth, ch=cv.clientHeight; if(!cw||!ch) return;
  cv.width=Math.round(cw*dpr); cv.height=Math.round(ch*dpr);
  const ctx=cv.getContext("2d"); ctx.setTransform(dpr,0,0,dpr,0,0); ctx.clearRect(0,0,cw,ch);
  const css=getComputedStyle(document.documentElement), INK=css.getPropertyValue("--ink").trim(), NG=css.getPropertyValue("--ng").trim();
  const {L,W,Tv,ex,g,nx,ny}=m, h=0.4*Tv;
  const az=(-45+V3.az)*Math.PI/180, el=Math.min(V3.el,89.5)*Math.PI/180;
  const v=[Math.cos(el)*Math.cos(az),Math.cos(el)*Math.sin(az),Math.sin(el)];
  const rt=[-Math.sin(az),Math.cos(az)], up=[-Math.sin(el)*Math.cos(az),-Math.sin(el)*Math.sin(az),Math.cos(el)];
  const lv=SHADE.light, LW0=[lv[0]*rt[0]+lv[1]*up[0]+lv[2]*v[0], lv[0]*rt[1]+lv[1]*up[1]+lv[2]*v[1], lv[1]*up[2]+lv[2]*v[2]],
        LWn=Math.hypot(...LW0), LW=LW0.map(x=>x/LWn);
  const D=Math.hypot(L,W), sc=Math.min(cw*0.92/D, ch*0.84/(D*Math.sin(el)+(Tv+2*h)*Math.cos(el)));
  const pr=(x,y,z)=>{ const X=x-L/2,Y=y-W/2,Z=z+Tv/2;
    return [cw/2+sc*(X*rt[0]+Y*rt[1]), ch/2-sc*(X*up[0]+Y*up[1]+Z*up[2]), X*v[0]+Y*v[1]+Z*v[2]]; };
  const gx=i=>L*i/(nx-1), gy=j=>W*j/(ny-1), Z=(i,j)=>g[j][i]*ex;
  const polys=[];
  for(let j=0;j<ny-1;j++) for(let i=0;i<nx-1;i++){
    const q=[pr(gx(i),gy(j),Z(i,j)),pr(gx(i+1),gy(j),Z(i+1,j)),pr(gx(i+1),gy(j+1),Z(i+1,j+1)),pr(gx(i),gy(j+1),Z(i,j+1))];
    const r=(g[j][i]+g[j][i+1]+g[j+1][i+1]+g[j+1][i])/4, c=baseGray((r/m.lim+1)/2);
    const dzx=(Z(i+1,j)+Z(i+1,j+1)-Z(i,j)-Z(i,j+1))/2*SHADE.relief, dzy=(Z(i,j+1)+Z(i+1,j+1)-Z(i,j)-Z(i+1,j))/2*SHADE.relief;
    const dx=L/(nx-1), dy=W/(ny-1), nn=[-dzx*dy,-dzy*dx,dx*dy], nl=Math.hypot(...nn);
    const lit=(nn[0]*LW[0]+nn[1]*LW[1]+nn[2]*LW[2])/nl, k=Math.max(0.5,Math.min(1.14,1+1.8*(lit-LW[2])));
    const gv=Math.round(Math.min(255,c*k));
    polys.push({q,d:(q[0][2]+q[2][2])/2,fill:`rgb(${gv},${gv},${gv})`}); }
  const faces=[{n:[0,-1],e:[...Array(nx).keys()].map(i=>[i,0])},{n:[0,1],e:[...Array(nx).keys()].map(i=>[i,ny-1])},
               {n:[-1,0],e:[...Array(ny).keys()].map(j=>[0,j])},{n:[1,0],e:[...Array(ny).keys()].map(j=>[nx-1,j])}];
  const vis=faces.filter(F=>F.n[0]*v[0]+F.n[1]*v[1]>1e-6);
  vis.forEach(F=>{ const k=(F.n[0]*v[0]+F.n[1]*v[1])/Math.cos(el), s=0.45+0.35*Math.min(1,k);
    const col=[0.5*s+.12,0.5*s+.12,0.5*s+.14];
    const fill=`rgb(${col.map(x=>Math.round(Math.min(1,x)*255))})`;
    for(let t=0;t<F.e.length-1;t++){ const [i1,j1]=F.e[t],[i2,j2]=F.e[t+1];
      const q=[pr(gx(i1),gy(j1),Z(i1,j1)),pr(gx(i2),gy(j2),Z(i2,j2)),pr(gx(i2),gy(j2),Z(i2,j2)-Tv),pr(gx(i1),gy(j1),Z(i1,j1)-Tv)];
      polys.push({q,d:(q[0][2]+q[2][2])/2-1e-3,fill}); } });
  polys.sort((a,b)=>a.d-b.d);
  ctx.lineJoin="round"; ctx.lineWidth=0.7;
  for(const p of polys){ ctx.beginPath(); p.q.forEach(([x,y],k)=>k?ctx.lineTo(x,y):ctx.moveTo(x,y)); ctx.closePath();
    ctx.fillStyle=p.fill; ctx.strokeStyle=p.fill; ctx.fill(); ctx.stroke(); }
  /* 輪廓線 */
  ctx.strokeStyle="rgba(0,0,0,.75)"; ctx.lineWidth=1.1;
  const line=(arr,dz)=>{ ctx.beginPath(); arr.forEach(([i,j],k)=>{ const [x,y]=pr(gx(i),gy(j),Z(i,j)+dz); k?ctx.lineTo(x,y):ctx.moveTo(x,y); }); ctx.stroke(); };
  faces.forEach(F=>line(F.e,0)); vis.forEach(F=>line(F.e,-Tv));
  vis.forEach(F=>[F.e[0],F.e[F.e.length-1]].forEach(([i,j])=>{ const a=pr(gx(i),gy(j),Z(i,j)), b=pr(gx(i),gy(j),Z(i,j)-Tv);
    ctx.beginPath(); ctx.moveTo(a[0],a[1]); ctx.lineTo(b[0],b[1]); ctx.stroke(); }));
  /* 尺寸文字 */
  ctx.font=`500 13px ${css.getPropertyValue("--txt")}`; ctx.fillStyle=INK; ctx.textAlign="center"; ctx.textBaseline="middle";
  if(V3.el<80) vis.forEach(F=>{ const mid=F.e[Math.floor(F.e.length/2)], [x,y]=pr(gx(mid[0])+F.n[0]*W*.12,gy(mid[1])+F.n[1]*W*.12,-Tv);
    ctx.fillText(F.n[1]?`長 ${m.L} mm`:`寬 ${m.W} mm`,x,y+8); });
  /* 量測點與標籤 */
  const lab=[]; m.pts.forEach(p=>{ const z=p.m==null?0:p.r*ex, [x,y,d]=pr(p.x,p.y,z); lab.push({p,x,y,d}); });
  /* 標籤避讓：前面的點先放，依序嘗試上、下、左、右、更上方，不與已放的標籤重疊 */
  ctx.font=`700 13px ${css.getPropertyValue("--num")}`;
  const placed=[], hit=(r)=>placed.some(q=>r.x<q.x+q.w+2&&r.x+r.w+2>q.x&&r.y<q.y+q.h+2&&r.y+r.h+2>q.y);
  [...lab].sort((a,b)=>b.d-a.d).forEach(o=>{ const p=o.p, miss=p.m==null;
    o.t1=p.label; o.t2=miss?"無數據":`${p.r>=0?"+":""}${p.r.toFixed(1)}`;
    const w=Math.max(ctx.measureText(o.t1).width,ctx.measureText(o.t2).width)+10, h=34;
    const cand=[[-w/2,-h-10],[-w/2,10],[-w-10,-h/2],[10,-h/2],[-w/2,-2*h-14],[-w/2,h+14]];
    let r=null; for(const [dx,dy] of cand){ const t={x:o.x+dx,y:o.y+dy,w,h}; if(!hit(t)){ r=t; break; } }
    o.box=r||{x:o.x+cand[0][0],y:o.y+cand[0][1],w,h}; placed.push(o.box); });
  lab.sort((a,b)=>a.d-b.d).forEach(({p,x,y,box,t1,t2})=>{
    const bad=p.st==="hi"||p.st==="lo", miss=p.m==null;
    ctx.strokeStyle="rgba(0,0,0,.55)"; ctx.lineWidth=1; ctx.beginPath(); ctx.moveTo(x,y);
    ctx.lineTo(Math.max(box.x,Math.min(x,box.x+box.w)),Math.max(box.y,Math.min(y,box.y+box.h))); ctx.stroke();
    if(miss){ ctx.strokeStyle=NG; ctx.lineWidth=3; ctx.beginPath(); ctx.moveTo(x-6,y-6); ctx.lineTo(x+6,y+6); ctx.moveTo(x+6,y-6); ctx.lineTo(x-6,y+6); ctx.stroke(); }
    else { ctx.beginPath(); ctx.arc(x,y,4.5,0,7); ctx.fillStyle="#ff7a00"; ctx.fill(); ctx.lineWidth=1.2; ctx.strokeStyle="#111"; ctx.stroke(); }
    ctx.fillStyle=bad||miss?"rgba(200,50,43,.94)":"rgba(255,255,255,.9)"; ctx.beginPath();
    ctx.roundRect?ctx.roundRect(box.x,box.y,box.w,box.h,4):ctx.rect(box.x,box.y,box.w,box.h); ctx.fill();
    ctx.fillStyle=bad||miss?"#fff":"#1c2326"; ctx.textAlign="center"; ctx.fillText(t1,box.x+box.w/2,box.y+10); ctx.fillText(t2,box.x+box.w/2,box.y+25);
  });
  $("#v3ang").textContent=`旋轉 ${V3.az}°`;
}
function v3Side(){ const m=V3.m, el=$("#v3side");
  if(m.err){ el.innerHTML=""; return; }
  const grad=`linear-gradient(90deg,rgb(${SHADE.lo},${SHADE.lo},${SHADE.lo}),rgb(${SHADE.hi},${SHADE.hi},${SHADE.hi}))`;
  const fmt=v=>`${v>=0?"+":""}${v.toFixed(1)}`;
  const miss=m.pts.filter(p=>p.m==null), bad=m.pts.filter(p=>p.st==="hi"||p.st==="lo");
  el.innerHTML=`<div class="v3-card"><span class="k">平面度（最高 − 最低）</span><span class="big">${m.flat.toFixed(1)}<small>µm</small></span><span class="k">允許值：未定（TBD）</span></div>
    <div class="v3-card"><div class="ln"><span>最高點 ${esc(m.hi.name)}</span><b>${fmt(m.hi.r)}</b></div><div class="ln"><span>最低點 ${esc(m.lo.name)}</span><b>${fmt(m.lo.r)}</b></div>
      <span class="k">單位 µm，相對於擬合平面</span></div>
    <div class="v3-card v3-leg"><span class="k">越高越白、越低越灰；光從左上方照射</span><div class="bar" style="background:${grad}"></div>
      <div class="tk"><span>${fmt(-m.lim)}</span><span>0</span><span>${fmt(m.lim)}</span></div></div>
    ${bad.length||miss.length?`<div class="v3-card" style="border-color:var(--ng)">${bad.length?`<span style="color:var(--ng);font-weight:700">超出允收：${bad.map(p=>esc(p.name)).join("、")}</span>${m.sg<0?`<span class="k">探頭在下方：讀值「偏高」＝該處表面較低</span>`:""}`:""}${miss.length?`<span style="color:var(--ng);font-weight:700">無數據（不參與擬合）：${miss.map(p=>esc(p.name)).join("、")}</span>`:""}</div>`:""}
    <ul class="v3-note"><li>使用 ${m.ok.length}/${m.pts.length} 點；已扣除整片傾斜與高低。</li><li>高度放大約 ×${Math.round(m.mag).toLocaleString()} 倍，厚度為示意。</li>
      <li>點與點之間的形狀是推估，判定以實測點為準。</li><li>探頭在${m.sg<0?"下方，已換算成由上往下看的高度":"上方"}。</li></ul>`;
}
function v3Render(){ const m=V3.m, msg=$("#v3msg");
  msg.hidden=!m.err; if(m.err){ msg.textContent=m.err; const c=$("#v3cv"); c.getContext("2d").clearRect(0,0,c.width,c.height); }
  $("#v3play").textContent=V3.play?"❚❚ 暫停":"▶ 播放";
  ["#v3prev","#v3play","#v3next"].forEach(k=>$(k).disabled=!!m.err);
  v3Side(); draw3d(); }
function v3Timer(){ clearInterval(V3.timer); V3.timer=null;
  if(V3.play&&!V3.m?.err&&$("#v3Dlg").open) V3.timer=setInterval(()=>{ V3.az=(V3.az+30)%360; draw3d(); },700); }
function upd3dBtn(){ const n=lastData?probePoints(lastData).filter(p=>p.m!=null).length:0, b=$("#v3dBtn");
  b.disabled=busy||n<3; b.title=n<3?"需要至少 3 個有效量測點":"以立體圖檢視這一片的表面高低"; }
function open3d(){ if(!lastData||busy) return;
  V3.m=buildModel(lastData); V3.az=0;
  $("#v3sn").textContent=serial?`編號 ${serial}`:"";
  const rs=$("#v3rs"); rs.className="rs "+lastState; rs.textContent={pass:"合格",fail:"不合格",device:"設備異常"}[lastState]||"";
  $("#v3Dlg").showModal(); requestAnimationFrame(()=>{ v3Render(); v3Timer(); }); }
function close3d(){ clearInterval(V3.timer); V3.timer=null; $("#v3Dlg").close(); }
$("#v3dBtn").addEventListener("click",open3d);
$("#v3Close").addEventListener("click",close3d); $("#v3done").addEventListener("click",close3d);
$("#v3Dlg").addEventListener("close",()=>{ clearInterval(V3.timer); V3.timer=null; });
$("#v3prev").addEventListener("click",()=>{ V3.play=false; V3.az=(V3.az+330)%360; v3Render(); v3Timer(); });
$("#v3next").addEventListener("click",()=>{ V3.play=false; V3.az=(V3.az+30)%360; v3Render(); v3Timer(); });
$("#v3play").addEventListener("click",()=>{ V3.play=!V3.play; v3Render(); v3Timer(); });
$("#v3Dlg").addEventListener("keydown",e=>{ if(e.key==="ArrowLeft") $("#v3prev").click(); else if(e.key==="ArrowRight") $("#v3next").click();
  else if(e.key===" "&&e.target.tagName!=="BUTTON"){ e.preventDefault(); $("#v3play").click(); } });
window.addEventListener("resize",()=>{ if($("#v3Dlg").open) draw3d(); });

