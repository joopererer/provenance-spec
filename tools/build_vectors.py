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
        if s.get("url"):
            attrs.append(f'prov:sourceUrl="{escape(s["url"])}"')
        attrs.append(f'prov:platform="{s["platform"]}"')
        if s.get("id"):
            attrs.append(f'prov:sourceId="{escape(s["id"])}"')
        for k, x in [("itemIndex", "itemIndex"), ("itemCount", "itemCount"), ("authorId", "authorId"),
                     ("publishedAt", "publishedAt"), ("pairId", "pairId")]:
            if s.get(k) is not None:
                attrs.append(f'prov:{x}="{escape(str(s[k]))}"')
        if s.get("url"):
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
BAIDU = {
    "schema": "0.1",
    "assetId": "5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b",
    "capturedAt": "2026-10-22T14:00:00+08:00",
    "capturedBy": "OnlineAlbumPlugin/0.2.0",
    "metadataDate": "2026-10-22T14:00:00+08:00",
    "source": {"url": None, "platform": "baidupan", "id": "1092837465019283",
               "itemIndex": None, "itemCount": None, "authorId": None, "publishedAt": None, "pairId": None},
    "title": "网盘备份图片", "creator": None, "description": None, "subject": ["备份"], "rating": None,
}
EXIF_CASE = {
    "schema": "0.1",
    "assetId": "8a9b0c1d-2e3f-4a5b-8c7d-8e9f0a1b2c3d",
    "capturedAt": "2026-10-22T15:00:00+02:00",
    "capturedBy": "EasySave/1.7.0",
    "metadataDate": "2026-10-22T15:00:00+02:00",
    "source": {"url": "https://www.xiaohongshu.com/explore/6ad511fa0000000021034011", "platform": "xiaohongshu",
               "id": "6ad511fa0000000021034011", "itemIndex": 1, "itemCount": 1,
               "authorId": None, "publishedAt": "2026-10-22T14:30:00+08:00",
               "pairId": "6ad511fa0000000021034011#1"},
    "title": "Live 图封面（含 EXIF）", "creator": ["摄影师"],
    "description": "测试 EXIF APP1 段在 XMP APP1 段之前；读取方必须跳过 EXIF 段，写入方必须保留",
    "subject": ["LivePhoto", "风景"], "rating": 5,
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


def save_jpeg(im, p, xmp_bytes=None, exif_bytes=None):
    import io
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=92)
    data = buf.getvalue()
    idx = 2
    if data.startswith(b"\xff\xd8\xff\xe0"):
        idx = 4 + int.from_bytes(data[4:6], "big")
    segments = []
    if exif_bytes:
        app1_exif = b"\xff\xe1" + (len(exif_bytes) + 2).to_bytes(2, "big") + exif_bytes
        segments.append(app1_exif)
    if xmp_bytes:
        payload = b"http://ns.adobe.com/xap/1.0/\x00" + xmp_bytes
        app1_xmp = b"\xff\xe1" + (len(payload) + 2).to_bytes(2, "big") + payload
        segments.append(app1_xmp)
    data = data[:idx] + b"".join(segments) + data[idx:]
    with open(p, "wb") as f:
        f.write(data)


os.makedirs(TV, exist_ok=True)
cases = []

# JPEG with foreign field (preservation test)
p = os.path.join(TV, "xhs-item3.jpg")
save_jpeg(img(1), p, xmp_packet(XHS, foreign=True).encode("utf-8"))
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
if not os.path.exists(p):
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

# Element syntax + multiple rdf:Description blocks + non-standard prefix (exiftool style)
MB = {
    "schema": "0.1",
    "assetId": "7d8e9f0a-1b2c-4d3e-9f4a-5b6c7d8e9f01",
    "capturedAt": "2026-10-21T09:00:00+02:00",
    "capturedBy": "EasySave/1.7.0",
    "metadataDate": "2026-10-21T09:00:00+02:00",
    "source": {"url": "https://www.xiaohongshu.com/explore/6ad466ed000000001e024277", "platform": "xiaohongshu",
               "id": "6ad466ed000000001e024277", "itemIndex": 1, "itemCount": 2,
               "authorId": None, "publishedAt": "2026-10-20T08:00:00Z", "pairId": None},
    "title": "子元素写法 & 多块",
    "creator": ["作者甲", "作者乙"],
    "description": None,
    "subject": ["标签A"],
    "rating": 3,
}


