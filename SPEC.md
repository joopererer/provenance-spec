# Provenance Metadata Spec（溯源元数据规范）

- 版本：**0.1.3（草案）**
- 状态：可实现；0.x 期间允许调整，1.0 起冻结已有字段语义
- 适用项目：EasySave、File Organizer、OnlineAlbumPlugin、Tessera-system，以及任何希望读写本规范的软件

---

## 1. 目标与原则

让下载、收藏、导入的媒体文件**自带来源和整理信息**，脱离任何 App 的数据库也能读出、迁移、重建。

1. **文件即真相**：元数据首先存在文件里（或同名边车文件里）。各 App 的数据库只是索引缓存，可随时从文件重建。
2. **优先用标准字段**：标题、作者、标签、评分等用 XMP 标准字段，Windows 资源管理器、Lightroom、digiKam 等软件可以直接读写。只有标准没有的才放进自定义命名空间 `prov`。
3. **只增补，不破坏**：写入时保留文件中已有的所有其他元数据；不重新编码画面/音视频数据。
4. **隐私优先**：不写入任何 token、cookie、用户自己的账号标识；链接一律规范化。
5. **读者宽容**：读到不认识的字段直接忽略并原样保留；读到缺字段的记录照常使用。

---

## 2. 命名空间

| 前缀 | 命名空间 URI | 说明 |
|---|---|---|
| `prov` | `https://joopererer.github.io/provenance-spec/ns/` | 本规范自定义字段 |
| `dc` | `http://purl.org/dc/elements/1.1/` | Dublin Core（标准） |
| `xmp` | `http://ns.adobe.com/xap/1.0/` | XMP 基础（标准） |

- 命名空间 URI **永久不变**，版本号写在 `prov:schema` 字段里，不写进 URI。
- 前缀 `prov` 只是约定；解析时必须以 URI 为准，不能以前缀为准。
- 注意：本规范与 W3C PROV 本体无关，只是前缀相同。

---

## 3. 字段

### 3.1 字段分类

- **抓取字段**：在第一次写入（下载/抓取/导入）时确定，之后**不可修改**。
- **用户字段**：用户可随时修改（标签、评分、标题等）。
- **系统字段**：每次写入时由软件更新。

### 3.2 必填字段

| 字段 | 类型 | 类别 | 说明 |
|---|---|---|---|
| `prov:schema` | 文本 | 系统 | 规范版本，当前为 `"0.1"` |
| `prov:assetId` | 文本（UUID v4，小写） | 抓取 | 文件的永久身份。首次写入时生成，之后**任何软件都不得修改**，复制文件时一并保留。已知同一来源（`platform + sourceId + itemIndex`）的 `assetId` 时复用，未知或无 `sourceId` 时生成新的；读取方不能假设一个资源只有一个 `assetId` |
| `prov:capturedAt` | 日期 | 抓取 | 首次被收录的时间（下载完成/导入时间） |
| `prov:capturedBy` | 文本 | 抓取 | 首次写入的软件及版本，如 `EasySave/1.7.0`。用于排查某个版本写错数据 |
| `xmp:MetadataDate` | 日期 | 系统 | 本条元数据最后一次修改的时间（XMP 标准字段） |

### 3.3 来源字段

| 字段 | 类型 | 类别 | 必填 | 说明 |
|---|---|---|---|---|
| `prov:platform` | 文本 | 抓取 | 是 | 平台标识，见 3.5 |
| `prov:sourceId` | 文本 | 抓取 | 条件必填 | 平台内的原生 ID（笔记 ID、shortcode、推文 ID、Drive 文件 ID、网盘 fs_id）。无原生 ID 的普通网页（`web`）可省略 |
| `prov:sourceUrl` | 文本 | 抓取 | 条件必填 | **规范化后**的来源页面链接（见第 5 节）。不是 CDN 直链。无稳定公开页面链接的平台（如私有云盘）可省略 |
| `prov:itemIndex` | 整数 | 抓取 | 多项来源时必填 | 在来源中的序号，**从 1 开始**。单项来源省略 |
| `prov:itemCount` | 整数 | 抓取 | 否 | 来源中的总项数 |
| `prov:authorId` | 文本 | 抓取 | 否 | 作者在平台上的稳定 ID（用户名会改，ID 不会） |
| `prov:publishedAt` | 日期 | 抓取 | 否 | 来源内容的发布时间 |
| `prov:pairId` | 文本 | 抓取 | 否 | 配对标识：Live Photo 的图片和视频写同一个值，格式 `<sourceId>#<itemIndex>` |

