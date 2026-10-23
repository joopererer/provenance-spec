# 变更记录

## 0.1.4（草案）— 2026-10-23

- MP4/MOV XMP 存储与解析规范（§4.1, §4.3, §4.7, §10）：
  - §4.1：MP4/MOV 使用顶层 `uuid` box（UUID `BE7ACFCB-97A9-42E8-9C71-999491E3AFAC`），16 字节 UUID 之后直接是 XMP 包，没有额外头部。读取方只扫描顶层 box，绝对不进入 `mdat`。不支持 QuickTime 的 `moov/udta/XMP_`。
  - §4.7 读取规则：支持 32 位与 64 位（`size == 1` 时的 `largesize`）长度解析；有多个 XMP 块时取最后一个可解析的；文件被截断或 XML 不完整时视为没有 XMP，不得报错。
  - §4.7 写入规则：
    - 新块追加到文件末尾，旧的 XMP 块只把 box 类型改为 `free`，其他字节原样不动；
    - 最后一个顶层块长度为 0 时（延伸至 EOF），需先把长度写明，原地无法完成时允许拒绝写入；
    - 必须支持 64 位长度；
    - 允许原地追加写入：追加失败时必须截回原长度，确保文件不损坏。
  - §4.3 C2PA 检测：MP4 的 C2PA 存放在顶层 `uuid` box（UUID `D8FEC3D6-1B0E-483C-9297-5828877EC481`），检测到时禁止嵌入，改用边车文件。
  - §10 一致性要求：对 MP4/MOV，写入后媒体数据逐字节不变，恰好一个 XMP 块位于文件末尾，不重新编码。
- 测试用例：新增第一批 MP4/MOV 测试用例（由 `tools/build_vectors.py` 用 ffmpeg + Python 确定性生成，配套 `*.expected.json`）：
  - `mp4-no-xmp.mp4`：无 XMP 的标准 MP4
  - `mp4-xmp-uuid.mp4`：含顶层 XMP uuid box（含 `photoshop:Headline` 外来命名空间字段，写入后必须保留）
  - `mov-no-xmp.mov`：含 wide atom 的 QuickTime MOV，无 XMP
  - `mov-xmp-uuid.mov`：moov atom 在末尾且末尾追加 XMP uuid box 的 MOV 视频
  - `mp4-64bit-box.mp4`：含 64 位长度（largesize，size=1）box 的 MP4
  - `mp4-size-zero-mdat.mp4`：末尾 mdat box 长度为 0（延伸至 EOF）的 MP4，写入前需先写明实际长度
  - `mp4-truncated-mdat.mp4`：mdat 数据被截断的 MP4，读取方不得报错并视为无 XMP
  - `mp4-truncated-xmp.mp4`：XMP 块数据被截断且 XML 不完整的 MP4，读取方不得报错并视为无 XMP
  - `mp4-multiple-xmp.mp4`：含有多个顶层 XMP 块的 MP4，读取方取最后一个可解析的 XMP 块
  - `mp4-mdat-uuid-noise.mp4`：mdat 媒体数据内部包含 XMP UUID 字节序列但顶层无 XMP 的 MP4，验证读取方只扫描顶层不进入 mdat
- 待补（暂不做）：
  - 真实签名的 C2PA 视频测试文件（待相关签名工具链完善后补充）
  - 分片 MP4（Fragmented MP4 / fMP4）测试文件

## 0.1.3（草案）— 2026-10-22

