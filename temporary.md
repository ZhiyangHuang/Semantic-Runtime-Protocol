有，而且**不只是有人做，实际上已经形成了一个小研究方向**。不过，你提出的想法比现有工作还要更进一步。

你的理解可以描述成：

> **不是根据词频(TF-IDF)判断重要词，而是根据语义向量判断：删除某个词后，句子的语义损失有多大，从而得到每个词的信息密度（Information Density）。**

这和目前几类工作关系如下。

---

## 1. Token Importance（最接近你的想法）

目前已经有论文直接研究：

> **每个 token 对整个 sentence embedding 的贡献是多少？**

例如 2024 年的一篇论文提出：

> **Advanced sentence embedding considering token importance**

它不是简单平均所有 token embedding，而是：

```
Sentence
↓

BERT

↓

Token Embedding

↓

计算每个token的重要性(weight)

↓

Weighted Pooling

↓

Sentence Embedding
```

其中：

```
important token
↓

weight 大

↓

最终 sentence embedding 更受它影响
```

而不是

```
所有token权重一样
```

论文甚至利用可解释 AI（XAI）和摘要模型来计算 token importance，再用这些权重构造更好的句向量。实验表明，这种方法优于普通平均池化和 CLS pooling。([ScienceDirect][1])

---

## 2. 删除一个词，看语义变化（Semantic Contribution）

另一类研究更接近你说的：

假设一句话：

```
The cat sat on the mat.
```

得到

```
Embedding(S)
```

然后依次删除：

```
The
↓

Embedding(S-The)
```

```
cat
↓

Embedding(S-cat)
```

```
sat
↓

Embedding(S-sat)
```

计算

```
cos(E(S),E(S-word))
```

如果：

```
删除 cat

相似度下降很多
```

说明

```
cat
```

语义贡献高。

如果

```
删除 the

变化几乎没有
```

说明

```
the
```

信息密度低。

很多解释 Transformer 的工作都会采用这种 **ablation（消融）** 思路来衡量 token 的贡献。([ScienceDirect][2])

---

## 3. Information Gain（信息增益）

还有研究发现：

**Embedding 本身甚至编码了词的信息量。**

例如 EMNLP 的工作：

> **Norm of Word Embedding Encodes Information Gain**

作者发现：

```
embedding 的长度(norm)

≈

这个词的信息增益
```

信息越大的词：

```
embedding norm 越大
```

而不是随机形成的。([CiNii Research][3])

---

## 4. TF-IDF 的语义版本

传统：

```
重要度

=

TF-IDF
```

只看：

```
出现次数

+

是否常见
```

后来有人提出：

```
Word Embedding

+

Information Weight
```

即：

```
Sentence Embedding

=

Σ

WordEmbedding

×

InformationWeight
```

权重来自信息论而不是词频，因此更能反映语义重要性。([ScienceDirect][4])

---

# 但是，你提出的其实还有一点不同

你说的是：

> **不是单独算 token importance，而是计算 token 与整个句子语义中心的关系。**

例如：

```
Sentence

↓

Sentence Embedding
```

然后：

```
每个词

↓

Word Embedding
```

计算：

```
cos(word_i,

sentence_embedding)
```

例如

```
Sentence：

The red sports car suddenly crashed.
```

假设：

```
Sentence embedding
```

与：

```
car

0.92

crashed

0.90

sports

0.74

red

0.42

the

0.08
```

于是得到：

```
car
crashed

>>

sports

>>

red

>>

the
```

这其实就是一种：

> **Semantic Centrality（语义中心性）**

目前直接以这个名字做的不算多，但它与 **Attention、Token Importance、Embedding Attribution** 等方向密切相关。

---

# 我觉得你这里还有一个可以发展的方向

如果结合你的 **SRP（Semantic Runtime Protocol）**，可以设计一个新的指标，例如：

对于每个 token：

[
Density_i
=========

Importance_i
\times
Centrality_i
\times
Uniqueness_i
]

其中：

* **Importance**：删除该 token 后句向量变化（Semantic Loss）。
* **Centrality**：token 与句向量的余弦相似度。
* **Uniqueness**：该 token 是否提供了其他 token 无法替代的信息（例如基于上下文冗余或信息增益）。

这样就能得到：

```
Token
↓

Semantic Density Score
↓

保留高密度token

删除低密度token
```

这与传统摘要（extractive summarization）不同，它关注的是**语义压缩**而不是句子抽取。

**如果你把这个扩展到 SRP 中，作为“语义压缩时保留哪些 token”的原则，我认为它会比当前简单的关键词或 TF-IDF 策略更有研究价值，也比现有的 weighted pooling 更偏向运行时语义协议，而不是仅仅改进句向量表示。**

[1]: https://www.sciencedirect.com/science/article/abs/pii/S0925231223011104?utm_source=chatgpt.com "Advanced sentence-embedding method considering token importance based on explainable artificial intelligence and text summarization model - ScienceDirect"
[2]: https://www.sciencedirect.com/science/article/pii/S2468502X21000097?utm_source=chatgpt.com "USEVis: Visual analytics of attention-based neural embedding in information retrieval - ScienceDirect"
[3]: https://cir.nii.ac.jp/crid/1870865117635296896?utm_source=chatgpt.com "Norm of Word Embedding Encodes Information Gain | CiNii Research"
[4]: https://www.sciencedirect.com/science/article/pii/S0885230817302887?utm_source=chatgpt.com "Unsupervised sentence representations as word information series: Revisiting TF–IDF - ScienceDirect"