### 3.4 标准字段（推荐）

| 字段 | 类别 | 说明 | Windows 中显示为 |
|---|---|---|---|
| `dc:title` | 用户 | 标题（抓取时取来源标题） | 标题 |
| `dc:creator` | 用户 | 作者显示名（有序列表） | 作者 |
| `dc:description` | 用户 | 正文/文案，**最多 2000 字符**，超出截断并以 `…` 结尾 | 备注（部分版本） |
| `dc:subject` | 用户 | 标签（无序列表） | 标记 |
| `xmp:Rating` | 用户 | 评分 0–5 | 分级 |
| `dc:source` | 抓取 | 与 `prov:sourceUrl` 相同，供不认识 `prov` 的软件读取（省略 `sourceUrl` 时亦省略） | — |
| `photoshop:Credit` | 抓取 | 可选。署名行，格式 `作者显示名 / 平台名`，如 `示例作者 / 小红书`。IPTC 的 Credit Line 字段，Google 图片等会显示 | — |

### 3.5 平台标识 `prov:platform`

小写字符串，已登记平台：

| 平台标识 | 平台名称 | `sourceId` 定义 | `sourceUrl` 规则 | 说明 |
|---|---|---|---|---|
| `xiaohongshu` | 小红书 | 笔记 ID（如 `6ad2f7050000000012034042`） | 必填（规范化 explore 链接） | 多图使用 `itemIndex` |
| `instagram` | Instagram | shortcode（如 `Ddl1WWnGyCN`） | 必填（规范化 `/p/` 链接） | 多图使用 `itemIndex` |
| `x` | X (Twitter) | tweetId（纯数字推文 ID） | 必填（规范化 `/i/status/` 链接） | 多图使用 `itemIndex` |
| `tiktok` | TikTok | 视频 ID | 必填（规范化链接） | 待 TikTok 支持时补充规范链接格式 |
| `youtube` | YouTube | 视频 ID | 必填（规范化链接） | 待支持 |
| `gdrive` | Google Drive | `fileId`（Drive API 资源 ID） | `https://drive.google.com/file/d/{fileId}/view` | 单文件来源省略 `itemIndex` |
| `baidupan` | 百度网盘 | `fs_id`（64位无符号整数转字符串） | 省略（私有文件无稳定公开链接） | 网盘移动、重命名后 `fs_id` 保持不变；单文件来源省略 `itemIndex` |
| `onedrive` | Microsoft OneDrive | `{driveId}!{id}`（拼接 `driveId` 与 item `id`） | 省略（私有文件无稳定公开链接） | 个人版与商业版（SharePoint）统一采用 `{driveId}!{id}` 格式，确保跨驱动器和租户全局唯一；单文件来源省略 `itemIndex` |
| `web` | 普通网页 | 省略（网页无原生 ID） | 必填（规范化页面 URL，见第 5 节） | 仅用于追踪来源页面；不按来源键去重或复用 assetId；网页多图各自分配独立 assetId |
| `local` | 本地导入 | 省略 | 省略 | 本地导入、无网络来源 |

新增平台直接使用新的小写名称，并在本表中登记。插件尚未实现稳定接入的平台（例如 115 云盘）暂不登记。

**平台 ID 的不透明性**：`prov:sourceId` 一律视为不透明字符串（opaque string），读取方不得解析其内部结构。例如 OneDrive 采用 `{driveId}!{id}` 格式，但 Graph item `id` 本身内部也可能包含 `!` 符号，读取方切勿尝试通过切分字符串来推断 `driveId` 或 `id`。

### 3.6 关于 `itemIndex` / `itemCount`

保留 `itemIndex` 的理由：
1. **区分同一来源的不同文件**：一条 9 图笔记的 9 个文件，`sourceUrl` 完全相同，只有 `itemIndex` 能区分它们。没有它，"是否已下载过这张"就无法判断。
2. **重建顺序**：相册里文件的时间戳往往相同或乱序，重建历史时需要它恢复原帖的图片顺序。

`itemCount` 为可选：只在想发现"这条笔记共 9 张只存了 6 张"时有用，能拿到就写。

### 3.7 预留（0.1 不实现，名称已占用）

- 派生关系（裁剪、转码后的新文件）：**不新增自定义字段**，使用 XMP 标准的 `xmpMM:DerivedFrom`（`stRef:documentID` 填原文件的 `assetId`）。派生文件生成**新的** `assetId`。
- 说明：`prov:assetId` 不复用 `xmpMM:DocumentID`，因为相机和编辑软件会自行写入、改写 DocumentID（如"另存为"会生成新值），语义与本规范"永久不变"不一致。
- `prov:topics`：Tessera 主题（0.1 中主题直接用 `dc:subject` 标签表示）。
- `prov:mediaUrl`：媒体直链。只占用名称，用途说明为"媒体直链，只作为排查线索，不参与去重"，0.1.2 不实现。

