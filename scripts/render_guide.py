#!/usr/bin/env python3
"""Render the V13 shared roadbook from the preserved V8 design and editable content."""
import html
import json
import re
from collections import defaultdict
from pathlib import Path
import photo_book as photos
import weather_book as weather
from datetime import date, timedelta
ROOT=Path(__file__).resolve().parents[1]
def read(p): return (ROOT/p).read_text(encoding='utf-8')
def esc(s): return html.escape(str(s),quote=True)
plan=json.loads(read('data/guide.json'))
sources=json.loads(read('data/sources.json'))
def source(k):
    title,url=sources[k]
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(title)} ↗</a>'
def resolve(s): return re.sub(r'\{\{SRC:([a-z0-9]+)\}\}',lambda m:source(m[1]),s)
base=read('templates/v8-base.html')
style=re.search(r'<style>(.*?)</style>',base,re.S).group(1)+'\n'+read('templates/extension.css')+'\n'+read('templates/photobook.css')+'\n'+read('templates/weather.css')
days_intro=base[base.index('<section class="chapter" id="d1"'):base.index('<p class="quote">')]
days_intro=days_intro.replace('href="#stops"','href="#hotels"')
days_intro=days_intro.replace('海边慢一点，青岛见。','这天，先把家人接到。').replace('万平口 → 青岛<br>午后与朋友汇合','日照 → 青岛站<br>29 日 14:34 接 G881').replace('最后半天，<br>留给沙滩和早餐。','早一点出发，<br>给接站留足余量。').replace('今天不追景点数量。玩沙、吹风，再从容收好行李，把旅程交给下一场相聚。','森泊主要玩乐放在前一天下午。今天早餐后早出发，先到青岛站附近停好车，再等家人出站；沙滩只是有余量时的短停。')
old=re.search(r'(<section class="chapter day-three".*?<ol class="schedule">)(.*?)(</ol>)',days_intro,re.S)
new='''<li><time>07:00</time><div><b>早餐、整理行李</b><span>前一晚完成补能；不安排上午水乐园。</span></div></li><li><time>08:30–09:00</time><div><b>退房并出发</b><span>以13:30停车目标倒推；导航要求更早时就提前走。</span></div></li><li><time>13:30</time><div><b>青岛站周边停好车</b><span>确认社会车辆停车入口、出站会合点；留好停车位置。</span></div></li><li><time>14:34</time><div><b>迎接 G881 的家人</b><span>出站、洗手间和步行上车另留余量。<a href="#pickup">查看完整接站预案 ↗</a></span></div></li>'''
days_intro=days_intro[:old.start(2)]+new+days_intro[old.end(2):]
days_intro=days_intro.replace('早餐后进景区，上午只留给海上云台山，不追加连岛。云海是天气给的惊喜，不是必须打卡的任务；能见度差时，宁可把节奏放慢。','这段仍是一家三口。5岁宝宝按体力选短线，景区交通和开放入口先确认；不追加连岛。天气不好或孩子累了，可删去登山，早些到日照休息。')
days_intro=days_intro.replace('万平口 · 第三天上午','万平口 · 接站日前，适量留白')
days_intro=re.sub(r'<span class="photo-index">\d+ / 04</span>','',days_intro)
days_intro=re.sub(r'<img\b[^>]*>',lambda m:'<button type="button" class="photo-open" data-photo="original-'+re.search(r'src="[^"]*/([^"/]+)"',m[0]).group(1)+'" aria-label="放大查看：'+re.search(r'alt="([^"]*)"',m[0]).group(1)+'">'+m[0]+'<span class="photo-zoom" aria-hidden="true">↗</span></button>',days_intro)
for n in range(1,4):
    pattern = r'(<section[^>]*id="d'+str(n)+r'".*?</header>)'
    days_intro = re.sub(pattern, lambda m: m[1]+weather.strip(n), days_intro, count=1, flags=re.S)
def day_date(n):
    value=date.fromisoformat(plan['start_date'])+timedelta(days=n-1)
    return f'{value.month}月{value.day}日'
rows=[]
for d in plan['days']:
    n=d['n']; link=d.get('link',f'd{n}')
    rows.append(f'<tr class="{"anchor-row" if n==3 else ""}"><td><b>D{n:02d}</b><small data-day-date="{n}">{day_date(n)}</small></td><td><a href="#{link}"><strong>{esc(d["city"])}</strong><br>{esc(d["key"])} ↗</a></td><td>{esc(d["sleep"])}</td></tr>')
