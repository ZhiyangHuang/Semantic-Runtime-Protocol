# SRP Implementation Tasks

本文档将 `temporary1.md`、`temporary2.md`、`temporary3.md` 中的核心想法整理成一份可执行、可维护、可验收的 SRP 实施清单。

目标不是把 SRP 绑定到某个模型的内部缓存，而是把它完善为一个模型无关的 **Semantic Runtime Protocol**：

- SRP 缓存的是 `semantic runtime state`，不是 token hidden state。
- SRP 位于应用层和推理运行时之上，不直接操作 Transformer 的 KV Cache。
- SRP 的核心贡献不是“更会做摘要”，而是把长上下文交互提升为一个可演化、可验证、可诊断的 `semantic state machine`。

---

## 1. 总目标

将当前 SRP 从：

```text
压缩语义文本 + 恢复语义文本 + 多层验证
```

升级为：

```text
Conversation
-> Semantic Parser
-> Typed Semantic Objects
-> SemanticState
-> Runtime Metadata
-> Compress
-> Recover
-> Object Alignment
-> Importance-aware Verification
-> State Update / State Learn
```

核心原则：

- 不直接依赖 KV Cache，也不声称 “SRP caches V”。
- SRP 缓存的是语义状态，不是 token 序列。
- Runtime 的基本粒度是 `semantic object`，不是 token。
- 基础 verifier 仍以 object alignment 为核心，semantic similarity 是增强层，不替代基础 verifier。
- `SemanticState` 不是被动数据容器，而是会记录历史、更新置信度、调整重要性的 active runtime。
- 无模型规则版是主实现路径。
- embedding encoder、LLM judge、attention/saliency 都只能是可选增强，不能成为 SRP 的核心依赖。
- SRP 更强的论文定位是 `semantic state machine` / `semantic dynamical system`，用 drift、drift rate、stability curve 衡量长期稳定性。

---

## 2. 协议定位与边界

### 2.1 协议定位

需要在项目文档中明确写出以下结论：

- SRP caches semantic state rather than token sequences.
- SRP 不操作模型内部 KV Cache。
- SRP 是 model-independent runtime protocol。
- 稳定恢复模板有可能提升 `prompt-prefix stability`，从而间接提高支持 prefix caching 系统中的 prompt cache reuse。

验收标准：

- [x] 文档中不再出现 “SRP caches V” 这类不准确表述。
- [x] 文档中出现 `semantic runtime state`、`prompt-prefix stability`、`model-independent runtime protocol`。
- [x] 文档中明确说明 KV Cache 只能是可选实验信号，不能是 SRP 核心依赖。

### 2.2 协议本体定义

在主文档中给出正式的 SRP 状态定义：

```text
SemanticState =
    TypedSemanticRepresentation
  + Runtime Metadata
  + Global Verification History
  + Optional Derived State Views
```

其中：

- `TypedSemanticRepresentation` 是 primary state。
- `Runtime Metadata` 是每个 semantic object 的运行时属性。
- `Global Verification History` 是整轮状态演化历史。
- `Derived State Views` 包括 `state_vector`、embedding view、drift view 等可选派生表示。

验收标准：

- [x] 文档中把 `SemanticState` 定义为协议层状态，而不是普通内存容器。
- [x] 文档中显式区分 `primary state` 和 `derived state view`。
- [x] 文档中明确 `state_vector` 不能替代 object state。

### 2.3 协议操作符

将 SRP 定义为一组固定 operator：

```text
parse -> compress -> recover -> validate -> observe/update
```

各自职责：

- `parse`: text -> typed semantic objects
- `compress`: state -> compact runtime package
- `recover`: package -> recoverable prompt/state
- `validate`: source vs recovered -> alignment/coverage/drift
- `observe/update`: validation -> runtime metadata/history update

验收标准：

- [x] 文档中明确列出 5 个 operators。
- [x] 每个 operator 都有输入、输出、职责说明。
- [x] 当前 pipeline 能映射到这些 operators。