- 4.7 XMP 解析要求补充：识别 JPEG 的 XMP 段必须严格比较 APP1 段开头的标识字节（`"http://ns.adobe.com/xap/1.0/\0"`），遇到 EXIF（`"Exif\0\0"`）等其他 APP1 段必须直接跳过，不得作为文本解码；写入方必须逐字节原样保留 EXIF 等已有非 XMP 段。（来源：EasySave 实现时因 EXIF 段导致 Live 图封面写入失败）
- 新增测试用例 `exif-before-xmp.jpg`：EXIF APP1 段在 XMP APP1 段之前的 JPEG（含真实的 EXIF 二进制数据）；期望读取结果正常，写入后 EXIF 段逐字节保留。
- §6 去重与 assetId 归并补充：同一来源键对应多个不同 assetId 时（如多设备独立采集所致），索引方以 `capturedAt` 最早者为主记录，在自己的数据库中记录对应关系，不得修改文件中的 assetId。
- §3.5 平台登记补充说明：`sourceId` 一律视为不透明字符串，读取方不得解析其内部结构（OneDrive 的 `{driveId}!{id}` 中，`id` 本身也可能含 `!`）。
- IMPLEMENTATIONS.md：增加“当前使用版本”列；EasySave 状态改为已实现 0.1.1（JPEG/PNG/WebP 嵌入读写、边车读取，视频与边车写入未实现）。

## 0.1.2（草案）— 2026-10-22

- 平台登记：
  - 新增 `baidupan`（百度网盘）：`sourceId = fs_id`（64 位无符号整数转字符串；经查证，网盘内移动和重命名操作不会改变 `fs_id`）；私有文件无稳定公开页面链接，省略 `sourceUrl`；单文件来源省略 `itemIndex`。
  - 新增 `onedrive`（Microsoft OneDrive）：`sourceId = {driveId}!{id}`（拼接 Drive ID 与 item ID，统一个人版与商业版/SharePoint，确保跨驱动器和租户全局唯一）；省略 `sourceUrl`；单文件来源省略 `itemIndex`。
  - 115 云盘由于插件尚未实现接入，本次暂不登记。
- assetId 复用规则：已知同一来源键（`platform + sourceId + itemIndex`）的 assetId 时复用，未知或无 `sourceId` 时生成新的 UUID v4；读取方不能假设一个资源只有一个 assetId。
- 去重规则调整（第 6 节）：
  - 删除第 6 节第 2 条中"无 sourceId 时用 sourceUrl 作后备去重键"的规则：没有 `sourceId` 时，任何平台都不按来源键复用 assetId，也不按来源键去重，只按 assetId 和内容哈希判断。
  - 调整理由：`platform=web` 时 `sourceUrl` 是页面链接，同一个页面上的多张不同图片键完全相同，会被误判为同一个文件，甚至复用同一个 assetId；`itemIndex` 依赖网页的 DOM 顺序，不稳定，不能用来区分；图片直链（CDN）经常带尺寸、签名或时间参数，也无法作为稳定的 sourceId。宁可漏判重复（多出一个副本），也不能误合并两个不同的文件。并在第 6 节增加普通网页多图示例。
- 来源链接可选与字段预留：
  - 没有稳定公开链接的平台允许省略 `sourceUrl`（同步修改 `schema/provenance.schema.json` 中 `source` 的必填项，仅保留 `platform`）。
  - §3.7 预留 `prov:mediaUrl`：用途说明为"媒体直链，只作为排查线索，不参与去重"，0.1.2 不实现。
- 测试用例：
  - 新增测试用例 `baidupan-single.jpg`：验证省略 `sourceUrl` 的有 ID 网盘来源解析。

## 0.1.1（草案）— 2026-10-21

- 新增 4.7 XMP 解析要求：读取方必须支持属性写法、子元素写法、多个 rdf:Description 块，按命名空间 URI 识别字段并还原 XML 实体；写入方必须原地修改 XML、按 UTF-8 字节数计算长度、WebP 奇数长度补齐。（来自 EasySave 首次实现时发现的问题）
- 新增测试用例 `multiblock-elements.jpg`：子元素写法 + 多个 rdf:Description 块 + 非常用前缀。

## 0.1（草案）— 2026-10-20

- 修订：派生关系改用标准 `xmpMM:DerivedFrom`，删除预留的 `prov:derivedFrom`；新增可选 `photoshop:Credit` 署名行；含 C2PA 内容凭证的文件必须使用边车；新增导入时从系统下载记录读取来源线索（4.5）。

- 首个版本：必填字段（schema、assetId、capturedAt、capturedBy、MetadataDate）、来源字段、标准字段映射、存储位置、边车文件、合并规则、链接规范化、去重顺序、JSON 表示、测试用例。