有，而且**2024–2026 这一两年开始明显出现了**，不过和你的设想还是有区别。我查了一下最新论文，目前大概可以分成五类。

---

# 1. Token Importance + Multi-Vector Retrieval（最接近）

这是目前最接近你说法的方向。

2026 AAAI 有一篇论文：

> **Incorporating Token Importance in Multi-Vector Retrieval**

它是在 ColBERT 的基础上做的。

传统 ColBERT：

```
Query

↓

每个token

↓

Document token

↓

MaxSim

↓

全部token求和
```

论文改成：

```
Query token

↓

Importance Weight

↓

Weighted MaxSim

↓

Score
```

也就是说：

并不是所有 query token 都一样重要。

例如

```
"What causes lung cancer"

What

0.05

causes

0.3

lung

0.95

cancer

1.0
```

最后：

```
Score

=

Σ

weight_i × similarity_i
```

效果：

* Recall@10 提升约 1–4%
* 不需要重新训练 embedding，只训练 token weight 即可。([AAAI Publications][1])

---

# 2. Token-Level RAG

还有一些论文直接把 token 引入 RAG。

例如：

**A Theory for Token-Level Harmonization in RAG**

它研究的问题不是：

> 哪个 token 更重要？

而是：

> **每生成一个 token，到底应该相信 LLM 还是 Retrieval？**

它提出：

```
LLM

↓

预测token

↑↓

RAG

↓

预测token

↓

融合
```

最后：

对于每一个输出 token，

动态决定：

```
相信 Retrieval

还是

相信 LLM
```

这个方向叫：

> **Token-level RAG**

但是：

它关注的是

**生成阶段。**

不是：

**检索阶段。** ([arXiv][2])

---

# 3. Token Retrieval

Google DeepMind 做了另一件事。

论文：

> **Rethinking the Role of Token Retrieval in Multi-Vector Retrieval**

它发现：

以前：

```
整个document

↓

所有token

↓

全部比较
```

效率很低。

于是他们：

先预测：

```
哪些token值得拿出来比较？
```

然后：

只比较：

```
重要token
```

速度提升非常大，

同时精度还提高。([Google DeepMind][3])

---

# 4. Proposition Retrieval

还有一个方向其实很值得注意。

论文：

> Dense X Retrieval

提出：

不要检索：

```
Paragraph
```

也不要：

```
Sentence
```

而是：

```
Proposition
```

例如：

文章：

```
Apple released iPhone 15 in 2023.

It uses USB-C.

Battery lasts longer.
```

他们不是切成：

```
Sentence1

Sentence2

Sentence3
```

而是：

```
Fact1

Apple

release

iPhone15

2023

Fact2

iPhone15

USB-C

Fact3

Battery

Longer
```

也就是：

**按语义事实切分。**

作者认为：

> 信息密度更高。

对于 RAG 更好。([Deep Paper][4])

---

# 5. Semantic Tokens

还有人提出：

**Semantic Tokens in RAG**

他的想法不是：

token embedding，

而是：

```
Semantic Token

↓

代表一个概念
```

例如：

```
large language model
```

不是：

```
large

language

model
```

而是：

```
LLM

↓

一个Semantic Token
```

再进行 Retrieval。([arXiv][5])

---

# 但是，我觉得你的想法仍然和这些工作有一个核心区别

你提出的是：

> **利用句向量和词向量之间的语义关系，计算每个词的"信息密度"，再用于 RAG。**

也就是说，你不是仅仅做：

```
Token Weight
```

而是：

```
Sentence Embedding
          ↑
          │
Word Embedding

↓

Semantic Density
```

再利用它：

```
Semantic Density

↓

过滤token

↓

生成新的Embedding

↓

RAG
```

这一点，目前我没有找到公开论文**完全按照这个流程实现**。

现有工作大多数都是：

* Token importance（基于注意力、梯度、IDF）
* Token retrieval（提高效率）
* Multi-vector retrieval（ColBERT）
* Semantic chunking
* Proposition retrieval

而不是：

> **用"语义密度（Semantic Density）"重构查询向量或文档向量，再进行检索。**

---

## 我认为这里真正有研究价值的地方

如果我是审稿人，我会认为下面这个方向比"给 token 加权"更有新意：

```
Query

↓

Sentence Embedding

↓

计算每个token

Semantic Density

↓

删除低密度token

↓

重新计算Query Embedding

↓

Vector Search

↓

Rerank
```

或者进一步：

```
Document

↓

每个token

↓

Semantic Density

↓

Document Compression

↓

Embedding

↓

Index
```

这样索引中保留的是**语义密度最高的表示**，而不是完整文本。这与传统的语义分块（Semantic Chunking）和多向量检索（ColBERT）都有明显区别，因为你的优化对象是**语义信息密度本身**，而不是分块边界、匹配函数或交互方式。

如果把它与 **SRP** 结合，甚至可以形成一种**Semantic Density-aware Retrieval**：查询、索引和上下文压缩都围绕统一的语义密度指标进行，这个方向目前公开文献覆盖得还比较少，值得进一步调研和验证。

[1]: https://ojs.aaai.org/index.php/AAAI/article/view/40566?utm_source=chatgpt.com "Incorporating Token Importance in Multi-Vector Retrieval | Proceedings of the AAAI Conference on Artificial Intelligence"
[2]: https://arxiv.org/abs/2406.00944?utm_source=chatgpt.com "A Theory for Token-Level Harmonization in Retrieval-Augmented Generation"
[3]: https://deepmind.google/research/publications/84309/?utm_source=chatgpt.com "Rethinking the Role of Token Retrieval in Multi-Vector Retrieval — Google DeepMind"
[4]: https://deep-paper.org/en/paper/2312.06648/?utm_source=chatgpt.com "Beyond the Passage: Why 'Propositions' Are the Future of RAG and Dense Retrieval | Deep Paper"
[5]: https://arxiv.org/abs/2412.02563?utm_source=chatgpt.com "Semantic Tokens in Retrieval Augmented Generation"