---

## 4. 存储位置

### 4.1 按格式

| 格式 | 存储方式 |
|---|---|
| JPEG | APP1 段中的 XMP 包（`http://ns.adobe.com/xap/1.0/\0` 头）。单段上限 64KB，因此 XMP 包必须 **< 60KB**（`dc:description` 截断规则保证这一点）。可选：同时把 `dc:title` 写进 EXIF `ImageDescription`，方便只读 EXIF 的软件 |
| PNG | `iTXt` 块，关键字 `XML:com.adobe.xmp`，不压缩 |
| WebP | RIFF `XMP ` 块（需要 `VP8X` 扩展头并置 XMP 标志位） |
| MP4 / MOV | XMP `uuid` box（UUID `BE7ACFCB-97A9-42E8-9C71-999491E3AFAC`）；实现不了时使用边车文件 |
| GIF、HEIC、AVIF、RAW、其他 | 边车文件 |

### 4.2 边车文件

- 文件名：**完整原文件名 + `.xmp`**，例如 `IMG_001.jpg.xmp`、`IMG_001.mp4.xmp`。
  - 不用 `IMG_001.xmp`，因为 Live Photo 的图片和视频常常同名不同扩展名，会冲突。
- 内容：一个完整的 XMP 包（与嵌入的格式完全相同），UTF-8，无 BOM。
- 与原文件放在同一目录。移动/重命名原文件时，必须同步移动/重命名边车文件。
- 兼容性：darktable 使用同样的 `<完整文件名>.xmp` 命名；digiKam、Immich 等软件也读取 XMP 边车，具体命名支持以各软件文档为准。

### 4.3 何时嵌入、何时用边车

| 场景 | 默认 |
|---|---|
| 本规范的软件自己下载/抓取的文件 | 嵌入 |
| 用户自己的原有文件（导入、整理） | 边车（不改动用户原文件），可在设置中改为嵌入 |
| 格式不支持嵌入 | 边车 |
| 云盘上的文件（不下载） | 不修改文件，使用云盘自带的文件属性（如 Drive `appProperties`）存同样的字段 |
| 文件含 C2PA 内容凭证（JPEG 的 APP11 JUMBF 段、PNG 的 `caBX` 块等） | **必须用边车**。向已签名文件嵌入 XMP 会使签名校验失败，破坏其内容凭证 |

### 4.4 读取与合并

1. 读嵌入元数据；2. 读边车文件；3. 两者都有时按字段合并：
   - 抓取字段：以嵌入为准；
   - 用户字段：以 `xmp:MetadataDate` 较新的一方为准；
4. App 数据库与文件冲突时，**以文件为准**。文件被外部软件修改过（如在 Windows 资源管理器里改了标签），App 重新扫描时读入。

### 4.5 导入时的来源线索（可选）

没有本规范元数据的文件，导入时可以从操作系统记录的下载来源中读取线索，填入 `prov:sourceUrl`（`platform` 按链接判断，否则为 `web`）：

| 系统 | 位置 | 优先使用 |
|---|---|---|
| Windows | NTFS 备用数据流 `Zone.Identifier` 中的 `ReferrerUrl`、`HostUrl` | `ReferrerUrl`（来源页面）；没有时用 `HostUrl`（文件直链） |
| macOS | 扩展属性 `com.apple.metadata:kMDItemWhereFroms` | 列表中的来源页面 |
| Linux | 扩展属性 `user.xdg.origin.url`、`user.xdg.referrer.url` | `user.xdg.referrer.url` |

读到的链接同样必须按第 5 节规范化。这些线索只用于补全，`capturedBy` 写导入软件本身。

### 4.6 写入规则

- 读出原有 XMP 包 → 只修改本规范涉及的字段 → 写回。其他命名空间、其他字段**原样保留**。
- 已有 `prov:assetId` 时**绝不覆盖**；已有抓取字段时不覆盖。
- 已有 `dc:subject`、`xmp:Rating`、`dc:title` 等用户字段，除非是用户本次主动修改，否则不覆盖。
- 每次写入更新 `xmp:MetadataDate`。
- 只改元数据，**不重新编码**画面或音视频。
- 写入失败不得影响文件本身的保存；记录日志即可。