---

## 3. 核心数据结构

### 3.1 `SemanticObjectMetadata`

在 [state.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/state.py) 中维护单个 semantic object 的运行时元数据：

```python
@dataclass
class SemanticObjectMetadata:
    importance: float = 1.0
    confidence: float = 1.0
    access_count: int = 0
    retrieval_count: int = 0
    verification_passes: int = 0
    verification_failures: int = 0
    drift_count: int = 0
    last_verified_round: int = 0
```

验收标准：

- [x] dataclass 可序列化为 dict。
- [x] 默认值不破坏旧版 `SemanticState` 初始化。
- [x] 字段命名与 verifier / runtime update 逻辑一致。

### 3.2 `VerificationRecord`

在 [state.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/state.py) 中维护全局历史记录：

```python
@dataclass
class VerificationRecord:
    round_id: int
    coverage: float
    drift: float
    alignment_score: float
    passed: bool
    timestamp: str = ""
```

要求：

- 不保存原始长文本。
- 足够支撑 round-coverage-drift 曲线。
- 可导出成 records / JSON。

验收标准：

- [x] `VerificationRecord` 有 `as_dict()`。
- [x] 记录内容足够支撑趋势图。
- [x] 不保存完整长文本历史。

### 3.3 `SemanticState`

扩展 `SemanticState` 至少包含：

```python
runtime_metadata: Dict[str, SemanticObjectMetadata]
history: List[VerificationRecord]
round_id: int
state_vector: Optional[List[float]]
state_vector_encoder: Optional[str]
```

验收标准：

- [x] `SemanticState.as_dict()` 输出 `runtime_metadata`、`history`、`round_id`。
- [x] 旧调用方不传这些字段时仍能运行。
- [x] `compress_state()` / `recover_state()` 不因新增字段报错。
- [x] `as_dict()` 对 `state_vector` 只输出摘要，不强制输出完整向量。

### 3.4 稳定 object id

定义稳定 object id：

```text
{object_type}:{normalized_value_hash}
```

示例：

```text
constraint:8f31ab12
fact:0912cc7e
anchor:77aa019d
```

验收标准：

- [x] 同一类型、同一规范化值得到相同 id。
- [x] 不同类型即使值相同也得到不同 id。
- [x] id 不依赖对象在列表中的顺序。
- [x] 放在 `state.py` 或 `semantic_parser.py` 均可，但调用路径清晰。

---

## 4. 让 `SemanticState` 具备学习能力

### 4.1 `ensure_runtime_metadata()`

在 `SemanticState` 中增加：

```python
def ensure_runtime_metadata(self, anchor_memory: str = "") -> Dict[str, SemanticObjectMetadata]:
    ...
```

逻辑：

1. 调用 `ensure_typed_representation()`。
2. 遍历 semantic objects。
3. 为缺失 metadata 的 object 创建默认 `SemanticObjectMetadata`。
4. 根据对象类型设置基础 importance：
   - `constraint`: 1.0
   - `anchor`: 0.8
   - `fact`: 0.6

验收标准：

- [x] 每个 semantic object 都有 metadata。
- [x] 重复调用不会重置已有统计值。
- [x] constraint 默认 importance 高于 fact。

### 4.2 `observe_verification()`

在 `SemanticState` 中增加：

```python
def observe_verification(self, validation: Dict, committed: bool) -> None:
    ...
```

逻辑：

1. `round_id += 1`
2. 读取 `validation["object_alignment"]`
3. 高 similarity 的对象增加 `verification_passes`
4. 低 similarity / missing 的对象增加 `verification_failures` 与 `drift_count`
5. 写入一条 `VerificationRecord`
6. 调用 importance / confidence 更新逻辑

验收标准：

- [x] 成功匹配会增加 pass count。
- [x] 失败匹配会增加 failure 与 drift count。
- [x] 每轮验证后 `history` 增加一条记录。
- [x] `committed=False` 时也记录历史，并可降低 confidence。

