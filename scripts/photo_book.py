"""Photographic chapters for the locally reviewed family roadbook."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def esc(value):
    return html.escape(str(value), quote=True)

def load_photos():
    photos = []
    for name in ('south', 'north', 'hotels'):
        path = ROOT / f'data/photos-{name}.json'
        if path.exists():
            payload = json.loads(path.read_text())
            photos.extend(payload if isinstance(payload, list) else payload['photos'])
    return photos

PHOTOS = load_photos()
BY_ID = {p['id']: p for p in PHOTOS}

def img(p, eager=False, cls=''):
    return (f'<img class="{cls}" src="{esc(p["file"])}" alt="{esc(p["alt"])}" '
            f'width="{p["width"]}" height="{p["height"]}" '
            f'loading="{"eager" if eager else "lazy"}" decoding="async">')

def figure(p, cls='', eager=False, caption=None):
    label = p.get('title', p['place'])
    photo_class = ' photo-portrait' if p['height'] > p['width'] else ''
    return (f'<figure class="travel-photo {cls}{photo_class}"><button type="button" class="photo-open" '
            f'data-photo="{esc(p["id"])}" aria-label="放大查看：{esc(label)}">{img(p,eager)}'
            '<span class="photo-zoom" aria-hidden="true">↗</span></button>'
            f'<figcaption><small class="photo-place">{esc(p["place"])}</small><strong>{esc(label)}</strong><span>{esc(caption or p["caption"])}</span>'
            f'<a class="photo-credit" href="{esc(p["source_url"])}" target="_blank" rel="noopener">'
            f'{esc(p["attribution"])} ↗</a></figcaption></figure>')

def city_photos(city):
    pool = [p for p in PHOTOS if not p.get('hotel_name') and city in p.get('city','')]
    leads={'杭州':'south-hangzhou-dusk','连云港':'south-sucheng-road','日照':'south-rizhao-greenway','青岛':'south-qd-skyline','莱州':'south-laizhou-goldcoast','威海':'north-liugong-island','烟台':'north-yantai-coast','大连':'north-dalian-square'}
    return sorted(pool,key=lambda p:p['id']!=leads.get(city))

def pick(city, index=0):
    pool = city_photos(city)
    return pool[index % len(pool)] if pool else None

CHAPTERS = [
 ('杭州','从熟悉的城市，驶向一家人的假期。','01 / 出发','西湖的水色留在身后，前方是山、海，还有等着相聚的家人。路上安排好休息，第一晚只需安心抵达。','D1 · 一家三口出发','d1'),
 ('连云港','山藏在云里，家住进小院里。','02 / 山间小住','在宿城停一晚，让长途驾驶有一个温柔的收尾。第二天看天气和宝宝精神，挑一段山海风景，再慢慢去日照。','D1—D2 · 宿城与海上云台山','d2'),
 ('日照','把玩耍的时间，留给沙滩和浪花。','03 / 海边童年','宝宝有一段认真玩沙的时间，大人也有坐下看海的空闲。乐园与海边择一慢玩，接站日早点出发。','D2—D3 · 海滨休息，准时接站','d3'),
 ('青岛','这一站，风景里终于有了全家人。','04 / 在青岛相聚','先到车站接人，再一起吃顿饭。海边的红瓦、城市的天际线和博物馆里的故事，挑大家都舒服的一段看。','D3—D4 · 29日14:34青岛站会合','d4'),
 ('莱州','走到莱州，把时间留给相聚。','05 / 胶东停一停','城区歇脚、家人团聚，再按当天状态选择海岸或地方文化。这里不用赶景点，有一餐好好坐在一起吃的饭，就很值得。','D5 · 先完成必须的事，再选短游','d5'),
 ('威海','海风吹过来，日子就慢下来。','06 / 向海的生活','找一段平整的滨海步道，给外婆留休息的位置，给宝宝留看海的兴致。刘公岛、荣成是可选分支，按体力与通行条件取舍。','D6—D7 · 市区慢游，上岛有条件','d7'),
 ('烟台','港城的一晚，为下一片海做准备。','07 / 跨海之前','海边城市值得短暂停留，但今天最重要的是住好、吃好、休息好。人和车各自确认好行程，再从容向大连出发。','D8—D9 · 先确认承运，再跨海','d8'),
 ('大连','海的另一边，还有一起看的风景。','08 / 相逢山海尽头','把星海湾、东港和亲子场馆各留成一个从容的选择。家属优先按期回杭州，随后你取到车，按最快高速回杭州。','D9—D11 · 家属返杭优先，7号收束','d10'),
]

def album():
    if not PHOTOS:
        return ''
    out = '<section class="photo-album chapter" id="album"><div class="album-heading"><div class="eyebrow">A journey to look forward to</div><h2>先看看，<br>我们要一起去的地方。</h2><p>从小院的晚风，到海边的日落。<br>风景慢慢看，日子一起过。</p></div><div class="album-jumps" aria-label="图文画册城市目录">'
    out += ''.join(f'<a href="#scene-{i}">{esc(c[0])}<span>↗</span></a>' for i,c in enumerate(CHAPTERS))
    out += '</div><p class="album-note">点击照片可放大。风光与房间实景用于了解目的地；可选景点不必全部走完，酒店照片也不代表已订房型。每天的安排和无障碍条件见后文。</p>'
    for i,(city,title,kicker,copy,tag,anchor) in enumerate(CHAPTERS):
        pool = city_photos(city)
        if not pool:
            continue
        out += f'<article class="city-spread" id="scene-{i}"><div class="spread-heading"><span class="spread-index">{i+1:02d}</span><div><small>{esc(kicker)}</small><h3>{esc(title)}</h3></div></div><div class="spread-intro"><p>{esc(copy)}</p><a href="#{anchor}">{esc(tag)} ↗</a></div><div class="scenery-grid scenery-count-{len(pool)}">'
        out += ''.join(figure(p,'scenery-card'+(' scenery-lead' if j==0 else '')) for j,p in enumerate(pool))
        out += '</div></article>'
    out += '<div class="family-quote"><span>FOR OUR FAMILY</span><p>不必把每一处风景都走遍，<br>但愿每一段回忆里，都有我们。</p><a href="#overview">带着期待，看看怎么出发 ↓</a></div></section>'
    return out

def cover():
    p = BY_ID.get('north-dalian-bangchuidao') or pick('威海')
    if not p:
        return ''
    return '<div class="cover-story">'+figure(p,'cover-photo',True,caption='把一次旅行，过成一家人共同的回忆。')+'<span class="cover-stamp">山海之间<br><b>FAMILY<br>JOURNEY</b></span></div>'

def day_photo(number):
    cities={4:'青岛',5:'莱州',6:'威海',7:'威海',8:'烟台',9:'大连',10:'大连',11:'杭州'}
    city=cities.get(number)
    if not city:return ''
    pool=[p for p in city_photos(city) if number in p.get('day_numbers',[])] or city_photos(city)
    if not pool:return ''
    chosen={4:'south-qd-naval',5:'south-laizhou-goldcoast',6:'north-weihai-haiyuan',7:'north-liugong-island',8:'north-yantai-coast',9:'north-dalian-square',10:'north-dalian-bay',11:'south-hangzhou-dusk'}
    p=BY_ID.get(chosen[number]) or pool[0]
    if number==11:
        p=dict(p,title='回到熟悉的杭州，把海风留在回忆里')
        note='杭州城市风光。太太、宝宝和妈妈最迟7号抵杭，回家休息，不增加游览。'
    else:
        note=p['caption']
    return figure(p,'day-photo',caption=note)

def hotel_photo(name):
    pool=[p for p in PHOTOS if p.get('hotel_name')==name]
    if name=='待确认车辆受理港后再选酒店':
        p=BY_ID.get('north-yantai-coast') or pick('烟台')
        return figure(p,'hotel-photo',caption='烟台城市风貌示意，非酒店实拍；酒店等车辆受理港确认后再选。') if p else ''
    return ''.join(figure(p,'hotel-photo') for p in pool[:2])

def dialog():
    return '''<dialog id="photo-dialog" aria-label="实景照片大图"><button class="photo-close" type="button" aria-label="关闭大图">关闭 ×</button><figure><img id="photo-large" alt=""><figcaption id="photo-description"></figcaption></figure></dialog>'''

def sources():
    out='<details class="sources photo-source-index"><summary>全程实景照片来源 · 地点与酒店对应索引</summary><p>图片来自链接所示的景区、酒店、政府或媒体页面；保留原始来源，未以其他城市、其他酒店或AI图冒充实景。图片是目的地参考，不代表出行当日的天气、房况或预约结果。</p><ul>'
    for p in PHOTOS:
        out+=f'<li><b>{esc(p.get("title",p["place"]))}</b> · <a href="{esc(p["source_url"])}" target="_blank" rel="noopener">{esc(p["attribution"])} ↗</a></li>'
    return out+'</ul></details>'