### 4.7 XMP 解析要求（读取方必须做到）

XMP 是 RDF/XML，同一份数据有多种合法写法，不同软件写出的形式不同。读取方必须同时支持：

1. **属性写法**：`<rdf:Description prov:schema="0.1"/>`（exiftool、Adobe 软件常用）。
2. **子元素写法**：`<rdf:Description><prov:schema>0.1</prov:schema></rdf:Description>`。
3. **多个 `rdf:Description` 块**：同一个 XMP 包里可以有多个块（exiftool 常按命名空间分块），所有块的字段合并读取。
4. **按命名空间 URI 识别字段**，不按前缀；同一 URI 可能使用别的前缀。
5. XML 实体（`&amp;`、`&lt;`、`&quot;` 等）必须还原。
6. **JPEG APP1 段识别**：识别 JPEG 中的 XMP 段时，**必须**比较 APP1 段开头的标识字节 `http://ns.adobe.com/xap/1.0/\0`（前 29 字节）。遇到以 `Exif\0\0`（EXIF 数据）或其他标识开头的非 XMP APP1 段，必须直接跳过，**绝不得**作为文本解码（更不得假定首个 APP1 就是 XMP）。（来源：EasySave 实现时因 EXIF 段导致 Live 图封面写入失败）

写入方要求：

1. 在 XML 结构上**原地修改**规范涉及的字段；其他节点、属性、命名空间声明原样保留，不得从数据模型重新生成整个 XMP 包。
2. 所有长度（JPEG 段长度、PNG 块长度、WebP 块长度）按 **UTF-8 字节数**计算，不是字符数。注意 xpacket 头中的 `\ufeff` 在 UTF-8 中占 3 字节。
3. WebP 块长度为奇数时，块数据后补 1 个 `0x00` 填充字节（填充不计入块长度）。
4. 遇到已有的 EXIF 段（`Exif\0\0`）或其他非 XMP 的 APP 段时，必须逐字节原样保留，不得破坏或覆盖；写入 XMP 时应将 XMP APP1 段插入或原地替换已有的 XMP APP1 段。

---

## 5. 链接规范化

写入 `prov:sourceUrl` 前必须规范化：

1. 去掉跟踪和分享参数：`utm_*`、`fbclid`、`gclid`、`igsh`、`igshid`、`si`、`spm`、`share_*`、`shareRedId`、`xsec_token`、`xsec_source`、`apptime`、`author_share`、`xhsshare`、`track_code`、`app_platform`、`app_version`、`ignoreEngage`、`dlrf`、`xtok`、`img_index` 等。
2. 去掉 URL 片段（`#…`）。
3. 短链先展开为最终链接再规范化。
4. 已知平台改写为固定格式：

| 平台 | 规范格式 |
|---|---|
| xiaohongshu | `https://www.xiaohongshu.com/explore/{noteId}` |
| instagram | `https://www.instagram.com/p/{shortcode}/`（Reels 同样使用 `/p/`） |
| x | `https://x.com/i/status/{tweetId}`（不含用户名，用户名会改） |
| tiktok | 待 TikTok 支持时补充 |
| gdrive | `https://drive.google.com/file/d/{fileId}/view` |
| baidupan | 省略（私有文件无稳定公开链接） |
| onedrive | 省略（私有文件无稳定公开链接） |
| web | 方案 + 小写主机名 + 路径 + 去除跟踪参数后的查询串 |

说明：规范化后的小红书链接在未登录或缺少 token 时可能无法直接打开，这是可以接受的：`sourceId` 和链接仍唯一标识内容，用户可以重新搜索或在 App 内打开。

---

## 6. 去重与 assetId 复用

### 6.1 assetId 复用规则
- 写入方在已知同一来源（`prov:platform` + `prov:sourceId` + `prov:itemIndex`）已分配 `assetId` 时（例如本地数据库已有记录），必须复用已有 `assetId`；未知或无 `sourceId` 时生成新的 UUID v4。
- **读取方不能假设一个资源只有一个 assetId**：不同设备独立采集、不同应用写入、或者历史导入未关联来源记录时，完全可能为同一张图片生成不同的 `assetId`。
- **多 assetId 的主从归并**：同一来源键对应多个不同 `assetId` 时，索引方（如相册或整理工具）以 `prov:capturedAt` 最早者为主记录，在自己的数据库中记录对应或映射关系，**不得修改文件中的 assetId**。

### 6.2 去重判定顺序
按顺序判断，命中即视为同一文件：