### 4.3 importance 更新公式

先使用一个简单、可解释的更新公式：

```text
base_weight = constraint 1.0, anchor 0.8, fact 0.6
pass_rate = (passes + 1) / (passes + failures + 2)
access_factor = min(1.0, log1p(access_count) / 3)
drift_penalty = 1 / (1 + drift_count)
importance = clamp(base_weight * (0.5 + pass_rate) * (0.7 + access_factor) * drift_penalty, 0.0, 1.0)
confidence = clamp(pass_rate * drift_penalty, 0.0, 1.0)
```

验收标准：

- [x] importance 始终在 0 到 1 之间。
- [x] 反复通过验证的对象 importance 不下降。
- [x] 反复漂移的对象 importance 或 confidence 会下降。
- [x] 公式有简短注释说明，不追求过早复杂优化。

---

## 5. 升级 semantic similarity

### 5.1 canonicalization 层

在 [validate.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/validate.py) 或相关模块中增加规范化规则：

- 月份：
  - `May 2026`
  - `5/2026`
  - `05/2026`
- 常见缩写：
  - `NYC` -> `New York City`
  - `Prof.` -> `Professor`
  - `CS` -> `Computer Science`
- 保留现有 lowercase / 空白 / 标点规范化

验收标准：

- [x] `May 2026` 与 `5/2026` 的相似度接近或等于 1.0。
- [x] `NYC` 与 `New York City` 的相似度接近或等于 1.0。
- [x] 旧的 exact / substring / Jaccard 逻辑仍可作为 fallback。

### 5.2 `_object_similarity()` 重构

将结构明确为：

```text
canonical exact match
-> known semantic equivalence
-> substring fallback
-> token jaccard fallback
```

验收标准：

- [x] 代码结构上能清楚看出 canonicalization 是第一层。
- [x] fallback 行为与旧版本兼容。
- [x] 返回值始终在 0 到 1。

### 5.3 LLM judge 作为可选仲裁

保留接口，但默认关闭：

```python
def _llm_semantic_equivalence(source_value: str, recovered_value: str, client=None) -> Optional[float]:
    return None
```

要求：

- 默认不调用 LLM。
- 无 `client` 时行为完全确定。
- 仅用于高重要性、规则难以判定、encoder 也不够确定的对象。

验收标准：

- [x] `client=None` 时行为确定。
- [x] 文档中明确 LLM judge 只用于疑难仲裁。
- [x] 不能让 LLM judge 成为基础 verifier。

---

## 6. importance-aware verification

### 6.1 `validate_state()` 接收 runtime metadata

扩展签名：

```python
runtime_metadata: Optional[Dict[str, SemanticObjectMetadata]] = None
```

逻辑：

- 没有 metadata 时沿用 `OBJECT_WEIGHTS`
- 有 metadata 时使用 `base_weight * metadata.importance`

验收标准：

- [x] 旧调用方式不变。
- [x] 有 metadata 时 coverage 体现对象重要性。
- [x] 高 importance constraint 漂移时更容易导致验证失败。

### 6.2 alignment 结果带 object id

在 `_align_objects_by_type()` 的 match 中加入：

```python
"source_object_id": "...",
"recovered_object_id": "..." or None
```

验收标准：

- [x] `observe_verification()` 可直接根据 `source_object_id` 更新 metadata。
- [x] alignment 输出仍保留 `source_value`、`recovered_value`、`similarity`。
- [x] 无匹配时 `recovered_object_id` 为 `None`。

### 6.3 重要性感知 coverage

扩展 `_weighted_alignment_coverage()`：

- 默认权重来自 `OBJECT_WEIGHTS`
- 若对象有 metadata，则 `effective_weight = base_weight * metadata.importance`
- 输出 `coverage_details`

验收标准：

