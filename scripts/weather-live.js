(function(){
  'use strict';
  const core=window.TripWeather,configNode=document.getElementById('weather-config');
  if(!core||!configNode)return;
  const config=JSON.parse(configNode.textContent),interval=15*60*1000,cacheKey='hzqd-live-weather-v13';
  const status=document.getElementById('weather-live-status'),button=document.getElementById('weather-update'),checked=document.getElementById('weather-synced-at'),source=document.getElementById('weather-provider'),coverage=document.getElementById('weather-coverage');
  let lastGood=null,inflight=false,lastAttempt=0,pollTimer=null;
  const stamp=value=>new Intl.DateTimeFormat('zh-CN',{timeZone:'Asia/Shanghai',month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit',hour12:false}).format(new Date(value));
  function node(tag,text,className){const e=document.createElement(tag);if(text!=null)e.textContent=text;if(className)e.className=className;return e;}
  function render(payload,fetchedAt,cached){
    const today=core.chinaDate(new Date());let readyCount=0,totalCount=0;
    const byCity=Object.fromEntries(config.cities.map((c,i)=>[c.name,payload[i]]));
    config.days.forEach(day=>{
      const card=document.getElementById('weather-d'+day.n),container=card.querySelector('.weather-locations');container.replaceChildren();
      const results=day.locations.map(place=>core.forecast(byCity[place.city],day.date,today));
      const past=day.date<today,any=results.some(r=>r.available),all=results.every(r=>r.available);
      const badge=past?'日期已过':!any?'预报待发布':!all?'部分待发布':results.some(r=>r.trend)?'远期趋势':'逐日预报';
      card.classList.toggle('pending',!any);card.querySelector('.weather-badge').textContent=badge;
      results.forEach((result,i)=>{
        const place=day.locations[i],row=node('div',null,'weather-location'),city=node('div');city.append(node('b',place.city));
        city.append(node('small',place.optional?'提前返杭备选':place.note||'市区参考'));row.append(city);
        const info=node('div');totalCount++;
        if(result.available){
          readyCount++;const temp=node('strong',result.low+'–'+result.high,'weather-temp');temp.append(node('small','℃'));info.append(temp,node('p',result.text+' · 当日天气参考'));
          const lines=[];if(core.finite(result.rain))lines.push('最高降水概率 '+result.rain+'%');
          if(core.finite(result.wind))lines.push(result.direction+' · 最大风速 '+result.wind+' km/h');
          if(core.finite(result.gust))lines.push('最大阵风 '+result.gust+' km/h');
          info.append(node('p',lines.join('；'),'weather-wind'));
        }else{info.append(node('strong',past?'日期已过':'待发布','weather-unavailable'),node('p',past?'实时接口不再将这一天作为未来预报；不以今日天气代替。':'当天温度与天气尚未完整发布，进入预报范围后自动补齐。'));}
        row.append(info);const foot=node('div',null,'weather-source');const a=node('a','Open-Meteo ↗');a.href='https://open-meteo.com/';a.target='_blank';a.rel='noopener';foot.append(a);row.append(foot);container.append(row);
      });
      let clothes=past?'该日已结束；后续日期按各自预报与实际体感穿衣。':core.clothing(results);
      if(day.n<3)clothes=clothes.replace('外婆久坐按体感加腿毯，','');
      card.querySelector('[data-weather-advice="clothes"]').textContent=clothes;
      const strip=document.querySelector('[data-weather-strip="'+day.n+'"]');
      strip.querySelector('b').textContent=Number(day.date.slice(5,7))+'月'+Number(day.date.slice(8,10))+'日 · '+badge;
      strip.querySelector('span').textContent=day.locations.map((p,i)=>p.city+(p.optional?'（提前返杭）':'')+'：'+(results[i].available?results[i].low+'–'+results[i].high+'℃ · '+results[i].text:past?'日期已过':'预报待发布')).join('；');
      strip.querySelector('p').textContent=clothes;
    });
    checked.textContent=stamp(fetchedAt);source.textContent='来源：Open-Meteo · '+(cached?'上次成功缓存':'最新请求结果');coverage.textContent=readyCount+' / '+totalCount+'个地点日期有预报';
    document.getElementById('weather-coverage-note').textContent='其余为尚未完整发布或日期已过；不填成0℃或晴天。';
    status.textContent=(cached?'正在显示上次成功数据。':'全程天气已同步。')+' 最近同步：'+stamp(fetchedAt)+'（北京时间）；打开页面及每15分钟检查更新。';
    status.dataset.state=cached?'cached':'fresh';
  }
  function usableCache(value){
    if(!value||value.signature!==config.signature||!core.finite(value.fetchedAt)||value.fetchedAt>Date.now()+60000)return false;
    try{core.validate(value.payload,config.cities);return true;}catch(e){return false;}
  }
  try{const saved=JSON.parse(localStorage.getItem(cacheKey)||'null');if(usableCache(saved)){lastGood=saved;render(saved.payload,saved.fetchedAt,true);}}catch(e){}
  async function update(force){
    if(core.chinaDate(new Date())>config.endDate){
      clearInterval(pollTimer);button.hidden=true;status.textContent='本次行程日期已结束，页面停止自动请求天气。保留数据仅供回顾，请按卡片日期与最近同步时间辨别。';return;
    }
    if(inflight)return;
    if(!force&&lastGood&&Date.now()-lastGood.fetchedAt<interval)return;
    if(Date.now()-lastAttempt<30000)return;
    lastAttempt=Date.now();inflight=true;button.disabled=true;button.textContent='同步中…';status.textContent='正在同步全程8座城市的天气…';
    const abort=new AbortController(),timeout=setTimeout(()=>abort.abort(),15000);
    try{
      const response=await fetch(core.buildURL(config.cities),{signal:abort.signal,cache:'no-store',credentials:'omit',referrerPolicy:'no-referrer'});
      if(!response.ok)throw new Error('Weather HTTP '+response.status);
      const payload=core.validate(await response.json(),config.cities),fetchedAt=Date.now();
      // Valid structure with no usable trip data must not erase a previously useful forecast.
      const today=core.chinaDate(new Date());
      const any=config.days.some(d=>d.date>=today&&d.locations.some(p=>core.forecast(payload[config.cities.findIndex(c=>c.name===p.city)],d.date,today).available));
      if(!any&&today<=config.endDate)throw new Error('暂无可替换的完整预报');
      lastGood={payload,fetchedAt,signature:config.signature};render(payload,fetchedAt,false);
      try{localStorage.setItem(cacheKey,JSON.stringify(lastGood));}catch(e){}
    }catch(e){
      if(lastGood){render(lastGood.payload,lastGood.fetchedAt,true);status.textContent='暂时无法更新，保留上次成功数据（'+stamp(lastGood.fetchedAt)+'）。稍后会重试，也可查看下方中国天气网。';}
      else{status.textContent='自动同步暂时不可用，当前显示2026年9月20日的备用快照，不是最新天气。可稍后重试或打开各城官方预报。';source.textContent='备用来源：中国天气网 · 2026-09-20快照';}
      status.dataset.state='stale';
    }finally{clearTimeout(timeout);inflight=false;button.disabled=false;button.textContent='立即更新天气';}
  }
  button.addEventListener('click',()=>update(true));
  if(core.chinaDate(new Date())>config.endDate){
    status.textContent='本次行程日期已结束，页面停止自动请求天气。保留数据仅供回顾，请按卡片日期与最近同步时间辨别。';button.hidden=true;
  }else{
    update(false);pollTimer=setInterval(()=>{if(!document.hidden)update(false);},interval);
    document.addEventListener('visibilitychange',()=>{if(!document.hidden)update(false);});
    window.addEventListener('online',()=>update(false));
  }
})();
