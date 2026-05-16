# 文档目录

```
docs/
├── architecture/         三层架构设计
│   ├── overview.md       架构总览 — 从顶层理解系统
│   ├── layer-1-capture.md    采集层：信息如何进入系统
│   ├── layer-2-structure.md  结构层：知识单元如何稳定存在
│   ├── layer-3-evolution.md  演化层：认知如何逐渐成熟
│   └── design-decisions.md   设计决策记录
├── collaboration/        AI 协作协议
│   ├── overview.md       协作模型总览
│   ├── tier-boundary.md  操作权限分级（Tier 1/2/3）
│   ├── signal-detection.md  系统信号判断协议
│   └── vault-structure-reference.md  Vault 结构参考
└── conventions/          约定规则
    ├── naming.md         命名规则
    ├── yaml-metadata.md  YAML 元数据规范
    └── note-templates.md 笔记模板约定
```

## 阅读路径

**推荐阅读顺序**：

1. `architecture/overview.md` — 先理解三层架构的核心理念
2. 读三层各自的细节文档（按需深入）
3. `architecture/design-decisions.md` — 了解关键设计取舍
4. 如果对 AI 协作感兴趣，读 `collaboration/`
5. 如果需要实际搭建，读 `conventions/`
