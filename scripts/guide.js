(function(){
'use strict';
const key='hzqd-offline-v13';
const checks=[...document.querySelectorAll('[data-check]')];
const memo=document.getElementById('memo'), hint=document.getElementById('save-hint'), start=document.getElementById('start-date');
const budgets=[...document.querySelectorAll('[data-budget]')];
let state={checks:{},memo:'',startDate:'',budget:{}}, toastTimer;
try {const old=JSON.parse(localStorage.getItem(key)||localStorage.getItem('hzqd-offline-v12')||localStorage.getItem('hzqd-offline-v11')||localStorage.getItem('hzqd-offline-v10')||localStorage.getItem('hzqd-offline-v9')||localStorage.getItem('hzqd-offline-v8')||'null');if(old&&typeof old==='object'){state.checks=old.checks&&typeof old.checks==='object'?old.checks:{};state.memo=typeof old.memo==='string'?old.memo:'';state.startDate=typeof old.startDate==='string'?old.startDate:'';state.budget=old.budget&&typeof old.budget==='object'?old.budget:{};}else state.memo=localStorage.getItem('tripMemo')||'';} catch(e) {hint.textContent='浏览器限制本地保存；关闭前请复制重要备注。';}
function save(){state.checks=Object.fromEntries(checks.map(c=>[c.dataset.check,c.checked]));state.memo=memo.value;state.startDate=start.value;state.budget=Object.fromEntries(budgets.map(i=>[i.dataset.budget,i.value]));document.getElementById('print-memo').textContent=memo.value;try{localStorage.setItem(key,JSON.stringify(state));}catch(e){hint.textContent='当前浏览器无法保存；关闭前请复制重要备注。';}}
function count(){document.getElementById('check-progress').textContent='已准备 '+checks.filter(c=>c.checked).length+' / '+checks.length+' 项';}
function dates(){
  const v=start.value, status=document.getElementById('date-status'), warning=document.getElementById('weather-date-warning');
  const valid=v&&!Number.isNaN(new Date(v+'T12:00:00').getTime());
  const d=new Date((valid?v:'2026-09-27')+'T12:00:00');
  document.querySelectorAll('[data-day-date]').forEach(x=>{const t=new Date(d);t.setDate(t.getDate()+Number(x.dataset.dayDate)-1);x.textContent=(t.getMonth()+1)+'月'+t.getDate()+'日 · '+'日一二三四五六'[t.getDay()];});
  const changed=valid&&v!=='2026-09-27';if(warning)warning.hidden=!changed;
  status.textContent=changed?'当前为试排日历：已约2026年9月29日14:34接站、10月7日家属抵杭的硬节点未改变。天气仍对应原定9月27日—10月7日，须按新日期重新查询；这里不更改票务。':(valid?'日期已确认：':'日期框未填，仍按已确认计划显示：')+'2026年9月27日出发，9月29日14:34接G881，10月7日家属抵杭。天气按这组日期自动同步；最新状态见全程天气章节。';
}
function budget(){const inputs=budgets.filter(i=>i.dataset.budget!=='reserve');const filled=inputs.filter(i=>i.value!==''&&i.validity.valid);const sum=filled.reduce((a,i)=>a+Number(i.value),0);const rate=budgets.find(i=>i.dataset.budget==='reserve');const percent=rate.validity.valid&&rate.value!==''?Number(rate.value):0;const money=n=>n.toLocaleString('zh-CN',{maximumFractionDigits:0});document.getElementById('budget-result').textContent=filled.length?'已填 '+filled.length+'/6 类费用小计 ¥'+money(sum)+'；加 '+percent+'% 机动金后 ¥'+money(sum*(1+percent/100))+'。'+(filled.length<6?' 尚有未填费用，请勿视为全程总价。':' 按当前填写金额估算，非供应商报价。'):'尚未填写费用。';}
checks.forEach(c=>{c.checked=state.checks[c.dataset.check]===true;c.addEventListener('change',()=>{count();save();});});memo.value=state.memo;start.value=state.startDate||'2026-09-27';budgets.forEach(i=>{if(Object.prototype.hasOwnProperty.call(state.budget,i.dataset.budget))i.value=state.budget[i.dataset.budget];i.addEventListener('input',()=>{budget();save();});});document.getElementById('print-memo').textContent=memo.value;memo.addEventListener('input',save);start.addEventListener('input',()=>{dates();save();});count();dates();budget();
function toast(t){const el=document.getElementById('toast');el.textContent=t;clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.textContent='',3500);}
document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{let ok=false;try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(b.dataset.copy);ok=true;}}catch(e){}if(!ok){const f=document.createElement('textarea');f.value=b.dataset.copy;f.style.position='fixed';f.style.left='-9999px';document.body.appendChild(f);f.select();try{ok=document.execCommand('copy');}catch(e){}f.remove();b.focus();}toast(ok?'已复制，可粘贴到导航或同行聊天。':'未能自动复制，请长按页面文字复制。');}));
document.getElementById('expand-days').addEventListener('click',()=>document.querySelectorAll('.day-card').forEach(d=>d.open=true));document.getElementById('collapse-days').addEventListener('click',()=>document.querySelectorAll('.day-card').forEach(d=>d.open=false));
const photoDialog=document.getElementById('photo-dialog');
if(photoDialog&&typeof photoDialog.showModal==='function'){
  let photoOpener=null;
  document.querySelectorAll('.photo-open').forEach(button=>button.addEventListener('click',()=>{
    photoOpener=button;
    const original=button.querySelector('img'),large=document.getElementById('photo-large');
    large.src=original.currentSrc||original.src;large.alt=original.alt;
    document.getElementById('photo-description').innerHTML=button.closest('figure').querySelector('figcaption').innerHTML;
    photoDialog.showModal();document.documentElement.classList.add('photo-dialog-open');
  }));
  photoDialog.querySelector('.photo-close').addEventListener('click',()=>photoDialog.close());
  photoDialog.addEventListener('click',e=>{if(e.target===photoDialog){const r=photoDialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)photoDialog.close();}});
  photoDialog.addEventListener('close',()=>{document.documentElement.classList.remove('photo-dialog-open');if(photoOpener)photoOpener.focus({preventScroll:true});});
}
function reveal(hash){if(!hash||hash==='#')return;let t=document.getElementById(hash.slice(1));if(!t)return;if(t.classList.contains('day-story')){const detail=t.querySelector('.day-card');if(detail)detail.open=true;}for(let p=t;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;}
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',()=>reveal(a.hash)));window.addEventListener('hashchange',()=>reveal(location.hash));reveal(location.hash);
let printState=[];window.addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('details')].map(d=>[d,d.open]);printState.forEach(([d])=>d.open=true);});window.addEventListener('afterprint',()=>printState.forEach(([d,o])=>d.open=o));document.getElementById('print-button').addEventListener('click',()=>window.print());
if('IntersectionObserver' in window){const links=[...document.querySelectorAll('.nav a')];const observer=new IntersectionObserver(entries=>{entries.forEach(e=>{if(e.isIntersecting)links.forEach(a=>a.hash==='#'+e.target.id?a.setAttribute('aria-current','location'):a.removeAttribute('aria-current'));});},{rootMargin:'-8% 0px -65% 0px'});links.forEach(a=>{const s=document.getElementById(a.hash.slice(1));if(s)observer.observe(s);});}
})();