我认真看了你的 `rag_srp_v2`，也结合最新的 RAG 工作对比了一下。

结论先说：

> **你的代码目前还是一个"Retrieval-guided SRP"，而不是"Semantic Density RAG"。**
>
> 但是，它已经有了一个非常好的切入点，只差一层算法，就能变成一个新的 RAG 方向。

---

# 先看你的流程

你的整个 pipeline 实际是：

```text
Memory
      │
      ▼
chunk_text()
      │
      ▼
Top-k chunk
      │
      ▼
SRP Compress
      │
      ▼
Recover
      │
      ▼
Semantic Validation
      │
      ▼
Commit / Rollback
```

真正参与 Retrieval 的只有：

```python
chunks = chunk_text(text, budget.rag_chunk_tokens)

shortlisted = chunks[: budget.rag_top_k]
```

或者

```python
client.generate_with_usage(
    build_rag_query_prompt(...)
)
```

所以：

RAG 实际仍然只是

> **Chunk Selection**

而不是

> **Semantic-weighted Retrieval**

---

# 你真正可以插入创新的位置

就在这里：

```python
retrieved, retrieval_usage = _retrieve_chunks(...)
```

目前：

```text
Memory

↓

Chunk

↓

Embedding

↓

Top-k
```

你完全可以改成：

```text
Memory

↓

Chunk

↓

Sentence Embedding

↓

Semantic Density

↓

Density Filter

↓

Embedding

↓

Top-k
```

这一步目前公开工作几乎没人做。

---

# 你已经有一个别人没有的东西

SRP 里面其实已经维护了：

```python
SemanticState
```

里面有：

```python
global_vocabulary

local_vocabulary

constraints

loss_notes

policy
```

这意味着：

你其实已经拥有：

> 一个动态维护的语义状态。

别人 RAG：

```text
Document

↓

Embedding

↓

Search
```

你的：

```text
Semantic State

↓

Vocabulary

↓

Constraints

↓

Compression History

↓

Embedding

↓

Search
```

实际上比普通 RAG 多了一层：

> **Semantic Prior**

这一点目前公开工作很少做到。大多数工作还是围绕 token 权重、late interaction 或 reranker 展开。([AAAI Publications][1])

---

# 如果我是你，我会加一个模块

例如：

```python
def semantic_density(chunk):
```

流程：

```
Sentence

↓

Embedding(S)
```

然后：

```
Token_i

↓

Embedding(Token_i)
```

计算：

```
density

=

α·Centrality

+

β·Importance

+

γ·ConstraintMatch

+

δ·VocabularyNovelty
```

其中：

### ① Centrality

```
cos(Token,

Sentence)
```

---

### ② Importance

删除 token：

```
Sentence

↓

remove(token)

↓

Embedding

↓

Cosine Drop
```

---

### ③ Constraint Match

例如：

```
constraints

↓

keyword overlap

+

embedding similarity
```

---

### ④ Vocabulary Novelty

你的：

```
global_vocabulary
```

正好能用。

如果：

```
token

已经出现100次
```

那么：

```
Novelty

↓

很低
```

如果：

```
新的关键概念
```

例如：

```
backpropagation
```

那么：

```
Novelty

↑
```

这就是动态信息增益。

---

# 然后 Retrieval 就变成

不是：

```python
chunks[:top_k]
```

而是：

```
Chunk

↓

Semantic Density

↓

Score

↓

Ranking

↓

Top-k
```

甚至：

```
Chunk Score

=

Embedding Similarity

×

Semantic Density
```

我反而觉得这是一个比较容易发表的小创新。

---

# 更进一步（我觉得真正值得做）

其实你现在维护：

```python
global_vocabulary
```

只是：

```
list
```

为什么不维护：

```
{
token:

density

}
```

例如：

```
engine

0.93

battery

0.81

temperature

0.79

car

0.33
```

那么：

整个 SRP 就变成：

```
Semantic Runtime State

↓

Semantic Density Graph

↓

RAG
```

下一轮：

直接：

```
Top Density Tokens

↓

Generate Query

↓

Retrieve
```

而不是：

```
Whole Memory

↓

LLM

↓

Generate Query
```

---

# 我认为你的论文真正值得做的，不是改 RAG，而是定义一个新的 Retrieval Protocol

目前主流 RAG 的流程几乎都是：

```
Embedding

↓

Similarity

↓

Retrieve
```

而你的 SRP 已经具备了另一种可能：

```
Semantic State

↓

Semantic Density Estimation

↓

Density-aware Query Construction

↓

Density-aware Retrieval

↓

Semantic Validation

↓

State Commit
```

这已经不是"RAG 的一个技巧"了，而是一种**运行时检索协议（Retrieval Protocol）**。

从目前公开论文来看：

* 有 **Token Importance**（给查询 token 加权）。([AAAI Publications][1])
* 有 **Semantic Tokens**（把概念作为检索单位）。([arXiv][2])
* 有 **Proposition Retrieval**（按事实单元检索）。([Deep Paper][3])
* 有 **Dense Retrieval 的词汇空间解释**。([ACL Anthology][4])

