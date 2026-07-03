| Backend | Model | Cycles | Raw Prompt Drift | Raw Prompt Success | Summarization Drift | Summarization Success | Rag Drift | Rag Success | Srp Drift | Srp Success | Rag Srp Drift | Rag Srp Success | Rag Srp Anchor Drift | Rag Srp Anchor Success |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| local | Qwen/Qwen3-4B-AWQ | 1 | 0.737 | 1.000 | 0.735 | 0.917 | 0.726 | 0.917 | 0.813 | 0.750 | - | - | - | - |
| local | Qwen/Qwen3-4B-AWQ | 3 | 0.341 | 0.917 | 0.526 | 0.583 | 0.122 | 0.917 | 0.806 | 0.722 | - | - | - | - |
| local | Qwen/Qwen3-4B-AWQ | 5 | 0.354 | 0.917 | 0.559 | 0.583 | 0.122 | 0.917 | 0.417 | 0.950 | 0.698 | 1.000 | 0.561 | 1.000 |
| local | Qwen/Qwen3-4B-AWQ | 7 | 0.360 | 0.929 | 0.572 | 0.583 | 0.160 | 0.917 | 0.408 | 0.917 | - | - | - | - |
| mock | Qwen/Qwen3-4B-AWQ | 1 | - | - | - | - | - | - | - | - | 0.846 | 0.167 | - | - |
| mock | Qwen/Qwen3-4B-AWQ | 3 | 0.480 | 0.917 | 0.840 | 0.078 | 0.747 | 0.400 | 0.846 | 0.167 | - | - | - | - |
| mock | gpt-4o-mini | 1 | 0.480 | 0.917 | 0.673 | 0.233 | 0.747 | 0.400 | 0.933 | 0.067 | - | - | - | - |
| mock | gpt-4o-mini | 3 | 0.480 | 0.917 | 0.840 | 0.078 | 0.747 | 0.400 | 0.846 | 0.167 | - | - | - | - |
| mock | gpt-4o-mini | 5 | 0.480 | 0.917 | 0.873 | 0.047 | 0.747 | 0.400 | 0.846 | 0.167 | - | - | - | - |
| mock | gpt-4o-mini | 7 | 0.480 | 0.917 | 0.887 | 0.033 | 0.747 | 0.400 | 0.846 | 0.167 | - | - | - | - |
| mock | gpt-4o-mini | 9 | - | - | 0.895 | 0.026 | - | - | 0.846 | 0.167 | - | - | - | - |
