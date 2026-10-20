# 变更记录

## 0.1（草案）— 2026-10-20

- 修订：派生关系改用标准 `xmpMM:DerivedFrom`，删除预留的 `prov:derivedFrom`；新增可选 `photoshop:Credit` 署名行；含 C2PA 内容凭证的文件必须使用边车；新增导入时从系统下载记录读取来源线索（4.5）。

- 首个版本：必填字段（schema、assetId、capturedAt、capturedBy、MetadataDate）、来源字段、标准字段映射、存储位置、边车文件、合并规则、链接规范化、去重顺序、JSON 表示、测试用例。