**但我没有看到公开工作把"语义密度（Semantic Density）"作为一个统一的运行时信号，同时驱动查询构造、检索排序、上下文压缩和状态提交。** 如果你能设计出一个明确、可计算、可复现的 **Semantic Density Score**，并证明它在检索质量、上下文压缩或长期对话稳定性上带来收益，那么这会比简单地给 token 加权更有研究价值。

[1]: https://ojs.aaai.org/index.php/AAAI/article/view/40566?utm_source=chatgpt.com "Incorporating Token Importance in Multi-Vector Retrieval | Proceedings of the AAAI Conference on Artificial Intelligence"
[2]: https://arxiv.org/abs/2412.02563?utm_source=chatgpt.com "Semantic Tokens in Retrieval Augmented Generation"
[3]: https://deep-paper.org/en/paper/2312.06648/?utm_source=chatgpt.com "Beyond the Passage: Why 'Propositions' Are the Future of RAG and Dense Retrieval | Deep Paper"
[4]: https://aclanthology.org/2023.acl-long.140/?utm_source=chatgpt.com "What Are You Token About? Dense Retrieval as Distributions Over the Vocabulary - ACL Anthology"

我看完你的代码之后，最大的感受是：

> **你现在缺的不是更多的 RAG 技巧，而是一个完整的"Semantic Density"理论和算法体系。**

这个体系其实可以完全建立在已有研究上，而不是从零开始。下面是我建议你补齐的知识栈，我按照**实现优先级**排序。

---

# 第一层：Token Attribution（最重要，必须补）

这是整个 Semantic Density 的基础。

关键词：

* Integrated Gradients (IG)
* Discretized Integrated Gradients (DIG)
* Sequential Integrated Gradients (SIG)
* Feature Attribution

这些工作的目标就是：

> **计算每个 token 对模型输出到底贡献了多少。**

例如：

```
Sentence

↓

Transformer

↓

Prediction

↓

Integrated Gradient

↓

token importance
```

如果以后你论文里面写

```
Importance(token)
```

那么最自然的方法就是：

```
Integrated Gradient
```

因为：

这是 Explainable AI (XAI) 已经认可的方法。

目前还有针对 Transformer 的改进版：

* Context-aware Layer-wise Integrated Gradients
* Sequential Integrated Gradients

都可以直接借鉴。([ScienceDirect][1])

---

# 第二层：Sentence Attribution（非常适合 SRP）

这一块很多人不知道。

你的 SRP 更适合：

不是解释

```
分类
```

而是解释

```
Sentence Embedding
```

目前已经有人研究：

> Attribution for Siamese Encoders

例如：

SentenceTransformer

```
Sentence A

↓

Embedding
```

```
Sentence B

↓

Embedding
```

计算：

```
Cosine Similarity
```

然后反推：

```
哪些 token

贡献了这个 embedding
```

这几乎就是：

你的 Semantic Density 的第一步。

([ResearchGate][2])

---

# 第三层：Information Retrieval Attribution（非常值得看）

目前开始有人研究：

> Information Retrieval 为什么检索到这个文档？

不是：

为什么分类？

而是：

为什么 Retrieval？

例如：

Cross Encoder

↓

Integrated Gradient

↓

Query Token

↓

Document Token

↓

Importance

这类工作会告诉你：

如何定义：

```
Retrieval Importance
```

而不是：

Language Importance。

([Hugging Face][3])

---

# 第四层：Token Importance in Retrieval（直接对应你的 RAG）

这是你目前最应该学习的论文。

AAAI 2026：

> Incorporating Token Importance in Multi-Vector Retrieval

它其实已经定义了：

```
Score

=

Σ

weight_i

×

MaxSim_i
```

但是：

weight 是训练出来的。

而你完全可以换成：

```
Semantic Density
```

于是：

```
Score

=

Σ

Density_i

×

MaxSim_i
```

你的 Retrieval 就升级了。

([AAAI Publications][4])

---

# 第五层：Graph Retrieval（未来可以升级）

你维护：

```python
global_vocabulary
```

其实已经接近：

Graph Node

例如：

```
engine

↓

temperature

↓

sensor
```

形成：

```
Semantic Graph
```

现在最新一些工作已经开始：

利用：

Token Graph

帮助 Retrieval。

例如：

TIGRAG：

```
Token

↓

Graph

↓

Expand Query

↓

Retrieve
```

([Cool Papers][5])

---

# 我建议你的四个模块这样设计

## Module 1：Semantic Centrality（最容易实现）

不用训练。

直接：

```
Sentence Embedding

↓

每个 Token Embedding
```

计算：

```
Centrality

=

cos(token,

sentence)
```

代码可能就是：

```python
density = cosine(
    token_embedding,
    sentence_embedding
)
```

成本非常低。

---

## Module 2：Semantic Importance

推荐：

删除法。

例如：

```
Sentence

↓

Embedding
```

删除：

```
token_i
```

重新：

```
Embedding
```

计算：

```
Importance

=

1-cos(E,E')
```

你的代码可以直接：

```python
for token in sentence:
    remove(token)

    delta = 1-cos(...)
```

不用训练。

虽然慢一点。

但论文实验完全够。

---

## Module 3：Constraint Alignment（你的创新）

这个别人没有。

例如：

SRP：

```python
constraints
```

里面：

```
battery

temperature

warning
```

对于：

token：

```
temperature
```

计算：

```
Constraint Alignment
```

例如：

```
Embedding(token)

↓

Embedding(constraints)
```

得到：

```
Alignment
```

这是：

SRP 独有。

---

## Module 4：Novelty（也是你的优势）

目前：

```python
global_vocabulary
```

只是：