- [x] 无 metadata 时与旧逻辑基本一致。
- [x] 有 metadata 时高 importance 对象影响更大。
- [x] `coverage_details` 输出 average importance 或 effective weight 信息。

### 6.4 `critical_failures`

在 validate 结果中加入：

```python
"critical_failures": [...]
```

规则：

- importance >= 0.8 且 similarity < 0.5 的对象进入 `critical_failures`
- 存在 critical failure 时，验证倾向失败

验收标准：

- [x] 高 importance 对象缺失时 `passed=False`。
- [x] 低 importance 对象缺失不一定阻塞提交。
- [x] 失败结果能解释是哪些对象导致失败。

---

## 7. 接入 pipeline 生命周期

### 7.1 初始化 metadata

在 [pipeline.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/pipeline.py) 中创建初始 state 后调用：

```python
state.ensure_runtime_metadata(anchor_memory=anchor_memory)
```

验收标准：

- [x] 第一轮压缩前已有 metadata。
- [x] 不影响现有 vocabulary、term_map、policy。

### 7.2 validate 时传入 metadata

```python
validation = validate_state(..., runtime_metadata=state.runtime_metadata)
```

验收标准：

- [x] pipeline 能运行旧任务。
- [x] validation 结果中出现 importance-aware 字段。

### 7.3 验证后学习

每轮得到 `validation` 和 `committed` 后调用：

```python
state.observe_verification(validation, committed=committed)
```

下一轮 state 保留：

- `runtime_metadata`
- `history`
- `round_id`

验收标准：

- [x] 多轮运行后 `history` 长度等于 cycle 数。
- [x] metadata 的 pass/failure/drift 计数跨轮保留。
- [x] rollback 时不丢失运行时历史。

### 7.4 records 输出 runtime 指标

每轮 record 至少增加：

```python
"runtime_round": state.round_id
"runtime_history_length": len(state.history)
"critical_failures": validation.get("critical_failures", [])
"mean_object_importance": ...
```

验收标准：

- [x] records 可直接观察 runtime 是否在演化。
- [x] 不输出过长 metadata 全量内容。

---

## 8. 压缩与恢复保留运行时信息

### 8.1 `compress_state()` 输出 runtime summary

返回中加入轻量摘要：

```python
"runtime_summary": {
    "object_count": ...,
    "high_importance_count": ...,
    "mean_importance": ...,
    "history_length": ...
}
```

验收标准：

- [x] 不把完整 history 放进压缩 prompt。
- [x] summary 能帮助调试 SRP runtime。
- [x] `client=None` 和 `client!=None` 两条路径都能返回该字段。

### 8.2 `recover_state()` 不强行生成新 metadata

原则：

- `recover_state()` 只恢复语义内容
- runtime metadata 由原 state 根据验证结果维护
- recovered state 可为空 metadata，合并逻辑由 pipeline 完成

验收标准：

- [x] `recover_state()` 不覆盖原 state 的 runtime metadata。
- [x] pipeline 负责把 committed memory 和旧 runtime history 合并到下一轮 state。

### 8.3 恢复模板稳定性

规范恢复模板骨架：

```text
SYSTEM
STATE SUMMARY
STATE OBJECTS / CONSTRAINTS
CURRENT TURN
```

目标：

- 减少 recover prompt 的结构波动
- 为 `prompt-prefix stability` 提供可解释依据

验收标准：

- [x] 恢复模板段落顺序固定。
- [x] 模板变化主要发生在槽位内容，而不是区块骨架。
- [x] 不把完整历史直接重新拼回 recover prompt。

### 8.4 模板稳定性诊断字段

建议增加：

```text
recover_template_version
recover_template_sections
recover_prompt_word_count
```

验收标准：

- [x] pipeline records 中能看到模板结构摘要。
- [x] 字段是轻量摘要，不存完整 prompt。
- [x] 不影响 `client=None` 路径。

---

## 9. 测试任务

### 9.1 runtime 单元测试