intro=read('templates/plan.html').replace('{{OVERVIEW_ROWS}}',''.join(rows))
intro=intro.replace('以下时间均为建议时段，车船票未预订。','G881 接站按你提供的信息及匹配日期查询保留，其他游玩时段为建议。本项目尚未代订后续交通与住宿，已有订单请另行核对。')
extended='''<section class="chapter" id="journey"><div class="section-title"><h2>从青岛，把旅程继续向北。</h2><span>DAY BY DAY</span></div><p class="intro">主表按尽量同游大连倒排：接站后青岛一个完整轻游日，再经莱州、威海和烟台；太太、宝宝、妈妈最迟10月7日到杭。7号之后其他亲属自行决定行程；你取到车后走最快高速返杭，不再追加游玩。全团以轮椅可达、短时活动为先。</p><div class="day-tools"><span class="mini">点开每一天，查看吃饭休息、交通会合和备用方案</span><div><button class="quiet-button" id="expand-days" type="button">展开全部</button> <button class="quiet-button" id="collapse-days" type="button">收起全部</button></div></div>'''
for d in plan['days'][3:]:
    n=d['n']
    extended+=f'<article class="day-story" id="d{n}">'+photos.day_photo(n)+weather.strip(n)+f'<details class="day-card" {"open" if n==4 else ""}><summary><span class="day-no">{n:02d}<small data-day-date="{n}">{day_date(n)}</small></span><span class="day-summary"><strong>{esc(d["city"])}</strong><span>{esc(d["theme"])} · {esc(d["sleep"])}</span></span></summary><div class="day-content"><div class="daily-periods">'
    for field,label in [('morning','上午 / AM'),('noon','午餐与休息 / MIDDAY'),('afternoon','下午 / PM'),('evening','晚间 / EVENING')]:
        extended+=f'<div class="period"><b>{label}</b><p>{esc(d[field])}</p></div>'
    extended+='</div><div class="day-meta">'
    for field,label in [('transport','两组怎么走，在哪里会合'),('fallback','当天的备用方案')]:
        extended+=f'<div><b>{label}</b><p>{esc(d[field])}</p></div>'
    extended+=f'</div><p class="mini"><b>预订 / 取舍：</b>{esc(d["booking"])}</p><p class="mini">核验入口：'+ ' · '.join(source(k) for k in d['sources'])+'</p></div></details></article>'
extended+='</section>'
hotels='<section class="chapter" id="hotels"><div class="section-title"><h2>住在哪里，比打几个卡更重要。</h2><span>STAY WELL</span></div><p class="intro">以下为真实酒店或区域候选，按行程位置和需求筛选，尚未代表你的最终订单。人数按9成人与1名5岁宝宝预留，预算与房型待定，房价按真实日期比较；品牌档次也不保证当日价格。青岛与大连尽量连续住一家；10人团队优先按5间房比选，外婆房间先落实完整无台阶动线。</p><p class="note">当前推荐落脚方式：宿城八间房 → 日照森泊 → 青岛五四广场/浮山所一带 → 莱州城区 → 威海市区 → 烟台实际受理港附近 → 大连星海或东港二选一。酒店有停车位与有可用充电桩，要分别确认。</p>'
groups=defaultdict(list)
for h in json.loads(read('data/hotels.json')):groups[h['city']].append(h)
for city,items in groups.items():
    hotels+=f'<div class="hotel-group"><h3>{esc(city)}</h3><div class="hotel-grid">'
    for h in items:
        hotels+='<article class="hotel">'+photos.hotel_photo(h['name'])+f'<small>{esc(h["type"])}</small><h4>{esc(h["name"])}</h4><p><b>{esc(h["position"])}</b></p><p>{esc(h["why"])}</p><p class="hotel-check"><b>预订前确认：</b>{esc(h["check"])}</p><a href="{esc(h["url"])}" target="_blank" rel="noopener">查看酒店/官方资料 ↗</a>'
        if city!='烟台': hotels+=f'<button type="button" class="copy-button" data-copy="{esc(h["name"])} {esc(h["position"])}">复制候选名称<span>↗</span></button>'
        hotels+='</article>'
    hotels+='</div></div>'
