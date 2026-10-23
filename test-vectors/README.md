# 测试用例

- `xhs-item3.jpg`：JPEG，多图笔记第 3 张，含特殊字符；另含 photoshop:Headline 外来字段，写入后必须保留
- `ig-item2.png`：PNG iTXt，用户字段较新（metadataDate 晚于 capturedAt）
- `x-single.webp`：WebP XMP 块，单项来源（无 itemIndex）
- `local-video.mp4 + local-video.mp4.xmp`：边车文件；本地导入，无来源；占位 MP4 仅用于验证边车命名
- `no-metadata.jpg`：无元数据：读取结果为空；去重时使用文件 SHA-256（见 expected 中的 sha256）
- `multiblock-elements.jpg`：子元素写法 + 三个 rdf:Description 块（exiftool 风格）+ 命名空间前缀为 pv 而不是 prov；另含 xmp:CreatorTool 外来字段，写入后必须保留（SPEC 4.7）
- `baidupan-single.jpg`：JPEG，百度网盘来源，省略 sourceUrl（私有文件无稳定公开链接），仅含 platform 与 sourceId（fs_id）
- `exif-before-xmp.jpg`：JPEG，EXIF APP1 段在 XMP APP1 段之前（含真实 EXIF 二进制数据）；读取方必须跳过 EXIF 段识别 XMP，写入后 EXIF 段必须逐字节保留（SPEC 4.7）
- `mp4-no-xmp.mp4`：MP4 视频，无 XMP 元数据；读取结果为空，去重时使用文件 SHA-256
- `mp4-xmp-uuid.mp4`：MP4 视频，顶层 XMP uuid box，含 photoshop:Headline 外来字段（写入后必须保留，SPEC 4.1/4.7）
- `mov-no-xmp.mov`：QuickTime MOV 视频，含 wide atom，无 XMP 元数据
- `mov-xmp-uuid.mov`：QuickTime MOV 视频，moov atom 在末尾，末尾追加顶层 XMP uuid box（SPEC 4.1/4.7）
- `mp4-64bit-box.mp4`：MP4 视频，含 64 位长度 box（largesize，size=1），包含 64 位 free box 与 64 位 XMP uuid box（SPEC 4.7）
- `mp4-size-zero-mdat.mp4`：MP4 视频，最后一个顶层 box 为 size=0 的 mdat（延伸至文件末尾）；写入方写入前必须先写明其实际长度（SPEC 4.7）
- `mp4-truncated-mdat.mp4`：MP4 视频，mdat 数据块被截断；读取方视为无 XMP，不得报错（SPEC 4.7）
- `mp4-truncated-xmp.mp4`：MP4 视频，XMP 块数据被截断且 XML 不完整；读取方视为无 XMP，不得报错（SPEC 4.7）
- `mp4-multiple-xmp.mp4`：MP4 视频，包含多个顶层 XMP uuid box；读取方取最后一个可解析的 XMP 块（SPEC 4.7）
- `mp4-mdat-uuid-noise.mp4`：MP4 视频，mdat 数据内部包含 XMP UUID 字节序列但顶层无 XMP；读取方只扫描顶层不进入 mdat，不得误读（SPEC 4.1/4.7）
- `urls.json`：链接规范化用例

每个 `*.expected.json` 是按 SPEC 第 7 节 JSON 表示读出的期望结果（省略缺失字段）。

一致性要求见 SPEC 第 10 节。测试文件由 `tools/build_vectors.py` 用 ffmpeg + Python 确定性生成；**不要手工修改这些文件**，需要修改时改脚本重新生成并在 CHANGELOG 中说明。