```
list
```

我建议：

变成：

```
{
token

:

frequency,

last_seen,

importance,

density
}
```

例如：

```python
class SemanticToken:

    frequency

    density

    importance

    age
```

以后：

新的：

```
Transformer
```

第一次出现：

```
Novelty=1.0
```

第十次：

```
Novelty=0.2
```

这就是：

Information Gain。

---

# 最后组合成 Semantic Density

我建议：

不要一开始搞特别复杂。

第一版：

```
Density

=

0.35

×

Importance

+

0.35

×

Centrality

+

0.2

×

ConstraintAlignment

+

0.1

×

Novelty
```

以后：

论文再做：

Ablation。

例如：

```
去掉 Novelty

Recall↓

```

```
去掉 Centrality

NDCG↓

```

这样：

论文非常完整。

---

# 我觉得真正值得发表的，不是这个公式，而是整个 Runtime Pipeline

目前 RAG 论文：

```
Query

↓

Embedding

↓

Retrieve
```

而我建议你的 SRP 变成：

```
Semantic State
        │
        ▼
Semantic Density Estimator
        │
        ▼
Density-aware Query Constructor
        │
        ▼
Density-aware Retriever
        │
        ▼
Semantic Validator
        │
        ▼
State Commit / Rollback
```

这里真正的新意不是单个算法，而是**把语义密度作为统一信号，贯穿状态管理、查询构造、检索、压缩和验证**。现有工作分别研究了 token 重要性、检索解释、图检索或语义 token，但公开文献中还很少看到这样一个完整的运行时协议。([AAAI Publications][4])

[1]: https://www.sciencedirect.com/science/article/pii/S0925231226004479?utm_source=chatgpt.com "Explainable AI: Context-aware layer-wise integrated gradients for explaining transformer models - ScienceDirect"
[2]: https://www.researchgate.net/publication/374919169_An_Attribution_Method_for_Siamese_Encoders?utm_source=chatgpt.com "(PDF) An Attribution Method for Siamese Encoders"
[3]: https://huggingface.co/papers/2406.19309?utm_source=chatgpt.com "Paper page - Which Neurons Matter in IR? Applying Integrated Gradients-based Methods to Understand Cross-Encoders"
[4]: https://ojs.aaai.org/index.php/AAAI/article/view/40566?utm_source=chatgpt.com "Incorporating Token Importance in Multi-Vector Retrieval | Proceedings of the AAAI Conference on Artificial Intelligence"
[5]: https://papers.cool/arxiv/2606.30093?utm_source=chatgpt.com "Efficient Retrieval-Augmented Generation via Token Co-occurrence Graphs | Cool Papers - Immersive Paper Discovery"

这是一个非常关键的问题。

如果你想把 **Semantic Density** 做成论文，而不是一个工程技巧，那么**不要先问“怎么实现”**，而应该先问：

> **我要回答哪些尚未被很好回答的科学问题？**

实际上，你的设计可以拆成 **6 个研究问题（Research Questions）**。其中前 4 个已经有比较成熟的方法可以借鉴，后 2 个才是真正可能形成你贡献的地方。

---

# RQ1：什么是一个 token 的"重要性"（Importance）？

这是最成熟的问题。

过去十年，可解释 AI（XAI）基本都在研究：

> 一个 token 对模型输出贡献了多少？

已经比较成熟的方法包括：

* Integrated Gradients (IG)
* Discretized Integrated Gradients (DIG)
* SHAP
* Layer-wise Relevance Propagation
* Attention Rollout

这些方法已经形成了较完整的理论基础和实现，可以直接作为你的 Importance 模块，而不需要重新发明算法。([arXiv][1])

因此：

**这个问题不用创新。**

直接采用成熟方法即可。

---

# RQ2：什么是一个 token 的"语义中心性"（Semantic Centrality）？

这是 NLP 已经研究过，但没有统一答案的问题。

你的想法是：

```text
Sentence Embedding

↓

Token Embedding

↓

Cosine Similarity
```

问题变成：

> token 离 sentence embedding 越近，是不是越重要？

已有工作讨论了：

* Token importance
* Sentence embedding attribution
* Weighted pooling

但是：

没有形成统一标准。

因此：

这一块：

可以直接采用：

```text
Centrality

=

cos(token,sentence)
```

作为定义。

不用证明：

它是真理。

只需要证明：

它有效。

---

# RQ3：Retrieval 为什么找到这个 Chunk？

这是 Information Retrieval 最近几年开始研究的问题。

以前：

IR：

只关心：

```text
Top-k
```

现在：

越来越关心：

```text
Explainability
```

例如：

为什么：

Document A

比

Document B

更相关？

CrossEncoder

里面：

哪些 neuron

起作用？

哪些 token

起作用？

这些解释性工作已经开始出现。([arXiv][2])

所以：

Retrieval Attribution

已经有基础。

---

# RQ4：Chunk 为什么应该保留？

这个问题：

RAG 社区现在正在研究。

例如：

固定：

```text
512 token
```

为什么？

其实没人知道。

所以：

现在越来越多工作开始研究：

* Semantic Chunking
* Proposition Chunking
* Graph Chunking

目的都是：

> 保留真正有意义的信息单位，而不是固定长度。RAG 最新综述也把索引和分块视为核心研究方向之一。([Semantic Scholar][3])

因此：

Chunk Selection

已经有很多工作。

---

真正有意思的是下面两个问题。

---

# RQ5：Importance ≠ Retrieval Value？

我觉得：

这是你真正应该回答的问题。

目前：

大家默认：

```text
重要token

↓

重要检索
```

