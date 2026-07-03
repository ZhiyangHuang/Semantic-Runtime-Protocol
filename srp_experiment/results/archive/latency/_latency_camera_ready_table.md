| Backend | Model | Cycles | Strongest Baseline | Baseline Drift | Baseline Success | Baseline Tokens | Baseline Latency (s) | SRP Drift | SRP Success | SRP Tokens | SRP Latency (s) | Delta Drift | Delta Success | Delta Tokens | Delta Latency (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| local | Qwen/Qwen3-4B-AWQ | 1 | Raw Prompt | 0.737 | 1.000 | 139.33 | - | 0.813 | 0.750 | 108.00 | - | 0.076 | -0.250 | -31.33 | - |
| local | Qwen/Qwen3-4B-AWQ | 3 | Rag | 0.122 | 0.917 | 33.67 | - | 0.806 | 0.722 | 24.78 | - | 0.684 | -0.195 | -8.89 | - |
| local | Qwen/Qwen3-4B-AWQ | 5 | Rag Srp Anchor | 0.561 | 1.000 | 27.87 | - | 0.417 | 0.950 | 27.33 | - | -0.144 | -0.050 | -0.54 | - |
| local | Qwen/Qwen3-4B-AWQ | 7 | Raw Prompt | 0.360 | 0.929 | 181.10 | - | 0.408 | 0.917 | 29.00 | - | 0.048 | -0.012 | -152.10 | - |
| mock | Qwen/Qwen3-4B-AWQ | 1 | Rag Srp | 0.846 | 0.167 | 36.00 | - | - | - | - | - | - | - | - | - |
| mock | Qwen/Qwen3-4B-AWQ | 3 | Raw Prompt | 0.480 | 0.917 | 108.11 | 0.0000 | 0.846 | 0.167 | 34.33 | 0.0000 | 0.367 | -0.750 | -73.78 | 0.0000 |
| mock | gpt-4o-mini | 1 | Raw Prompt | 0.480 | 0.917 | 47.67 | - | 0.933 | 0.067 | 34.33 | - | 0.453 | -0.850 | -13.34 | - |
| mock | gpt-4o-mini | 3 | Raw Prompt | 0.480 | 0.917 | 108.11 | - | 0.846 | 0.167 | 34.33 | - | 0.367 | -0.750 | -73.78 | - |
| mock | gpt-4o-mini | 5 | Raw Prompt | 0.480 | 0.917 | 168.33 | - | 0.846 | 0.167 | 34.33 | - | 0.367 | -0.750 | -134.00 | - |
| mock | gpt-4o-mini | 7 | Raw Prompt | 0.480 | 0.917 | 196.81 | - | 0.846 | 0.167 | 34.33 | - | 0.367 | -0.750 | -162.48 | - |
| mock | gpt-4o-mini | 9 | Summarization | 0.895 | 0.026 | 22.22 | - | 0.846 | 0.167 | 34.33 | - | -0.049 | 0.141 | 12.11 | - |
