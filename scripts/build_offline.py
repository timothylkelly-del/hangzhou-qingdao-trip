#!/usr/bin/env python3
"""Build a self-contained HTML handout using Python's standard library only."""
import base64
import hashlib
import json
import mimetypes
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'dist' / '杭州到大连_山海路书_v13_全程同行与自动天气_本地版.html'

class ResourceCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.anchors = []
        self.images = []
        self.fetches = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a' and attrs.get('href', '').startswith('#'):
            self.anchors.append(attrs['href'][1:])
        if tag == 'img':
            self.images.append(attrs)
        if tag in ('script', 'img', 'iframe', 'source', 'audio', 'video') and attrs.get('src'):
            self.fetches.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') in ('stylesheet','preload','modulepreload'):
            self.fetches.append(attrs.get('href', ''))

def embed(match):
    relative = match.group(1)
    path = (ROOT / relative).resolve()
    if ROOT not in path.parents or not path.is_file():
        raise ValueError(f'Invalid local resource: {relative}')
    mime = mimetypes.guess_type(path.name)[0]
    if not mime or not mime.startswith('image/'):
        raise ValueError(f'Expected an image: {relative}')
    payload = base64.b64encode(path.read_bytes()).decode('ascii')
    return f'src="data:{mime};base64,{payload}"'

page = (ROOT/'index.html').read_text(encoding='utf-8')
expected_assets=set()
for manifest in ('south','north','hotels'):
    data=json.loads((ROOT/f'data/photos-{manifest}.json').read_text())
    photos=data if isinstance(data,list) else data['photos']
    expected_assets.update(p['file'] for p in photos)
used_assets=set(re.findall(r'src="(assets/[^"\s]+)"',page))
assert expected_assets<=used_assets, 'Some sourced photos are absent from the roadbook'
page = re.sub(r'src="(assets/[^"\s]+)"', embed, page)
check = ResourceCheck()
check.feed(page)
assert len(check.ids) == len(set(check.ids)), 'Duplicate element ID'
assert set(check.anchors) <= set(check.ids), 'Broken in-page anchor'
content_images=[image for image in check.images if image.get('src')]
assert len(content_images) >= 45, 'Expected full-route scenery and lodging coverage'
assert all(image.get('alt') for image in content_images), 'Missing image alt text'
assert all(src.startswith('data:image/') for src in check.fetches), 'External or relative runtime resource'
assert len(set(image['src'] for image in content_images)) >= 40, 'Insufficient distinct photos'
assert not re.search(r'@import|url\s*\(', page), 'CSS resource requires review'
OUTPUT.parent.mkdir(exist_ok=True)
OUTPUT.write_text(page, encoding='utf-8')
print(f'Built: {OUTPUT}')
print(f'Bytes: {OUTPUT.stat().st_size:,}; embedded image placements: {len(content_images)}; unique resources: {len(set(i["src"] for i in content_images))}; external image/font/script files: 0; live weather requires network')
print(f'SHA256: {hashlib.sha256(OUTPUT.read_bytes()).hexdigest()}')