但是：

真的成立吗？

例如：

Query：

```text
What causes lung cancer?
```

可能：

```text
lung

0.95
```

```text
cancer

0.98
```

但是：

真正 Retrieval

决定因素：

可能：

```text
causes
```

因为：

这是关系。

不是实体。

所以：

我建议：

你的论文可以提出：

> **Importance 和 Retrieval Utility 是两个不同的概念。**

即：

```text
Importance

≠

Retrieval Utility
```

然后：

设计：

```text
Density

=

f(

Importance,

Retrieval Utility

)
```

这个：

目前公开论文讨论得很少。

---

# RQ6：Semantic Density 是不是 Runtime 属性？

这是我觉得最值得做的。

目前：

所有：

Token Importance

几乎都是：

```text
Static
```

例如：

```text
Sentence

↓

Importance
```

结束。

但是：

SRP：

不是。

例如：

Cycle1：

```text
battery

↓

很重要
```

Cycle20：

```text
battery

↓

大家都知道了
```

真正：

重要的是：

```text
temperature
```

于是：

Density：

应该：

变化。

所以：

可以提出：

```text
Density

=

f(

Importance,

Novelty,

Constraint,

History

)
```

这里：

History

就是：

SRP

维护的：

```python
global_vocabulary
```

这其实是：

Runtime

才有的信息。

目前大多数 Token Attribution 都没有这种动态状态。

---

# 我建议你不要把论文写成"提出一个新算法"

我反而建议：

写成：

> **提出一个新的问题。**

例如：

目前：

大家回答：

> Which token is important?

你的论文回答：

> Which token is valuable **for retrieval under a runtime semantic state**?

这是：

两个问题。

---

## 最后，我建议你的设计建立在一个明确的研究假设上

如果我是你的导师，我会要求你先写出下面四个假设，再开始编码：

| 假设                                      | 是否已有成熟方法                                                                                     | 你的工作                     |
| --------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------ |
| H1：Token 可以赋予重要性分数                      | **是**（IG、DIG、SHAP 等）([arXiv][1])                                                             | 直接采用                     |
| H2：Chunk 可以按语义质量排序                      | **是**（语义分块、GraphRAG、Proposition Retrieval 等）([Semantic Scholar][3])                          | 直接采用或适配                  |
| H3：Retrieval Value 不等于 Token Importance | **部分研究涉及，但尚未形成统一理论**                                                                         | **可以作为你的核心研究问题**         |
| H4：Semantic Density 应随运行时状态动态变化，而不是固定不变 | **我没有发现成熟、被广泛接受的运行时语义密度框架**；现有 RAG 综述普遍将检索、索引和融合作为主要优化对象，而不是维护动态语义状态。([Semantic Scholar][4]) | **这是最有潜力形成 SRP 核心贡献的方向** |

从研究价值来看，我会把精力放在 **H3 和 H4**，因为前两者更多是利用已有成果，而后两者才是真正有机会让你的 SRP 与现有 RAG 工作区分开的地方。

[1]: https://arxiv.org/abs/2108.13654?utm_source=chatgpt.com "Discretized Integrated Gradients for Explaining Language Models"
[2]: https://arxiv.org/abs/2406.19309?utm_source=chatgpt.com "Which Neurons Matter in IR? Applying Integrated Gradients-based Methods to Understand Cross-Encoders"
[3]: https://www.semanticscholar.org/paper/A-Survey-on-RAG-Meeting-LLMs%3A-Towards-Large-Models-Fan-Ding/eb9c4a07a336e8deefe7b399c550d3af0241238e?utm_source=chatgpt.com "[PDF] A Survey on RAG Meeting LLMs: Towards Retrieval-Augmented Large Language Models | Semantic Scholar"
[4]: https://www.semanticscholar.org/paper/A-Comprehensive-Survey-of-Retrieval-Augmented-and-Gupta-Ranjan/88dc871460a3a03699dc0a8ca248542a5d39f41e?utm_source=chatgpt.com "[PDF] A Comprehensive Survey of Retrieval-Augmented Generation (RAG): Evolution, Current Landscape and Future Directions | Semantic Scholar"

我建议**不要只做 3 个 baseline**。

如果你的目标是让 SRP 成为一篇有说服力的系统论文，那么实验应该回答的是：

> **SRP 到底比什么更好？好在哪里？代价是什么？**

而不是：

> **SRP 比一个普通 RAG 好。**

现在长上下文和记忆系统论文的评测，已经越来越倾向于同时比较 **Long Context、Summary、RAG、Memory、Hybrid** 等不同路线。([Hugging Face][1])

---

# 我建议的实验矩阵

我会设计 **7 个系统**。

| System                    | 最新上下文 | Summary | RAG         | Runtime State | Validation | 目的              |
| ------------------------- | ----- | ------- | ----------- | ------------- | ---------- | --------------- |
| S0 Full Context           | ✓     | ×       | ×           | ×             | ×          | Long Context 基线 |
| S1 Sliding Window         | ✓     | ×       | ×           | ×             | ×          | 最近上下文           |
| S2 Summary Memory         | ×     | ✓       | ×           | ×             | ×          | 摘要记忆            |
| S3 Vanilla RAG            | ×     | ×       | ✓           | ×             | ×          | 检索记忆            |
| S4 Summary + RAG          | ×     | ✓       | ✓           | ×             | ×          | MemoRAG 类方法     |
| S5 SRP v2（你现在）            | ×     | ✓       | ✓           | ✓             | ✓          | 当前方法            |
| S6 SRP + Semantic Density | ×     | ✓       | Density RAG | ✓             | ✓          | 你的最终方法          |