测试内容：

- metadata 初始化
- observe verification 导致 passes / failures 变化
- history 增长
- importance / confidence 约束在 0 到 1

验收标准：

- [x] 测试不依赖外部 LLM。
- [x] 使用小型手写 validation dict。

### 9.2 canonicalization 测试

至少覆盖：

- `May 2026` vs `5/2026`
- `NYC` vs `New York City`
- `Prof.` vs `Professor`
- `CS` vs `Computer Science`

验收标准：

- [x] 每组相似度高于 0.85。
- [x] 完全无关文本相似度仍较低。

### 9.3 importance-aware verification 测试

构造两类对象：

- 高 importance constraint 缺失
- 低 importance fact 缺失

验收标准：

- [x] 高 importance constraint 缺失导致 critical failure。
- [x] 低 importance fact 缺失不自动进入 critical failure。
- [x] 无 metadata 时旧 coverage 逻辑仍可用。

### 9.4 多轮 pipeline 测试

运行 2 到 3 个 cycle。

验收标准：

- [x] 每轮都有 `runtime_history_length`。
- [x] `history` 长度随 cycle 增长。
- [x] records 中保留 validation、coverage、drift、critical failures。

---

## 10. Semantic State Encoder 抽象

### 10.1 encoder 接口

文件：

[encoder.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/encoder.py)

接口：

```python
class SemanticStateEncoder:
    name: str
    dimension: int | None

    def encode_passage(self, text: str) -> List[float]:
        ...

    def encode_query(self, text: str) -> List[float]:
        ...
```

验收标准：

- [x] 接口不依赖具体 embedding 模型。
- [x] `encode_passage()` / `encode_query()` 明确区分。
- [x] 无 embedding 依赖时导入 `srp` 不报错。

### 10.2 `HashingSemanticEncoder`

先实现确定性的无模型 encoder：

```python
class HashingSemanticEncoder(SemanticStateEncoder):
    dimension = 256
```

逻辑：

- tokenize
- stable hash
- 固定维度投影
- L2 normalize

验收标准：

- [x] 不依赖 torch / transformers / sentence-transformers。
- [x] 同一文本多次编码结果一致。
- [x] 可计算 cosine similarity。
- [x] 仅作为 deterministic fallback，不声称强语义理解。

### 10.3 可选 `E5SmallEncoder`

建议：

```python
class E5SmallEncoder(SemanticStateEncoder):
    model_name = "intfloat/e5-small-v2"
```

要求：

- passage 使用 `passage:`
- query 使用 `query:`
- normalize embeddings
- 输出维度 384

验收标准：

- [x] 未安装依赖时不影响无模型测试。
- [x] 安装依赖后 `encode_passage("hello")` 返回长度 384。
- [x] 支持 `.env` 配置 `SRP_ENCODER_MODEL=intfloat/e5-small-v2`。

### 10.4 encoder factory

```python
def build_encoder(kind: str | None = None) -> SemanticStateEncoder | None:
    ...
```

建议支持：

```text
none
hashing
e5-small-v2
```

验收标准：

- [x] 默认 `none` 或 `hashing`，不默认下载模型。
- [x] `.env` 支持 `SRP_ENCODER=none|hashing|e5-small-v2`。
- [x] embedding encoder 与 LLM judge 配置分离。

---

## 11. Drift、Stability 与 Bounded Update

### 11.1 `cosine_similarity()`

在 [encoder.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/encoder.py) 中实现：

```python
def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    ...
```

验收标准：

- [x] 不依赖 numpy 也能运行。
- [x] 空向量返回 0.0。
- [x] 相同向量返回接近 1.0。

### 11.2 `serialize_state_for_encoding()`

定义稳定的 state serialization：

- memory
- constraints
- global/local vocabulary
- term_map
- high-importance runtime metadata 摘要

验收标准：

