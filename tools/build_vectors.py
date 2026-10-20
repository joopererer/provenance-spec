import json, os, hashlib
from xml.sax.saxutils import escape
from PIL import Image, PngImagePlugin

ROOT = os.path.join(os.path.dirname(__file__), "..")
TV = os.path.join(ROOT, "test-vectors")
NS = "https://joopererer.github.io/provenance-spec/ns/"


def w(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def wjson(rel, obj):
    w(rel, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def xmp_packet(r, foreign=False):
    s = r.get("source") or {}
    attrs = [
        f'prov:schema="{r["schema"]}"',
        f'prov:assetId="{r["assetId"]}"',
        f'prov:capturedAt="{r["capturedAt"]}"',
        f'prov:capturedBy="{escape(r["capturedBy"])}"',
        f'xmp:MetadataDate="{r["metadataDate"]}"',
    ]
    if s:
        attrs.append(f'prov:sourceUrl="{escape(s["url"])}"')
        attrs.append(f'prov:platform="{s["platform"]}"')
        if s.get("id"):
            attrs.append(f'prov:sourceId="{escape(s["id"])}"')
        for k, x in [("itemIndex", "itemIndex"), ("itemCount", "itemCount"), ("authorId", "authorId"),
                     ("publishedAt", "publishedAt"), ("pairId", "pairId")]:
            if s.get(k) is not None:
                attrs.append(f'prov:{x}="{escape(str(s[k]))}"')
        attrs.append(f'dc:source="{escape(s["url"])}"')
    if r.get("rating") is not None:
        attrs.append(f'xmp:Rating="{r["rating"]}"')
    if foreign:
        attrs.append('photoshop:Headline="Foreign field that must be preserved"')
    body = []
    if r.get("title"):
        body.append(f'<dc:title><rdf:Alt><rdf:li xml:lang="x-default">{escape(r["title"])}</rdf:li></rdf:Alt></dc:title>')
    if r.get("creator"):
        body.append("<dc:creator><rdf:Seq>" + "".join(f"<rdf:li>{escape(c)}</rdf:li>" for c in r["creator"]) + "</rdf:Seq></dc:creator>")
    if r.get("description"):
        body.append(f'<dc:description><rdf:Alt><rdf:li xml:lang="x-default">{escape(r["description"])}</rdf:li></rdf:Alt></dc:description>')
    if r.get("subject"):
        body.append("<dc:subject><rdf:Bag>" + "".join(f"<rdf:li>{escape(t)}</rdf:li>" for t in r["subject"]) + "</rdf:Bag></dc:subject>")
    nsdecl = (f'xmlns:prov="{NS}" xmlns:dc="http://purl.org/dc/elements/1.1/" '
              'xmlns:xmp="http://ns.adobe.com/xap/1.0/"')
    if foreign:
        nsdecl += ' xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"'
    a = "\n    ".join(attrs)
    b = "\n   ".join(body)
    return (
        '<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/">\n'
        ' <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
        f'  <rdf:Description rdf:about="" {nsdecl}\n    {a}>\n   {b}\n  </rdf:Description>\n'
        ' </rdf:RDF>\n</x:xmpmeta>\n<?xpacket end="w"?>'
    )


# ---------- records ----------
XHS = {
    "schema": "0.1",
    "assetId": "3f0c6a2e-8d4b-4c1a-9a3e-2b7f5d9e1c40",
    "capturedAt": "2026-10-20T15:30:00+02:00",
    "capturedBy": "EasySave/1.7.0",
    "metadataDate": "2026-10-20T15:30:00+02:00",
    "source": {"url": "https://www.xiaohongshu.com/explore/6ad2f7050000000012034042", "platform": "xiaohongshu",
               "id": "6ad2f7050000000012034042", "itemIndex": 3, "itemCount": 9,
               "authorId": "5f1a2b3c000000000100abcd", "publishedAt": "2026-10-18T09:12:00+08:00", "pairId": None},
    "title": "wow～ 好干净的奶白色",
    "creator": ["示例作者"],
    "description": "示例正文 & 特殊字符 <测试> \"引号\"",
    "subject": ["家居", "奶白色"],
    "rating": 4,
}
IG = {
    "schema": "0.1",
    "assetId": "9b2d4e61-7c3a-4f8e-b1d2-5a6c7e8f9012",
    "capturedAt": "2026-10-20T16:00:00Z",
    "capturedBy": "OnlineAlbumPlugin/2.3.0",
    "metadataDate": "2026-10-21T08:00:00Z",
    "source": {"url": "https://www.instagram.com/p/Ddl1WWnGyCN/", "platform": "instagram", "id": "Ddl1WWnGyCN",
               "itemIndex": 2, "itemCount": 6, "authorId": None, "publishedAt": None, "pairId": None},
    "title": None, "creator": ["example.account"], "description": None, "subject": ["inspiration"], "rating": None,
}
X = {
    "schema": "0.1",
    "assetId": "c4e5f6a7-b8c9-4d0e-8f1a-2b3c4d5e6f70",
    "capturedAt": "2026-10-20T17:45:10+02:00",
    "capturedBy": "EasySave/1.7.0",
    "metadataDate": "2026-10-20T17:45:10+02:00",
    "source": {"url": "https://x.com/i/status/2111025862892269612", "platform": "x", "id": "2111025862892269612",
               "itemIndex": None, "itemCount": None, "authorId": None, "publishedAt": None, "pairId": None},
    "title": None, "creator": ["example_user"], "description": "Single-image tweet", "subject": None, "rating": None,
}
LOCAL = {
    "schema": "0.1",
    "assetId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
    "capturedAt": "2026-10-20T18:00:00+02:00",
    "capturedBy": "FileOrganizer/2.0.0",
    "metadataDate": "2026-10-22T10:00:00+02:00",
    "source": None,
    "title": "旅行照片", "creator": None, "description": None, "subject": ["旅行", "2025"], "rating": 5,
}


def clean(r):
    out = {k: v for k, v in r.items() if v is not None}
    if out.get("source"):
        out["source"] = {k: v for k, v in out["source"].items() if v is not None}
    return out


def img(seed):
    im = Image.new("RGB", (64, 48))
    px = im.load()
    for y in range(48):
        for x in range(64):
            px[x, y] = ((x * 4 + seed * 40) % 256, (y * 5 + seed * 70) % 256, ((x + y) * 3 + seed * 20) % 256)
    return im


os.makedirs(TV, exist_ok=True)
cases = []

# JPEG with foreign field (preservation test)
p = os.path.join(TV, "xhs-item3.jpg")
img(1).save(p, "JPEG", quality=92, xmp=xmp_packet(XHS, foreign=True).encode("utf-8"))
wjson("test-vectors/xhs-item3.jpg.expected.json", clean(XHS))
cases.append(("xhs-item3.jpg", "JPEG，多图笔记第 3 张，含特殊字符；另含 photoshop:Headline 外来字段，写入后必须保留"))

# PNG
p = os.path.join(TV, "ig-item2.png")
info = PngImagePlugin.PngInfo()
info.add_itxt("XML:com.adobe.xmp", xmp_packet(IG), zip=False)
img(2).save(p, "PNG", pnginfo=info)
wjson("test-vectors/ig-item2.png.expected.json", clean(IG))
cases.append(("ig-item2.png", "PNG iTXt，用户字段较新（metadataDate 晚于 capturedAt）"))

# WebP
p = os.path.join(TV, "x-single.webp")
img(3).save(p, "WEBP", lossless=True, xmp=xmp_packet(X).encode("utf-8"))
wjson("test-vectors/x-single.webp.expected.json", clean(X))
cases.append(("x-single.webp", "WebP XMP 块，单项来源（无 itemIndex）"))

# Sidecar for a video-like file (content irrelevant)
with open(os.path.join(TV, "local-video.mp4"), "wb") as f:
    f.write(b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2" + b"\x00" * 32)
w("test-vectors/local-video.mp4.xmp", xmp_packet(LOCAL))
wjson("test-vectors/local-video.mp4.expected.json", clean(LOCAL))
cases.append(("local-video.mp4 + local-video.mp4.xmp", "边车文件；本地导入，无来源；占位 MP4 仅用于验证边车命名"))

# No metadata
p = os.path.join(TV, "no-metadata.jpg")
img(4).save(p, "JPEG", quality=92)
with open(p, "rb") as f:
    sha = hashlib.sha256(f.read()).hexdigest()
wjson("test-vectors/no-metadata.jpg.expected.json", {"_none": True, "sha256": sha})
cases.append(("no-metadata.jpg", "无元数据：读取结果为空；去重时使用文件 SHA-256（见 expected 中的 sha256）"))

# URL normalization
urls = [
    {"in": "https://www.xiaohongshu.com/discovery/item/6ad2f7050000000012034042?source=yamcha_homepage&xsec_token=ABCDEF123&xsec_source=h5_feed&type=normal",
     "out": "https://www.xiaohongshu.com/explore/6ad2f7050000000012034042", "platform": "xiaohongshu", "id": "6ad2f7050000000012034042"},
    {"in": "https://www.xiaohongshu.com/explore/6ad09b08000000000a024c55?app_platform=android&ignoreEngage=true&app_version=9.50.0&share_from_user_hidden=true&xsec_source=app_share&type=video&xsec_token=FAKE&author_share=1&xhsshare=CopyLink&shareRedId=FAKE&apptime=1792365888&share_id=FAKE&share_channel=copy_link&track_code=FAKE",
     "out": "https://www.xiaohongshu.com/explore/6ad09b08000000000a024c55", "platform": "xiaohongshu", "id": "6ad09b08000000000a024c55"},
    {"in": "https://www.instagram.com/p/DejQyvMmvVO/?img_index=4&xtok=FAKE",
     "out": "https://www.instagram.com/p/DejQyvMmvVO/", "platform": "instagram", "id": "DejQyvMmvVO"},
    {"in": "https://www.instagram.com/reel/DbU8Jo5uP3-/?igsh=FAKE",
     "out": "https://www.instagram.com/p/DbU8Jo5uP3-/", "platform": "instagram", "id": "DbU8Jo5uP3-"},
    {"in": "https://x.com/eric_sayompoo/status/2111025862892269612?s=20&t=FAKE",
     "out": "https://x.com/i/status/2111025862892269612", "platform": "x", "id": "2111025862892269612"},
    {"in": "https://twitter.com/someone/status/2111657987697971696/photo/1",
     "out": "https://x.com/i/status/2111657987697971696", "platform": "x", "id": "2111657987697971696"},
    {"in": "https://drive.google.com/file/d/1AbCdEfGhIjKlMnOpQrStUvWxYz012345/view?usp=sharing",
     "out": "https://drive.google.com/file/d/1AbCdEfGhIjKlMnOpQrStUvWxYz012345/view", "platform": "gdrive", "id": "1AbCdEfGhIjKlMnOpQrStUvWxYz012345"},
    {"in": "https://Example.COM/articles/42?utm_source=newsletter&utm_medium=email&page=2#comments",
     "out": "https://example.com/articles/42?page=2", "platform": "web", "id": None},
    {"in": "https://example.com/gallery?fbclid=FAKE&gclid=FAKE&si=FAKE",
     "out": "https://example.com/gallery", "platform": "web", "id": None},
]
wjson("test-vectors/urls.json", {"note": "短链（xhslink.com、t.co、vm.tiktok.com）需要联网展开，不放入离线用例；实现应先展开再规范化。所有 FAKE 值均为虚构。", "cases": urls})

w("test-vectors/README.md", "# 测试用例\n\n" + "\n".join(f"- `{n}`：{d}" for n, d in cases) + "\n- `urls.json`：链接规范化用例\n\n"
  "每个 `*.expected.json` 是按 SPEC 第 7 节 JSON 表示读出的期望结果（省略缺失字段）。\n\n"
  "一致性要求见 SPEC 第 10 节。图片由 `tools/build_vectors.py` 生成；**不要手工修改这些文件**，需要修改时改脚本重新生成并在 CHANGELOG 中说明。\n")

# ---------- schema ----------
date = {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2}))?$"}
schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://joopererer.github.io/provenance-spec/schema/0.1/provenance.schema.json",
    "title": "Provenance Metadata 0.1 (JSON representation)",
    "type": "object",
    "required": ["schema", "assetId", "capturedAt", "capturedBy"],
    "properties": {
        "schema": {"type": "string", "pattern": r"^\d+\.\d+$"},
        "assetId": {"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"},
        "capturedAt": date, "capturedBy": {"type": "string", "minLength": 1}, "metadataDate": date,
        "source": {
            "type": ["object", "null"],
            "required": ["url", "platform"],
            "properties": {
                "url": {"type": "string", "format": "uri"},
                "platform": {"type": "string", "pattern": "^[a-z0-9_-]+$"},
                "id": {"type": ["string", "null"]},
                "itemIndex": {"type": ["integer", "null"], "minimum": 1},
                "itemCount": {"type": ["integer", "null"], "minimum": 1},
                "authorId": {"type": ["string", "null"]},
                "publishedAt": {"anyOf": [date, {"type": "null"}]},
                "pairId": {"type": ["string", "null"]},
            },
            "additionalProperties": True,
        },
        "title": {"type": ["string", "null"]},
        "creator": {"type": ["array", "null"], "items": {"type": "string"}},
        "description": {"type": ["string", "null"], "maxLength": 2000},
        "subject": {"type": ["array", "null"], "items": {"type": "string"}},
        "rating": {"type": ["integer", "null"], "minimum": 0, "maximum": 5},
    },
    "additionalProperties": True,
}
wjson("schema/provenance.schema.json", schema)

w("examples/example.xmp", xmp_packet(XHS))
wjson("examples/example.json", clean(XHS))

with open(__file__, encoding="utf-8") as f:
    src = f.read()
w("tools/build_vectors.py", src.replace('os.path.join(os.path.dirname(__file__), "..")',
                                        'os.path.join(os.path.dirname(__file__), "..")'))
