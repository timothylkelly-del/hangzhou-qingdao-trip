(function(root,factory){
  const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.TripWeather=api;
})(typeof window==='object'?window:globalThis,function(){
  'use strict';
  const fields=['weather_code','temperature_2m_max','temperature_2m_min','precipitation_probability_max','precipitation_sum','wind_speed_10m_max','wind_gusts_10m_max','wind_direction_10m_dominant'];
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  const round=v=>finite(v)?Math.round(v):null;
  function chinaDate(now){return new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'}).format(now);}
  function weatherText(code){
    return ({0:'晴',1:'大部晴朗',2:'局部多云',3:'阴',45:'雾',48:'雾凇',51:'小毛毛雨',53:'毛毛雨',55:'较强毛毛雨',56:'冻毛毛雨',57:'较强冻毛毛雨',61:'小雨',63:'中雨',65:'大雨',66:'冻雨',67:'较强冻雨',71:'小雪',73:'中雪',75:'大雪',77:'雪粒',80:'小阵雨',81:'阵雨',82:'强阵雨',85:'小阵雪',86:'强阵雪',95:'雷暴',96:'雷暴伴冰雹',99:'强雷暴伴冰雹'})[code]||'天气类型待确认';
  }
  function direction(value){return finite(value)?['北','东北','东','东南','南','西南','西','西北'][Math.round(((value%360)+360)%360/45)%8]+'风':'风向待更新';}
  function forecast(data,date,today){
    if(date<today)return {available:false,past:true};
    const d=data&&data.daily,i=d&&Array.isArray(d.time)?d.time.indexOf(date):-1;
    const value=key=>i>=0&&Array.isArray(d[key])?d[key][i]:null;
    const low=value('temperature_2m_min'),high=value('temperature_2m_max'),code=value('weather_code');
    if(!finite(low)||!finite(high)||!finite(code)||low>high||low< -80||high>65)return {available:false,past:false};
    const days=Math.round((Date.parse(date+'T00:00:00Z')-Date.parse(today+'T00:00:00Z'))/86400000);
    return {available:true,past:false,low:round(low),high:round(high),code,text:weatherText(code),rain:round(value('precipitation_probability_max')),rainMM:value('precipitation_sum'),wind:round(value('wind_speed_10m_max')),gust:round(value('wind_gusts_10m_max')),direction:direction(value('wind_direction_10m_dominant')),trend:days>=7};
  }
  function clothing(items){
    const ready=items.filter(x=>x.available);if(!ready.length)return '当天预报尚未完整发布：薄长袖、可脱保暖中层、防风雨外套都备好，临近再按活动时段穿脱。';
    const low=Math.min(...ready.map(x=>x.low)),high=Math.max(...ready.map(x=>x.high));
    let text=high>=28?'白天较暖时以透气薄上衣为主，外套随身；':high>=23?'薄上衣或薄长袖，备可脱的轻外套；':'薄长袖配轻外套，长裤和包脚鞋；';
    text+=low<12?'早晚降温时加保暖中层，怕冷者备轻量棉服；':low<18?'早晚备薄抓绒或开衫，海边再加防风层；':'海边与候船时备防风层，车内暖和就减层；';
    if(ready.some(x=>(finite(x.rain)&&x.rain>=40)||(x.code>=51&&x.code<=99)))text+='带防雨外层和干袜；';
    if(ready.some(x=>(finite(x.wind)&&x.wind>=25)||(finite(x.gust)&&x.gust>=40)))text+='风较明显时缩短海边停留；';
    text+='外婆久坐按体感加腿毯，宝宝活动热了及时减层。';
    if(ready.length<items.length)text+=' 另一地点仍待预报，先保留备用层。';
    return text;
  }
  function buildURL(cities){
    const params=new URLSearchParams({latitude:cities.map(x=>x.lat).join(','),longitude:cities.map(x=>x.lon).join(','),daily:fields.join(','),timezone:'Asia/Shanghai',forecast_days:'16',wind_speed_unit:'kmh',temperature_unit:'celsius',precipitation_unit:'mm'});
    return 'https://api.open-meteo.com/v1/forecast?'+params;
  }
  function validate(payload,cities){
    if(!Array.isArray(payload)||payload.length!==cities.length)throw new Error('城市数据不完整');
    payload.forEach((p,i)=>{
      if(!p||!finite(p.latitude)||!finite(p.longitude)||Math.abs(p.latitude-cities[i].lat)>0.6||Math.abs(p.longitude-cities[i].lon)>0.6||p.timezone!=='Asia/Shanghai')throw new Error('城市或时区不匹配');
      if(!p.daily||!Array.isArray(p.daily.time)||!p.daily.time.length||!p.daily.time.every(d=>/^\d{4}-\d{2}-\d{2}$/.test(d)))throw new Error('日期数据不完整');
      if(p.daily_units?.temperature_2m_max!=='°C'||p.daily_units?.temperature_2m_min!=='°C'||p.daily_units?.wind_speed_10m_max!=='km/h'||p.daily_units?.wind_gusts_10m_max!=='km/h')throw new Error('天气单位不匹配');
      ['temperature_2m_min','temperature_2m_max','weather_code'].forEach(k=>{if(!Array.isArray(p.daily[k])||p.daily[k].length!==p.daily.time.length)throw new Error('天气字段不完整');});
    });return payload;
  }
  return {finite,forecast,clothing,buildURL,validate,chinaDate,weatherText};
});