- [x] 输出稳定，字段顺序固定。
- [x] 不包含完整 history 长文本。
- [x] 同一 state 重复序列化结果一致。

### 11.3 记录 semantic drift

若 encoder 可用：

```text
source_vector = encode_passage(pre_cycle_state_text)
recovered_vector = encode_passage(recovered_state_text)
semantic_similarity = cosine(source_vector, recovered_vector)
semantic_drift = 1 - semantic_similarity
```

验收标准：

- [x] records 中输出 `semantic_similarity`、`semantic_drift`、`encoder_name`。
- [x] encoder 为 `None` 时这些字段为 `None`。
- [x] semantic drift 不替代 object coverage。

### 11.4 drift rate

记录：

```text
drift_rate_t = semantic_drift_t - semantic_drift_{t-1}
```

或：

```text
state_divergence_t = 1 - cosine(S_t, S_0)
```

验收标准：

- [x] records 输出 `semantic_drift_rate`。
- [x] records / history 可画 drift curve。
- [x] 文档中明确 claim 是降低 drift growth rate，而不是保证 drift 为零。

### 11.5 bounded semantic update

定义：

```python
def update_state_vector(previous, current, decay: float = 0.85) -> List[float]:
    ...
```

公式：

```text
S_t = normalize(decay * S_{t-1} + (1 - decay) * E(x_t))
```

验收标准：

- [x] 输入维度不一致时报清楚错误。
- [x] 输出 L2 normalized。
- [x] `decay` 支持 `.env`：`SRP_STATE_DECAY=0.85`。

### 11.6 vector state 的边界

要求：

- `state_vector` 只用于 drift / stability / retrieval / rerank
- commit / rollback 仍以 object state 与 runtime metadata 为准

验收标准：

- [x] 没有验证逻辑只依赖 vector similarity 通过。
- [x] object coverage 仍是基础 verifier。
- [x] vector drift 只影响诊断或可选 rerank。

---

## 12. Semantic Memory Index 与压缩选择

### 12.1 `chunk_memory()`

```python
def chunk_memory(memory: str, max_words: int = 80) -> List[str]:
    ...
```

策略：

- 优先按句子切
- 过长句子按 word window 切
- 保留顺序与 `chunk_id`

验收标准：

- [x] 长上下文不再退化为只保留尾部。
- [x] 每个 chunk 有稳定 id。
- [x] 不依赖模型。

### 12.2 无模型 chunk saliency

优先实现规则版 saliency：

- 与 constraints 的 token overlap
- 与 expected keywords 的 overlap
- 数字、日期、专名、选项字母加权
- 首段 / 标题块加权

验收标准：

- [x] 不需要 embedding。
- [x] 输出 top-k chunks。
- [x] records 记录 `selected_chunk_ids`。

### 12.3 embedding rerank

若 encoder 可用：

- query = constraints + current query + expected keywords
- passage = each chunk
- 使用 cosine 排序

验收标准：

- [x] embedding rerank 只重排候选，不覆盖规则 saliency。
- [x] encoder 不可用时自动退化到规则 saliency。
- [x] records 中记录 `chunk_selection_method=rule|embedding|hybrid`。

### 12.4 本地 LLM chunk judge

若启用本地 Qwen：

```text
Given task constraints and a memory chunk, score whether this chunk is answer-critical from 0 to 1.
Return only JSON: {"score": 0.0, "reason": "..."}
```

约束：

- 默认关闭
- 只对规则 top-N 候选调用
- judge 输出不能直接决定 commit，只能作为 saliency bonus

验收标准：

- [x] `.env` 支持 `SRP_USE_LLM_JUDGE=false`。
- [x] judge 失败时不影响 pipeline。
- [x] records 记录 `llm_judge_calls`、`llm_judge_failures`。

---

## 13. 两层历史与对象生命周期

### 13.1 Global History 与 Per-Object Metadata 的边界

明确：