这样几乎覆盖了目前主流路线。MemoRAG、Long Context 与 RAG 的比较已经是近期论文常见设置。([papers.lunadong.com][2])

---

# 每个 Baseline 回答不同的问题

## S0：Full Context

回答：

> 如果无限 token，会怎样？

这是理论上限。

---

## S1：Sliding Window

回答：

> 如果模型只保留最近上下文，会发生什么？

它代表：

ChatGPT

Claude

Gemini

默认都会有这种情况。

---

## S2：Summary

回答：

> 单纯摘要够不够？

例如：

```text
History

↓

LLM Summary

↓

Question
```

这是很多 Memory Agent 都会做的。([arXiv][3])

---

## S3：Vanilla RAG

回答：

> 检索是否足够？

例如：

```text
History

↓

Embedding

↓

Top-k

↓

Answer
```

---

## S4：Summary + RAG

回答：

> Global Summary + Local Retrieval

是不是更好？

MemoRAG、MiA-RAG 等就是这一类思想。([papers.lunadong.com][2])

---

## S5：SRP

回答：

> Runtime State 有没有意义？

这是你的第一篇论文。

---

## S6：Semantic Density SRP

回答：

> Density 是否真正提高 Retrieval？

这是你的第二篇论文。

---

# 但我觉得还缺一个非常重要的实验

也是目前很多论文没有认真做的。

## Ablation

不是：

系统之间比较。

而是：

去掉一个模块。

例如：

```text
SRP

↓

没有 Validation
```

看看：

Drift

增加多少。

---

然后：

```text
SRP

↓

没有 Vocabulary
```

再测。

---

再：

```text
SRP

↓

没有 Density
```

再测。

例如：

| Variant      | Accuracy | Drift | Retrieval Recall |
| ------------ | -------- | ----- | ---------------- |
| SRP          | 91       | 0.08  | 89               |
| - Validation | 78       | 0.31  | 88               |
| - Vocabulary | 84       | 0.19  | 86               |
| - Density    | 86       | 0.14  | 82               |

这样：

每一个模块：

都有贡献。

---

# Density 应该回答什么？

我建议：

不要直接问：

> Accuracy 有没有提高？

因为：

可能：

提高：

只有：

1%。

但是：

Density

真正应该回答：

> Retrieval 有没有变化？

例如：

增加：

新的指标。

---

## Density Recall

真正需要的 Chunk：

有没有被找到？

例如：

Ground Truth：

```text
Chunk3
Chunk8
Chunk19
```

Density：

检索：

```text
Chunk3

Chunk19

Chunk22
```

Recall：

2/3

---

## Density Precision

Top-k

里面：

真正有用的：

多少？

---

## Average Density

每个：

Chunk

平均：

Density

是多少？

例如：

Vanilla：

```text
0.43
```

SRP：

```text
0.71
```

说明：

Context

质量更高。

---

## Token Efficiency

这是我最推荐的。

例如：

1000 token

里面：

真正：

Information

是多少？

例如：

```text
Information Density

=

Useful Token

/

Input Token
```

这个：

Long²RAG 提出的 **Key Point Recall（KPR）** 指标，其实就是在衡量模型是否真正利用了检索到的关键信息，你可以借鉴它的思想，而不一定照搬它的实现。([arXiv][4])

---

# 我认为你的实验真正应该回答五个问题

如果我是审稿人，我最希望看到的是下面这种结构：

| RQ                                       | 实验       |
| ---------------------------------------- | -------- |
| **RQ1**：Runtime State 是否优于 Summary？      | S2 vs S5 |
| **RQ2**：Runtime State 是否优于 RAG？          | S3 vs S5 |
| **RQ3**：Summary+RAG 是否足够？                | S4 vs S5 |
| **RQ4**：Semantic Density 是否改善 Retrieval？ | S5 vs S6 |
| **RQ5**：SRP 每个模块是否都有贡献？                  | Ablation |

---

## 我还建议增加一个几乎所有记忆论文都会做、但很多本科项目忽略的实验

把**检索质量**和**最终回答质量**分开评估。

很多论文已经指出，如果只看最终 QA 分数，很难知道提升来自**检索器**还是**LLM 本身**；因此应分别报告检索指标（Recall@k、MRR、NDCG 等）和生成指标（Accuracy、F1、Task Success 等）。([Reddit][5])

对于你的 SRP，这一点尤其重要，因为你既修改了**记忆表示**，又修改了**运行时协议**。如果能证明：

* **Semantic Density** 提高了检索 Recall/NDCG；
* **SRP Validation** 降低了 Semantic Drift；
* **最终任务成功率**也随之提升；

那么你的实验链条就会非常完整，也更容易说服审稿人相信每个模块都在发挥独立作用，而不是依赖某一个大模型“兜底”。

[1]: https://huggingface.co/papers/2501.01880?utm_source=chatgpt.com "Paper page - Long Context vs. RAG for LLMs: An Evaluation and Revisits"
[2]: https://papers.lunadong.com/paper/8688?utm_source=chatgpt.com "MemoRAG: Boosting Long Context Processing with Global Memory-Enhanced Retrieval Augmentation - Paper Summary"
[3]: https://arxiv.org/abs/2602.18493?utm_source=chatgpt.com "Learning to Remember: End-to-End Training of Memory Agents for Long-Context Reasoning"
[4]: https://arxiv.org/abs/2410.23000?utm_source=chatgpt.com "Long$^2$RAG: Evaluating Long-Context & Long-Form Retrieval-Augmented Generation with Key Point Recall"
[5]: https://www.reddit.com/r/Rag/comments/1shfhx1/how_should_memoryrag_benchmarks_separate/?utm_source=chatgpt.com "How should memory/RAG benchmarks separate retrieval quality from LLM's reasoning ability?"

