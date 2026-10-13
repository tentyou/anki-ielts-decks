# 雅思核心词汇 Anki 牌组

英文 → 中文，按原词表频次分为五个子牌组。支持 Windows Anki、AnkiDroid 和 AnkiMobile。

**[下载最新卡包](https://github.com/tentyou/anki-ielts-decks/releases/latest)** · **[反馈错误](https://github.com/tentyou/anki-ielts-decks/issues/new?template=correction.yml)**

当前版本 **v0.2.0**：12,155 张卡片，17,091 句中英例句，738 个词条有选择性的构词提示或词族；只包含单词离线音频，约 73 MB。

<img src="docs/card-preview.png" alt="含构词与词族的卡片预览" width="430">

## 内容

- 正面显示英文单词和单词播放按钮；反面显示音标、中文释义、双语例句与来源。
- 部分词条显示「构词与记忆」及「词族」，没有合适内容时整个栏目隐藏。
- 构词采用现代前后缀、词基及常见词族，不把拼写相似当作词源。词基在派生时可能发生拼写变化。不同词义不能仅通过构词相加推导。
- 单词发音为 Microsoft Zira Desktop 美式 TTS 生成的 MP3；不是依赖设备语音引擎的动态 TTS。音标沿用原站及先前补全，部分音标与美式发音存在差异。
- 没有例句音频，没有联网音频脚本，不显示自动音标或未人工校订提示。
- 卡片附词典与 GitHub 反馈入口。

参考 [anki-jlpt-decks](https://github.com/5mdld/anki-jlpt-decks) 的项目组织、发行和社区纠错方式；本项目没有复制该项目的代码、日语数据或媒体。

## 下载、安装及更新

1. 从 [Releases](https://github.com/tentyou/anki-ielts-decks/releases) 下载 `.apkg`，不要把 GitHub 的 Source code ZIP 当成卡包。
2. 在桌面 Anki 中导入。更新已有版本时，允许更新笔记与笔记类型，并打开合并笔记类型；需要时选择「始终更新」。
3. 使用同一 AnkiWeb 账户同步到 AnkiDroid / AnkiMobile，等待媒体同步完成后再离线学习。

沿用早期卡包的笔记 GUID、模型 ID、牌组 ID 和卡片模板序号。本版在原有 20 个字段末尾追加 `Morphology` 与 `WordFamily`，不改变旧字段次序；在独立 Anki 测试库验证升级及复习计划保留。导入仍可能覆盖你自己对原字段的修改，更新前请备份。

从带例句音频的旧完整版升级不会自动删除旧媒体。需要释放空间时，在桌面 Anki「工具 → 检查媒体」中检查未使用文件后清理，再同步。

## 校订范围

曾出现 `crane`「起重机」配「鹤」的例句：原因是只匹配拼写、没有确认所列词义。已有两轮集中修正，相关替换记录与回归校验现在进入版本控制。v0.2.0 又补查了名词、动词及专名冲突，例如 `sue` / Sue、`kindle` / Kindle、`tire` / tyre。

例句含 Tatoeba、Global Voices 语料，以及编写的教学或模板练习句；部分中文由机器翻译补齐。**没有对全部例句逐句完成人工校订，也不保证消除了所有词义、语法和翻译问题。** 自动规则和词性模型只生成候选，不能作为语义正确性的证明。维护状态保存在 JSONL 的 `review` 字段，不在学习卡片上弹出提示。

新增参考站 [雅思词典](https://isdc.pages.dev/) 匹配 11,798 个词条，用于交叉查阅及筛选词族。其词条与原表大多相同，不算独立验证；自动助记、派生词和真题材料没有整批复制到本项目。

## 参与迭代

- 单词、释义、例句、翻译：编辑 `deck-source/*.jsonl` 中相应词条；每行一条，`guid` 请保持不变。
- 构词、词族：编辑 `deck-source/morphology.json`；优先有把握的现代构词，无可靠解释时留空。
- 已知消歧例句：`deck-source/example-overrides.json` 保存本轮有意选择的双语例句。修改时同时更新 JSONL 与补丁，运行校验。
- 卡片外观：`templates/front.html`、`back.html`、`style.css`。
- 提交 PR 前运行下面的检查；[贡献说明](CONTRIBUTING.md) 介绍如何提供语境和依据。

## 本地构建

需要 Python 3.10+。所有脚本只读写项目文件，不访问你的 Anki 个人资料库。

```sh
python -m venv .venv
# 激活虚拟环境后：
python -m pip install -r requirements.txt
python scripts/validate.py
python -m unittest discover -s tests -v
```

只有源码时可以生成不带音频的测试卡包：

```sh
python scripts/build.py --text-only --output dist/text-only.apkg
```

生成完整版本，先下载本项目任一含音频的发行卡包，并提取单词音频：

```sh
python scripts/extract_media.py path/to/downloaded.apkg
python scripts/build.py
```

音频通过 `media-manifest.json` 的 SHA-256 校验。`media/` 与 `dist/` 不进入 Git；成品及校验文件放在 Releases。构建可重现数据和模板内容；ZIP 时间戳与 Anki 修改时间会随构建变化，不承诺字节级完全相同。

可选的实际 Anki 升级检查（需额外安装 `anki==26.9.3`）：

```sh
python scripts/check_upgrade.py previous.apkg dist/anki-ielts-v0.2.0.apkg
```

此脚本新建临时测试库，导入前后版本、模拟一张已复习卡并检查卡片 ID 与计划保留，结束后关闭并清理测试库。

## 来源与许可

本项目代码及原创构词说明采用 MIT；第三方词表、例句和其他内容保留各自权利与许可，详见 [来源与许可](docs/SOURCES.md)。维护者已确认取得原作者授权，并提供了[原帖链接](https://linux.do/t/topic/2863425)及沟通截图作为记录；该授权不等于将原词表改授为 MIT，具体沟通与范围见来源说明。