- global history 记录 round 级 coverage / drift / commit 演化
- per-object metadata 记录 object importance / confidence / pass / failure / drift
- 不引入 token-level history 作为协议核心

验收标准：

- [x] 文档中明确 `global history` 与 `per-object metadata` 的不同职责。
- [x] 不把 token history 写成协议核心。
- [x] `VerificationRecord` 与 `SemanticObjectMetadata` 的关系可解释。

### 13.2 对象生命周期摘要

增加轻量摘要：

```text
stable_object_count
drifting_object_count
high_risk_object_ids
```

建议纳入：

- `runtime_summary`
- `state_continuity_summary`

验收标准：

- [x] 不输出完整对象级长日志。
- [x] 可快速发现持续漂移的关键对象。
- [x] 生命周期摘要与 `critical_failures` 的解释方向一致。

---

## 14. 生成器与语义评估器解耦

### 14.1 双模型角色分离

文档中明确区分：

```text
Generator: Qwen / local LLM
Semantic Evaluator: Hashing / E5 / BGE / Arctic
```

要求：

- generator 负责生成与恢复文本
- evaluator 负责 semantic similarity / drift / retrieval / rerank
- SRP 本体不依赖某一个 evaluator backbone

验收标准：

- [x] 文档中出现 `generation model` 与 `semantic evaluator` 的角色区分。
- [x] evaluator failure 不阻塞 rule-only SRP。
- [x] 文档明确 SRP 的核心贡献不等于某个 embedding 模型。

### 14.2 evaluator 能力边界

明确：

- HashingEncoder 是 deterministic fallback
- E5/BGE/Arctic 是可替换 evaluator
- LLM judge 只做疑难仲裁

验收标准：

- [x] 文档中能看出 rule-only、encoder-assisted、judge-assisted 三层关系。
- [x] evaluator 不是协议唯一入口。
- [x] `client=None` 与 `encoder=None` 的退化路径写清楚。

---

## 15. 论文与实验表达

### 15.1 Related Work 定位

建议明确与以下方向的边界：

- Transformer-XL / KV cache：hidden state recurrence，不是 semantic protocol
- Memorizing Transformers / kNN-LM：external memory，不是 semantic state lifecycle
- RAG / RETRO：retrieve text，不管理 state drift
- Prompt compression / LongLLMLingua：压缩 prompt，不定义 runtime state machine
- Representation drift / continual learning：研究训练时表示漂移，不是 inference-time semantic runtime

验收标准：

- [x] 明确 SRP 的创新不是单个组件，而是 unified semantic state protocol。
- [x] 使用 `State definition + Operators + Stability metric` 三段定义 SRP。

### 15.2 推荐实验指标

建议指标：

- coverage score
- drift score
- critical failure count
- mean object importance
- high importance object preservation rate
- history length
- prompt token reduction
- semantic drift
- semantic drift rate
- semantic stability

验收标准：

- [x] 指标能体现 SRP 不只是 memory compression。
- [x] 指标能体现 Runtime State 随轮次演化。

### 15.3 推荐实验组

主实验建议：

- no SRP：tail context 或普通 summary
- SRP rule-only：object state + runtime metadata + rule saliency
- SRP hybrid：rule saliency + optional encoder drift metrics

鲁棒性实验建议：

- HashingEncoder
- E5-small-v2
- BGE-small-en-v1.5
- Arctic-Embed-S

验收标准：

- [x] 固定 generation model，仅更换 semantic evaluator。
- [x] 输出 JSONL 和汇总 CSV。
  - 已提供 `srp_experiment/export_csv.py`，支持单任务、批量 `--task-json`、批量 `--input-jsonl`。
  - 推荐用法：
    ```bash
    python srp_experiment/export_csv.py --cycles 1 --output-csv srp_experiment/tmp/srp_records.csv
    python srp_experiment/export_csv.py --task-json srp_experiment/tmp/task_a.json --task-json srp_experiment/tmp/task_b.json --task-id-prefix batch1- --output-csv srp_experiment/tmp/srp_records_batch.csv
    python srp_experiment/export_csv.py --input-jsonl srp_experiment/tmp/tasks.jsonl --task-id-prefix expA- --output-csv srp_experiment/tmp/srp_records_jsonl.csv
    ```