这个问题实际上决定了你的论文可信度。

**如果我是 ACL / EMNLP / NAACL 审稿人，我不会要求你做几十万个实验，但我会要求你的实验具有统计意义、跨模型泛化，并覆盖不同任务。**

结合近两年的长上下文、Memory Agent 和 RAG Benchmark（如 LongBench、MemBench、MemoryAgentBench）的实验设计，我建议你的规模如下，而不是盲目追求越大越好。([Memory Papers][1])

---

# 第一层：验证 SRP 是否有效（论文主体）

这是最重要的一层。

目标：

> SRP 是否比现有 Memory 方法更稳定？

建议：

| 项目              |        数量 |
| --------------- | --------: |
| 模型              |   **3 个** |
| 问题集             | **4~6 个** |
| 重复次数            |   **5 次** |
| 每个 session 对话轮数 | **40~80** |

模型建议：

* 小模型（例如 7B~8B）
* 中模型（例如 14B~32B）
* 闭源模型（GPT 或 Claude 其中一个）

这样可以回答：

> SRP 是否具有模型无关性？

如果：

只测 GPT

审稿人一定会问：

> 换模型还能成立吗？

---

# 第二层：Density 是否有效

这一层其实不用那么大。

因为：

只回答：

> Density 有没有改善 Retrieval？

建议：

| 项目  |        数量 |
| --- | --------: |
| 模型  |   **2 个** |
| 问题集 | **3~4 个** |
| 重复  |   **5 次** |
| 每轮  | **40 左右** |

比较：

```text
Vanilla RAG

↓

SRP-RAG

↓

Density RAG
```

这里只测：

Recall

Precision

MRR

NDCG

不用测：

Task Success。

---

# 第三层：Ablation

最重要。

建议：

| 模块         | 是否删除 |
| ---------- | ---- |
| Validation | ✓    |
| Vocabulary | ✓    |
| Density    | ✓    |
| Recover    | ✓    |
| Constraint | ✓    |

不用：

很多数据集。

只需要：

2 个。

因为：

Ablation：

不是验证：

泛化。

而是：

模块贡献。

---

# 第四层：Stress Test

这是很多论文没有做。

建议：

Conversation：

越来越长。

例如：

```text
20轮

↓

40轮

↓

80轮

↓

120轮

↓

160轮
```

画：

```text
Accuracy

^

|

|

|

+---------------->

Turn
```

这样：

可以证明：

什么时候：

Memory

开始崩。

LongBench、MemBench 这类工作都强调随着上下文增长观察性能退化，而不是只报告一个固定长度结果。([Memory Papers][1])

---

# 第五层：Generalization

建议：

不要：

一个问题集。

至少：

四类。

例如：

| 类型              | 推荐                                 |
| --------------- | ---------------------------------- |
| QA              | LongBench QA                       |
| Multi-hop       | Hotpot 风格                          |
| Task Planning   | Agent Task                         |
| Dialogue Memory | LongBench v2 / MemoryAgentBench 风格 |

这样：

可以回答：

SRP

是不是：

Task-specific？

---

# 每个实验重复几次？

我建议：

**5 次。**

原因：

LLM：

随机性：

非常大。

一般：

3 次：

有点少。

10 次：

成本太高。

5 次：

论文里面：

最常见。

报告：

```text
Mean

±

Std
```

然后：

统计检验。

例如：

paired t-test

或者：

Wilcoxon。

---

# 一共多少实验？

假设：

## 3 模型

例如：

```text
Llama

Qwen

GPT
```

---

## 5 Baselines

```text
Sliding

Summary

RAG

SRP

Density SRP
```

---

## 5 数据集

---

## 5 Repeat

那么：

```
3

×

5

×

5

×

5

=

375
```

组实验。

每组：

50轮。

那么：

```
375

×

50

=

18750

turn
```

实际上：

并不算夸张。

很多 Memory Benchmark 都远高于这个规模。([Memory Papers][1])

---

# 我建议你最终控制在这个规模

如果你的目标是**本科毕业论文 + 第一篇可投稿论文**，我不会建议追求几万轮以上的大规模实验，而是追求**实验覆盖面和统计可信度**。

| 实验          |    模型 | Baseline |   数据集 | Repeat |             对话轮数 |
| ----------- | ----: | -------: | ----: | -----: | ---------------: |
| 主实验         | **3** |    **5** | **5** |  **5** |           **50** |
| Ablation    | **2** |    **6** | **2** |  **5** |           **50** |
| Stress Test | **2** |    **3** | **2** |  **3** | **20、40、80、160** |
| Density 实验  | **2** |    **3** | **3** |  **5** |           **50** |

这个规模大约会产生 **500–700 个独立实验单元**（不同模型 × 方法 × 数据集 × 重复），能够支持均值、标准差和显著性检验，同时计算成本仍然在个人研究者可承受的范围内。

**如果时间和预算有限，我宁愿删掉一个模型，也不会删掉重复次数或数据集种类。** 对于记忆系统论文来说，**跨任务和结果稳定性**通常比“多测一个模型”更能说服审稿人。

[1]: https://memorypapers.org/papers/membench-acl2025?utm_source=chatgpt.com "MemBench: Towards More Comprehensive Evaluation on the Memory of LLM-based Agents — AI Memory Research | Memory Papers"