1. `prov:assetId` 相同；
2. `prov:platform` + `prov:sourceId` + `prov:itemIndex` 相同（**仅限有 `sourceId` 的平台**；无 `sourceId` 时不得按来源键去重，也不得按来源键复用 `assetId`）；
3. 文件内容 SHA-256 相同（**仅用于没有元数据的文件**：写入元数据会改变文件哈希，所以不能拿已写入元数据的文件和未写入的文件比哈希）；
4. 可选：感知哈希（如 dHash/pHash）相近，提示"可能重复"由用户确认，不自动合并。

> **为什么删除"无 sourceId 时用 sourceUrl 作后备去重键"的规则？**  
> `platform=web` 时 `sourceUrl` 是页面链接。若使用页面链接去重或复用 `assetId`，同一个页面上的多张不同图片因为键完全相同，会被误判为同一个文件，甚至被错误复用同一个 `assetId`；  
> 网页环境下的 `itemIndex` 依赖 DOM 渲染顺序，容易随网页脚本、动态加载或布局调整而变化，极不稳定，无法作为唯一区分依据；  
> 图片直链（CDN）经常携带尺寸、签名或时间参数，也无法作为稳定的 `sourceId`。  
> 因此，没有原生 `sourceId` 的平台（如普通网页 `web`）不进行来源键去重，只依据 `assetId` 和内容哈希判断。**宁可漏判重复（多出一个副本），也绝不能误合并两个不同的文件。**

### 6.3 示例：普通网页多图各自拥有独立 assetId
用户从同一个文章网页 `https://example.com/blog/travel` 收藏了主图与插图两张不同图片：
- 图片 A：`platform = "web"`, `sourceUrl = "https://example.com/blog/travel"`, 省略 `sourceId`，生成独立 `assetId = "a1111111-..."`
- 图片 B：`platform = "web"`, `sourceUrl = "https://example.com/blog/travel"`, 省略 `sourceId`，生成独立 `assetId = "b2222222-..."`

两张图片虽然 `sourceUrl` 相同，但没有 `sourceId`，因此各自拥有独立的 `assetId`，且不按来源键去重，绝不会被误合并为同一个文件。复制得到的同一文件副本则保留相同的 `assetId`。

---

## 7. JSON 表示

用于 API、命令行输出和测试数据。字段名去掉前缀，标准字段使用以下名称：

```json
{
  "schema": "0.1",
  "assetId": "3f0c6a2e-8d4b-4c1a-9a3e-2b7f5d9e1c40",
  "capturedAt": "2026-10-20T15:30:00+02:00",
  "capturedBy": "EasySave/1.7.0",
  "metadataDate": "2026-10-20T15:30:00+02:00",
  "source": {
    "url": "https://www.xiaohongshu.com/explore/6ad2f7050000000012034042",
    "platform": "xiaohongshu",
    "id": "6ad2f7050000000012034042",
    "itemIndex": 3,
    "itemCount": 9,
    "authorId": "5f1a2b3c000000000100abcd",
    "publishedAt": "2026-10-18T09:12:00+08:00",
    "pairId": null
  },
  "title": "wow～ 好干净的奶白色",
  "creator": ["某作者"],
  "description": "正文……",
  "subject": ["家居", "奶白色"],
  "rating": 4
}
```

- 缺失字段可以省略或为 `null`，含义相同。
- 机器可校验的定义见 `schema/provenance.schema.json`。

---

## 8. 日期格式

ISO 8601，**必须带时区**：`2026-10-20T15:30:00+02:00` 或 `2026-10-20T13:30:00Z`。只知道日期时写 `2026-10-20`。

---

## 9. 版本演进

- `0.x`：允许调整，但每次变更写进 `CHANGELOG.md`。
- `1.0` 之后：
  - 只能**新增**可选字段，不能删除字段、不能改变已有字段的含义或类型；
  - 小版本号递增（`1.1`、`1.2`）；读者遇到更高小版本时照常读取已知字段；
  - 确需破坏性变更时使用新字段名，旧字段保留只读。

---

## 10. 一致性要求（实现必须做到）

一个实现被认为"符合 0.1"，需要：

1. 通过 `test-vectors/` 中全部读取用例（读出的 JSON 与 `*.expected.json` 一致）；
2. 写入后再读出，字段完全一致（往返测试）；
3. 对含有其他命名空间字段的输入文件，写入后其他字段原样保留；
4. 已有 `assetId` 的文件写入后 `assetId` 不变；
5. 写入不改变图像像素（解码后逐像素比较一致）；
6. 链接规范化通过 `test-vectors/urls.json` 全部用例。
