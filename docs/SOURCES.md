# 来源与许可边界

## 原创代码与说明

`scripts/`、`tests/`、本项目编写的 HTML/CSS 模板、构词与词族说明、贡献文档及项目自编练习句适用根目录 MIT 许可证。事实、常见词形和语法规则不是对参考词典的长篇复制。

参考 anki-jlpt-decks 的公开仓库组织与迭代方式，没有复制其代码或牌组。该项目自己的内容许可证不适用于本项目。

## 原词表

- 来源：https://iscorevoc.pages.dev/
- 原词条、释义、原音标、频次及分组保留来源，不因本仓库的 MIT 许可证而重新授权。
- 维护者已确认获得原作者授权，并提供原帖链接：https://linux.do/t/topic/2863425 及与原作者的沟通截图。
- 截图中，维护者 tentyou 请求分享资源以制作 Anki 牌组；维护者确认是原作者的论坛用户 F-droid 回复：「这个东西你直接让 Agent 去看就行了，就几个文件」。这是本项目记录的资源使用与牌组制作授权依据；公开发布授权同时依据维护者的明确确认。
- 原帖链接用于标识资源出处；上述沟通内容来自维护者提供的截图，不声称该对话可在公开原帖直接查看。截图未上传到公开仓库。
- 沟通未指定将原数据改授为 MIT，也未给出完整的后续转授权条件。因此本仓库不把代码许可证自动扩展到原词表；需要另行再分发、改授许可证等用途时，应核实原作者授权范围。
- 当前数据含项目后续修订，不能认为所有释义均来自原作者或均已获词典编辑校订。

## 例句

- Tatoeba：https://tatoeba.org/ 。相应卡片字段保留英语、中文句子编号及句子作者页面链接，许可 [CC BY 2.0 FR](https://creativecommons.org/licenses/by/2.0/fr/)。数据获得自公开的中英句对导出镜像；保留 Tatoeba 作为作品来源。
- Global Voices：https://globalvoices.org/ ，[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)，通过 https://opus.nlpl.eu/ 的 GlobalVoices 2018Q4 平行语料取得。字段保留语料来源、行号与许可；没有把对齐行号假称为精确原文链接。作者与译者为 Global Voices 原文贡献者。
- 项目练习句：编写或模板化生成的教学材料，不冒称来自词典或真实考试。
- 部分缺失的中文使用 Google Translate 机器翻译；部分旧语料译文已修订。机器翻译和对齐仍可能不准确。修改可在版本历史中追踪。
- `example-overrides.json` 中的句子为项目有意编写的消歧练习句；不沿用被替换语料的署名。

第三方许可须独立遵守，根目录 MIT 许可证不覆盖第三方原作。

## 构词与词族

参考 Cambridge English Grammar Today 的现代构词框架：

- https://dictionary.cambridge.org/grammar/british-grammar/prefixes
- https://dictionary.cambridge.org/grammar/british-grammar/suffixes
- https://dictionary.cambridge.org/grammar/british-grammar/word-formation_2

说明采用项目自己的表述。词基可能发生拼写变化；构词只辅助记忆，不自动推导全部词义。对不确定的历史来源不作猜测。

## 新增交叉参考

https://isdc.pages.dev/ 提供词义、主例句、词根词缀与派生词。用于匹配、对比和筛选候选；未将其 49,213 条数据、真题文本、音频、助记或词根说明整批再发布。原始快照及比对缓存不进入 Git。该站与原词表多数字段相同，不能当作完全独立证据；发现的重复拼接和不合适派生关系没有直接合并。

## 音频与工具

单词 MP3 为本地 Microsoft Zira Desktop 生成的 TTS 录音。发行包只含生成的录音，不含 Microsoft 的语音引擎或语音安装组件；不是 Azure TTS，也不冒称真人录音。部分缺失 IPA 先前由 eSpeak NG 自动补全。

genanki 为构建依赖，按其自身许可证分发；仓库没有打包 Python 依赖源码或虚拟环境。NLTK 词性模型仅用于本地复核候选，未打包进入牌组和代码仓库；候选标注不代表已证实错误。
