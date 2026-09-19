"""Render live-weather hooks with an explicitly dated offline fallback."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/weather.json').read_text(encoding='utf-8'))

def esc(value):
    return html.escape(str(value), quote=True)

def date_label(value):
    return f'{int(value[5:7])}月{int(value[8:10])}日'

def link(url, title):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(title)} ↗</a>'

def conditions(item):
    if not item['available']:
        return '当天预报尚未覆盖'
    return f'{item["low_c"]}–{item["high_c"]}℃ · 白天{item["weather_day"]} / 夜间{item["weather_night"]}'

def strip(n):
    day = DATA['days'][n - 1]
    text = '；'.join(f'{item["city"]}{"（提前返杭）" if item.get("optional") else ""}：{conditions(item)}' for item in day['locations'])
    badge = '趋势参考' if any(item['available'] for item in day['locations']) else '待更新预报'
    return (f'<aside class="weather-strip" data-weather-strip="{n}" aria-label="D{n}天气与穿衣"><div><b>{date_label(day["date"])} · {badge}</b>'
            f'<span>{esc(text)}</span></div><p>{esc(day["clothes"])}</p>'
            f'<a href="#weather-d{n}">查看当天风雨、穿衣与备选 ↗</a></aside>')

def chapter():
    out = '''<section class="chapter" id="weather">
<div class="section-title"><h2>从出发到回家，<br>把每一站的冷暖放在心上。</h2><span>WEATHER ALONG THE WAY</span></div>
<p class="intro">2026年9月27日—10月7日 · 11天、8座城市。杭州 → 连云港宿城 → 日照 → 青岛 → 莱州 → 威海 → 烟台 ⇢ 大连 → 家属返杭。转场日同时看两地，海上那一段另外看风浪。</p>
<div class="weather-brief"><div><small>最近同步 · 北京时间</small><strong id="weather-synced-at">备用快照：9/20 00:03</strong><span id="weather-provider">正在连接天气数据</span></div><div><small>与行程日期逐一匹配</small><strong id="weather-coverage">全程8座城市</strong><span id="weather-coverage-note">尚未发布的日期自动等待，不挪用今天的天气</span></div><div><small>自动同步</small><strong>打开页面＋每15分钟</strong><span>支持手动更新；以天气源最新可用预报为准</span></div></div>
<div class="weather-live-controls"><p id="weather-live-status" role="status" aria-live="polite">正在获取全程天气；连接成功前显示2026年9月20日备用快照。</p><button id="weather-update" class="quiet-button" type="button">立即更新天气</button></div>
<p class="note"><strong>天气随预报更新：</strong>联网时自动向Open-Meteo获取各城市预报；打开页面、停留每15分钟或返回页面且缓存过期时检查。天气源按其模型周期更新，页面同步不是秒级实况。未发布或不完整的日期显示“待发布”，日期进入范围后自动补齐。更新失败保留上次数据并标注时间；无缓存时才用9月20日备用快照。温度是当日最低—最高，天气类型代表当日可能出现的主要情况，不代表全天如此。远期结果只作趋势，临行再查逐小时预报。</p>
<p class="mini">天气数据：<a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo</a> · <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>。中文整理、四舍五入和穿衣建议由路书生成；各城中国天气网链接保留在下方，便于交叉核对。首次打开需联网同步，浏览器缓存仅保存在当前设备。</p>
<p class="weather-date-warning" id="weather-date-warning" role="status" hidden>日历已调整：本章天气仍对应2026年9月27日—10月7日原计划，各卡片日期不会随日历移动。请按新日期重新查天气。</p>
<div class="weather-highlights"><p><b>出发与抵达，两地都看。</b>每个转场日同时显示两座城市，穿衣提示也随新预报调整；最低、最高温不能当成你正好出门时的气温。服务区、山地和海岸另看当地实况。</p><p><b>胶东到大连，防风层随身。</b>海边、码头和船舱的体感不同。给外婆备可脱保暖层和腿毯，宝宝备干衣；天气接口显示的城市风速不代表海面风浪或开航许可。</p></div>
<div class="weather-days">'''
    for day in DATA['days']:
        pending = all(not item['available'] for item in day['locations'])
        out += f'<article class="weather-day {"pending" if pending else ""}" id="weather-d{day["n"]}"><header><div><small>D{day["n"]:02d} · 2026</small><h3>{date_label(day["date"])}</h3></div><span class="weather-badge">{"预报待更新" if pending else "8—15天趋势"}</span></header><p class="weather-route">{esc(day["route"])}</p><div class="weather-locations">'
        for item in day['locations']:
            src = DATA['sources'][item['city']]
            out += f'<div class="weather-location"><div><b>{esc(item["city"])}</b><small>{"6日提前返杭时查" if item.get("optional") else esc(item.get("note", ""))}</small></div>'
            if item['available']:
                out += (f'<div><strong class="weather-temp">{item["low_c"]}–{item["high_c"]}<small>℃</small></strong>'
                        f'<p>白天{esc(item["weather_day"])} · 夜间{esc(item["weather_night"])}</p>'
                        f'<p class="weather-wind">昼：{esc(item["wind_day"])}<br>夜：{esc(item["wind_night"])}</p></div>')
            else:
                out += '<div><strong class="weather-unavailable">待更新</strong><p>当前来源仅覆盖到10月3日<br>当天温度、雨风尚无对应值</p></div>'
            out += f'<div class="weather-source">{link(src["url"], "官方预报")}</div></div>'
        out += '</div><dl class="weather-advice">'
        for key, label in [('clothes', '当天穿法'), ('care', '照顾家人'), ('backup', '天气备选')]:
            out += f'<div><dt>{label}</dt><dd data-weather-advice="{key}">{esc(day[key])}</dd></div>'
        out += f'</dl><a class="weather-itinerary" href="#d{day["n"]}">回到D{day["n"]}行程 ↗</a></article>'
    out += '''</div><div class="content-grid"><article class="panel"><h3>公路与山海，要多查一层</h3><p>这些是城市参考点。宿城山间、海上云台山景区、海边和高速沿线可能与城区不同；不能把两座城市的天气当成整段高速路况。9/26晚按实际导航核查杭州—苏北沿线预警，之后每次跨城出发前查沿途雨区、能见度与交通管制。</p><p>若临时去荣成或西霞口，另查当地预报；不直接套用威海市区数值。岛上项目还要核对景区船务与开放状态。</p></article><article class="panel"><h3>10/5跨海：人、车两张订单分别查</h3><p>本页城市天气自动更新，但不能据此判断10/5能否开航。10/3—4及5日出发前，核对渤海海峡、黄海北部相关海域风、浪与能见度，并向实际承运方确认客船和运车船运行、报到截止与两端港口。</p><p>城市“小于3级风”不等于海面同样风力。停航或延误时，太太、宝宝、妈妈的10/7抵杭期限优先；必要时留山东返杭，不等车。</p><p class="mini">'''
    out += link(DATA['marine_sources'][0]['url'], '中央气象台近海海区预报') + ' · ' + link(DATA['marine_sources'][1]['url'], '承运方官方入口')
    out += '''</p></article></div><div class="weather-refresh"><h3>接下来，在哪几个时间点再核对</h3><ol><li><b>9/24—26：</b>重新查全程城市，重点把9/27出发至9/29接站换成更近的逐日/逐小时预报；确认10/4—7是否已进入来源覆盖窗口。</li><li><b>每天晚饭后、次日出门前：</b>只核对“明天在哪＋路过哪＋是否去海边”，按真实雨风调整衣服和活动；阴雨就用室内备选。</li><li><b>10/3—5：</b>加查威海、烟台、大连与跨海海区，确认人车运输两端运行。不要只查烟台城区。</li><li><b>10/5—7：</b>同时查家属出发城市、杭州抵达时段及实际航班/列车运行；6日提前返杭也照此核对。</li></ol><p class="mini">城市天气在页面打开时自动同步；海况、停航、票务与景区开放仍须在上述节点单独核对。修改日期输入框只试排日历，不改既定天气日期。</p></div>'''
    out += '<details class="sources weather-sources"><summary>备用官方来源 · 9月20日快照说明</summary><ul class="source-index">'
    for city, src in DATA['sources'].items():
        out += f'<li>{link(src["url"], city+" · 中国天气网")}<br>查询：{esc(src["retrieved_at"])}；覆盖至{esc(src["forecast_until"])}。</li>'
    out += '</ul><p>连云港城区用于宿城区域趋势参考；具体山地与海边查当地更新。本地项目保留原始快照供核对；自动天气与该快照来源不同，比较时以页面标明的来源、日期和最近同步时间为准。</p></details></section>'
    locations = json.loads((ROOT / 'data/weather-locations.json').read_text(encoding='utf-8'))
    config = {'signature': 'v13-20260927-20261007', 'cities': locations['cities'], 'endDate': DATA['family_arrival_deadline'], 'days': [{'n': d['n'], 'date': d['date'], 'locations': [{k: v for k, v in item.items() if k in ('city','note','optional')} for item in d['locations']]} for d in DATA['days']]}
    out += '<script type="application/json" id="weather-config">' + json.dumps(config,ensure_ascii=False).replace('<','\\u003c') + '</script>'
    return out