def xmp_packet_blocks(r):
    s = r["source"]
    e = lambda tag, v: f"<{tag}>{escape(str(v))}</{tag}>"
    pv = "".join([
        e("pv:schema", r["schema"]), e("pv:assetId", r["assetId"]), e("pv:capturedAt", r["capturedAt"]),
        e("pv:capturedBy", r["capturedBy"]), e("pv:sourceUrl", s["url"]), e("pv:platform", s["platform"]),
        e("pv:sourceId", s["id"]), e("pv:itemIndex", s["itemIndex"]), e("pv:itemCount", s["itemCount"]),
        e("pv:publishedAt", s["publishedAt"]),
    ])
    dc = (f'<dc:title><rdf:Alt><rdf:li xml:lang="x-default">{escape(r["title"])}</rdf:li></rdf:Alt></dc:title>'
          "<dc:creator><rdf:Seq>" + "".join(f"<rdf:li>{escape(c)}</rdf:li>" for c in r["creator"]) + "</rdf:Seq></dc:creator>"
          "<dc:subject><rdf:Bag>" + "".join(f"<rdf:li>{escape(t)}</rdf:li>" for t in r["subject"]) + "</rdf:Bag></dc:subject>"
          f"<dc:source>{escape(s['url'])}</dc:source>")
    xm = e("xmp:Rating", r["rating"]) + e("xmp:MetadataDate", r["metadataDate"]) + e("xmp:CreatorTool", "SomeOtherTool 1.0")
    return (
        '<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/">\n'
        ' <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
        f'  <rdf:Description rdf:about="" xmlns:pv="{NS}">{pv}</rdf:Description>\n'
        f'  <rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">{dc}</rdf:Description>\n'
        f'  <rdf:Description rdf:about="" xmlns:xmp="http://ns.adobe.com/xap/1.0/">{xm}</rdf:Description>\n'
        ' </rdf:RDF>\n</x:xmpmeta>\n<?xpacket end="w"?>'
    )


p = os.path.join(TV, "multiblock-elements.jpg")
save_jpeg(img(5), p, xmp_packet_blocks(MB).encode("utf-8"))
wjson("test-vectors/multiblock-elements.jpg.expected.json", clean(MB))
cases.append(("multiblock-elements.jpg", "子元素写法 + 三个 rdf:Description 块（exiftool 风格）+ 命名空间前缀为 pv 而不是 prov；另含 xmp:CreatorTool 外来字段，写入后必须保留（SPEC 4.7）"))

# Baidu Netdisk (omit sourceUrl, has sourceId)
p = os.path.join(TV, "baidupan-single.jpg")
save_jpeg(img(6), p, xmp_packet(BAIDU).encode("utf-8"))
wjson("test-vectors/baidupan-single.jpg.expected.json", clean(BAIDU))
cases.append(("baidupan-single.jpg", "JPEG，百度网盘来源，省略 sourceUrl（私有文件无稳定公开链接），仅含 platform 与 sourceId（fs_id）"))

# JPEG with EXIF APP1 segment before XMP APP1 segment
p = os.path.join(TV, "exif-before-xmp.jpg")
im_exif = img(7)
exif_obj = im_exif.getexif()
exif_obj[0x010E] = "Live Photo Cover Image"
exif_obj[0x010F] = "Apple"
exif_obj[0x0110] = "iPhone 15 Pro"
exif_obj[0x0131] = "EasySave/1.7.0"
exif_obj[0x0132] = "2026:10:22 14:30:00"
save_jpeg(im_exif, p, xmp_bytes=xmp_packet(EXIF_CASE).encode("utf-8"), exif_bytes=exif_obj.tobytes())
wjson("test-vectors/exif-before-xmp.jpg.expected.json", clean(EXIF_CASE))
cases.append(("exif-before-xmp.jpg", "JPEG，EXIF APP1 段在 XMP APP1 段之前（含真实 EXIF 二进制数据）；读取方必须跳过 EXIF 段识别 XMP，写入后 EXIF 段必须逐字节保留（SPEC 4.7）"))

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
            "required": ["platform"],
            "properties": {
                "url": {"anyOf": [{"type": "string", "format": "uri"}, {"type": "null"}]},
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
