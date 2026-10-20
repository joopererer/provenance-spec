# 变更记录

## 0.1.1（草案）— 2026-10-21

- 新增 4.7 XMP 解析要求：读取方必须支持属性写法、子元素写法、多个 rdf:Description 块，按命名空间 URI 识别字段并还原 XML 实体；写入方必须原地修改 XML、按 UTF-8 字节数计算长度、WebP 奇数长度补齐。（来自 EasySave 首次实现时发现的问题）
- 新增测试用例 `multiblock-elements.jpg`：子元素写法 + 多个 rdf:Description 块 + 非常用前缀。

## 0.1（草案）— 2026-10-20

- 修订：派生关系改用标准 `xmpMM:DerivedFrom`，删除预留的 `prov:derivedFrom`；新增可选 `photoshop:Credit` 署名行；含 C2PA 内容凭证的文件必须使用边车；新增导入时从系统下载记录读取来源线索（4.5）。

- 首个版本：必填字段（schema、assetId、capturedAt、capturedBy、MetadataDate）、来源字段、标准字段映射、存储位置、边车文件、合并规则、链接规范化、去重顺序、JSON 表示、测试用例。
