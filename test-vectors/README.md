# 测试用例

- `xhs-item3.jpg`：JPEG，多图笔记第 3 张，含特殊字符；另含 photoshop:Headline 外来字段，写入后必须保留
- `ig-item2.png`：PNG iTXt，用户字段较新（metadataDate 晚于 capturedAt）
- `x-single.webp`：WebP XMP 块，单项来源（无 itemIndex）
- `local-video.mp4 + local-video.mp4.xmp`：边车文件；本地导入，无来源；占位 MP4 仅用于验证边车命名
- `no-metadata.jpg`：无元数据：读取结果为空；去重时使用文件 SHA-256（见 expected 中的 sha256）
- `multiblock-elements.jpg`：子元素写法 + 三个 rdf:Description 块（exiftool 风格）+ 命名空间前缀为 pv 而不是 prov；另含 xmp:CreatorTool 外来字段，写入后必须保留（SPEC 4.7）
- `urls.json`：链接规范化用例

每个 `*.expected.json` 是按 SPEC 第 7 节 JSON 表示读出的期望结果（省略缺失字段）。

一致性要求见 SPEC 第 10 节。图片由 `tools/build_vectors.py` 生成；**不要手工修改这些文件**，需要修改时改脚本重新生成并在 CHANGELOG 中说明。