hotels+='</section>'
ready=base[base.index('<section class="preflight shell"'):base.index('</main>')]
ready=ready.replace('ETC、胎压、玻璃水、车辆续航与补能计划','MEGA的ETC、胎压、玻璃水、实时续航与快充主备站').replace('两晚住宿、乐园权益、退房和停车安排','各城住宿、儿童入住人数、乐园权益与取消期限').replace('景区开放、出发前天气、青岛会合定位','G881票面、青岛站停车入口和出站会合点').replace('约定的出发时间、需要带的东西、青岛会合地点……','记录已确认日期、MEGA年款、同行分组、港口确认、酒店与紧急联系人；不要填写证件号或验证码……')
extra=[('tickets','理想MEGA纯电承运与配套客船：行驶证尺寸、电量要求、两端港口和取车时间'),('bags','每组独立的随身过夜包；船上必需物不留汽车里'),('rail','铁路组真实到发站、同站换乘余量、到酒店接驳'),('ferryweather','登船前48小时及当天复核天气、停航和两张订单'),('medical','过敏/既往病史、医嘱用品、附近急诊和紧急电话'),('return','太太宝宝妈妈最迟7日到杭州的已确认交通；你的带车返程独立安排'),('wheelchair','外婆轮椅：车辆、酒店、景区、船机全过程无障碍确认'),('party','10人座位与行李容量，分组陪护与家属返程交接')]
ready=ready.replace('<p class="progress"', ''.join(f'<label><input type="checkbox" data-check="{k}"><span>{v}</span></label>' for k,v in extra)+'<p class="progress"').replace('已准备 0 / 6 项','已准备 0 / 14 项')
photo_sources=base[base.index('<details class="sources">'):base.index('</details>')+len('</details>')]
photo_sources=photo_sources.replace('照片与地图来源','原有照片与离线地图来源').replace('住宿地为区域示意，非精确门牌导航。','宿城、日照、莱州、威海、烟台、大连为区域示意；连线不是行车路线、精确码头或船舶航迹。')
source_list='<details class="sources"><summary>行程与安全资料索引 · 核验日 2026-09-19</summary><p>推荐的游玩时长、删减顺序、住宿取舍由本路书按家庭节奏规划；链接用于核验地点、设施或规则，不代表当天房票余量。临行优先查最新公告。</p><ul class="source-index">'+''.join('<li>'+source(k)+'</li>' for k in sources)+'</ul></details>'
hero='''<header class="mast"><div class="shell"><a class="brand" href="#top">山海之间 · 家庭路书</a><span class="edition">VOL. 13 / OUR FAMILY JOURNEY</span></div></header><main id="top"><div class="shell"><section class="hero" aria-labelledby="cover-title"><div><div class="eyebrow">From Hangzhou, all the way to Dalian</div><h1 id="cover-title">一路向北，<br>在<em>山海</em>相聚。</h1><p class="lead">山间的小院、胶东的海风、海的另一边。先接上家人，再把这些风景慢慢看进记忆里。10个人的旅行，有宝宝的笑声，也有外婆坐下来歇脚的时光。</p><div class="hero-actions"><a href="#album">先看全程风景 ↓</a><a href="#overview">查看每日安排 ↗</a></div><div class="route-line"><b>杭州</b><i>→</i><b>宿城</b><i>→</i><b>日照</b><i>→</i><b>青岛</b><i>→</i><b>莱州</b><i>→</i><b>威海</b><i>→</i><b>烟台</b><i>⇢</i><b>大连</b></div></div><figure class="cover-map" id="map"><img src="assets/route-map.svg" alt="杭州经宿城、日照、青岛到莱州，再往威海，经烟台跨海到大连的区域地理示意。实线示陆地顺序，虚线示跨海段，不是导航轨迹。" width="500" height="680"><figcaption class="map-caption">去程顺序按最新讨论展开。北方在上；图示为区域位置和行程顺序，实际道路与港口以导航、票面为准。</figcaption></figure></section><section class="fact-strip" aria-label="行程速览"><div><small>RENDEZVOUS / 接站</small><strong>9月29日 · G881 · 14:34</strong></div><div><small>PARTY / 同行规模</small><strong>10人同行 · 9.27—10.7</strong></div><div><small>ACCESS / 全团出行</small><strong>轮椅长者 · 无障碍先核实</strong></div><div><small>DEADLINE / 返杭硬节点</small><strong>家属最迟10月7日到杭州</strong></div></section></div><nav class="nav" aria-label="路书目录"><div class="shell"><a href="#album">山海画册</a><a href="#overview">全程总览</a><a href="#weather">全程天气</a><a href="#clothing">穿衣装箱</a><a href="#pickup">29日接站</a><a href="#deadline">7日返杭</a><a href="#party">10人分组</a><a href="#d1">杭州出发</a><a href="#journey">每日细案</a><a href="#choices">景区取舍</a><a href="#transport">分组交通</a><a href="#ferry">跨海方案</a><a href="#hotels">住进风景</a><a href="#driver-return">高速返杭</a><a href="#emergency">应急备案</a><a href="#booking">预订预算</a><a href="#ready">随身清单</a></div></nav><div class="shell">'''
# Keep the map available while giving the cover to a real destination photograph.
old_map=re.search(r'<figure class="cover-map".*?</figure>',hero,re.S)
map_fold='<details class="map-fold"><summary>展开完整路线地图 · 杭州到大连</summary>'+old_map.group(0)+'</details>'
if photos.cover(): hero=hero[:old_map.start()]+photos.cover()+hero[old_map.end():]
driver_return='''<section class="chapter" id="driver-return"><div class="section-title"><h2>家人到家，你走最快高速返杭。</h2><span>HOMEWARD</span></div><p class="intro">路书在太太、宝宝和妈妈最迟7号抵达杭州时收束。7号之后其他亲属自行决定行程，不再安排；你的返程只赶路，不增加游玩、固定日序或指定中途城市。</p><div class="content-grid"><article class="panel"><h3>车辆到手，导航杭州</h3><p>从车辆实际所在位置设置杭州最终目的地，出发前刷新路况，选择合法可行的最快高速路线。默认陆路返杭，不再倒排返向船期；不沿途打卡。</p></article><article class="panel"><h3>只留必要的驾驶安排</h3><p>落实三名家属的独立返杭交通，车辆交接完成且休息充分后即可出发；家属到杭后报平安。快充补能、用餐、休息与必要夜宿按当天进度决定；不用追7号期限，也不以连续夜驾压缩时间。</p></article></div></section>'''
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f5f2e9"><meta name="description" content="杭州出发，青岛站接G881，续行莱州、威海、烟台、大连。含详细亲子日程、分组交通、新能源车跨海、住宿与应急预案的本地审阅路书。"><title>一路向北，在山海相聚｜杭州到大连 · 路书13 · 全程同行与自动天气</title><style>'''+style+'</style></head><body><a class="skip" href="#pickup">跳到接站计划</a>'+hero+photos.album()+map_fold+intro+weather.chapter()+read('templates/clothing.html')+read('templates/deadline.html')+read('templates/party.html')+days_intro+'<p class="extended-intro">从一次相聚开始，<br>把下一段旅程，留给更远的海。</p>'+extended+driver_return+read('templates/attractions.html')+read('templates/logistics.html')+read('templates/ferry.html')+read('templates/accessibility.html')+hotels+read('templates/safety.html')+'</div>'+ready+'''</main><footer class="footer"><div class="shell"><div class="footer-top"><b>杭州 → 青岛 → 莱州 → 威海 → 烟台 ⇢ 大连</b><span>有计划，也留余地。</span></div><p class="colophon">家庭共享版 13 · 2026-09-20 更新 · 城市天气自动同步<br>2026年9月27日出发、9月29日接站、10月7日家属抵杭已确认；名单余项、车辆年款、行驶证信息及轮椅交通细节仍待补齐。建议时段不等于车船班次；实际票面、天气和承运确认优先。</p>'''+source_list+photos.sources()+photo_sources+'</div></footer><noscript><p class="no-js-note">当前预览器未运行脚本：正文和展开内容仍可阅读，日期、费用计算与本机保存请用浏览器打开。</p></noscript><div id="toast" role="status" aria-live="polite"></div>' +photos.dialog()+'<script>'+read('scripts/guide.js')+'\n'+read('scripts/weather-core.js')+'\n'+read('scripts/weather-live.js')+'</script></body></html>'
page=resolve(page)
assert '{{' not in page,'Unresolved template token'
(ROOT/'index.html').write_text(page,encoding='utf-8')
print(f'Rendered {len(page):,} characters; {len(plan["days"])} itinerary rows; {sum(map(len,groups.values()))} hotel/area candidates.')