- [x] 证明 SRP 不绑定某个 embedding backbone。

---

## 16. 推荐实现顺序

建议按照以下顺序实施，不要跳步：

1. 核心数据结构：`SemanticObjectMetadata`、`VerificationRecord`、`SemanticState`
2. stable object id
3. `ensure_runtime_metadata()` / `observe_verification()` / importance 更新
4. canonicalization 与 semantic matching
5. importance-aware verification
6. pipeline 生命周期接入
7. `compress_state()` / `recover_state()` 的 runtime summary 与 continuity summary
8. `HashingSemanticEncoder` 与 encoder factory
9. drift / drift rate / stability 指标
10. `chunk_memory()` 与规则 saliency
11. 模板稳定性与对象生命周期摘要
12. 可选增强：E5 / rerank / LLM judge
13. 文档、related work、实验与 ablation

---

## 17. 收尾分组

### 17.1 Protocol Core

以下属于 SRP 本体，应该优先完成：

- `SemanticState` 的正式状态定义
- typed objects + runtime metadata + history
- stable object id
- importance-aware verification
- pipeline 跨轮演化
- runtime summary / continuity summary
- drift / drift rate / stability 基础指标
- chunk saliency
- 恢复模板稳定性

### 17.2 Optional Semantic Evaluators

以下属于可选增强：

- `HashingSemanticEncoder`
- `E5SmallEncoder`
- embedding rerank
- soft semantic evidence
- LLM judge

### 17.3 Paper / Ablation

以下属于论文与实验收尾：

- related work 对照
- robustness / ablation
- drift curve 可视化
- claim 收敛为 bounded drift / stability

---

## 18. 当前判断

如果只关心 SRP 本体是否完整，核心判断标准不是“有没有更多模型”，而是：

- 是否已经形成 `semantic runtime state`
- 是否已经形成 `state lifecycle`
- 是否已经形成 `object-level verification + runtime update`
- 是否已经形成 `stability diagnostics`

当这四件事都完成后，SRP 才真正从：

```text
semantic memory compression
```

升级为：

```text
semantic runtime state management
```

---

## 19. 剩余纯文档 / 纯实验项

以下项目保留未勾状态，但它们不再代表 SRP 主体实现缺口，而是文档写作、论文表达或外部依赖验证：

### 19.1 文档写作

- 当前主体协议说明已进入 `README.md`。
- 剩余文档工作主要是把这些说明进一步改写成论文正文，而不是继续补产品文档缺口。

### 19.2 外部依赖验证

- `10.3` 中安装 `sentence-transformers` 后，实测 `E5SmallEncoder.encode_passage("hello")` 返回 384 维。

### 19.3 论文与实验表达

- `15.x` 中 related work 的正式写法、实验章节文案、ablation 叙述、图表和曲线展示。
- `17.3` 中 robustness / ablation / drift curve 可视化的最终成稿表达。

### 19.4 当前未勾项总览

为避免和 SRP 本体实现混淆，当前仍未勾选的条目可以直接归并为以下三类：

1. 纯文档写作
- 把 README 中已有的协议定位、状态定义、operators、judge 边界改写为论文正文版本。

2. 外部依赖验证
- `10.3`：在真实安装 `sentence-transformers` 的环境中，验证 `E5SmallEncoder.encode_passage("hello")` 返回 384 维。

3. 论文与实验成稿
- `15.1`：related work 的正式边界写法。
- `15.2`：实验指标在论文中的组织与解释。
- `15.3`：ablation、robustness、固定 generation model / 更换 evaluator 的实验呈现。
- `17.3`：bounded drift / stability claim 的最终图表和文字收口。
