# provenance-spec

媒体文件溯源元数据规范：让下载、收藏、导入的图片和视频**自带来源与整理信息**，任何符合规范的软件都能读写，脱离 App 数据库也能重建。

- 规范正文：[`SPEC.md`](SPEC.md)（当前 0.1 草案）
- JSON Schema：[`schema/provenance.schema.json`](schema/provenance.schema.json)
- 示例：[`examples/`](examples/)
- 测试用例：[`test-vectors/`](test-vectors/)（所有实现必须通过）
- 已知实现：[`IMPLEMENTATIONS.md`](IMPLEMENTATIONS.md)
- 变更记录：[`CHANGELOG.md`](CHANGELOG.md)

## 一句话概括

标准 XMP 字段（标题、作者、标签、评分）+ 自定义命名空间 `prov`（永久 ID、来源链接、平台、平台内 ID、序号、抓取时间）。能嵌入就嵌入文件，不能嵌入就写同名边车文件 `<文件名>.xmp`。

## 各项目如何使用本仓库

1. **只读引用，不在项目里修改规范**。规范的修改只在本仓库进行。
2. 各项目把 `test-vectors/` 复制到自己的测试目录（或用 git submodule），并在项目文档中写明遵循的规范版本，例如"遵循 provenance-spec 0.1"。
3. 规范升级时，各项目更新测试用例并在自己的 CHANGELOG 中记录。
4. 新实现完成后，在 `IMPLEMENTATIONS.md` 登记。

## 重新生成测试用例

```bash
pip install pillow
python tools/build_vectors.py
```
