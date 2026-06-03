# SEAL: A Novel Methodology for Evaluating the Security of Agentic LLMs

## Abstract

The adoption of large language models (LLMs) as agentic systems introduces security risks that extend beyond traditional prompt-based interactions. This paper presents a novel framework intended to generate datasets for benchmarking the security of LLMs with tool-calling capabilities. Our methodology, termed **SEAL**, integrates automated red teaming through PyRIT for adversarial prompt generation and Promptfoo for structured evaluation under controlled inference-time settings, without requiring training-time modifications or external guardrails. 

The evaluation covers three adversarial strategies intended to measure confidentiality, integrity, and availability: direct tool injection, system prompt exfiltration, and indirect prompt injection with semantic denial-of-service (SDoS) effects. We further assess a semantic defense-in-depth strategy based on progressively hardened system prompts. Through extensive experimentation we demonstrate the validity and usefulness of **SEAL** for automated evaluation of the security level of agentic LLMs. The results obtained for the evaluated models, including both open-source and commercial systems, indicate that commercially aligned models and larger open-source architectures exhibit greater security stability across most assessed dimensions. However, a critical trade-off emerges between robustness and operational availability.

---

## Authors

**I. Gosálvez-White, P. García-Teodoro, R. Magán-Carrion**  
Network Engineering & Security Group  
School of Computer Science and Telecommunication Engineering — CITIC  
University of Granada, Granada (Spain)  
irenegwh@ugr.es · pgteodor@ugr.es · rmagan@ugr.es

---

## Funding

This work is a result of the project VIGILANT (Ref PID2024-161902OB-I00), funded by the Spanish Ministry of Science, Innovation and Universities.

---

## Repository Structure


```
SEAL/
├── README.md
├── requirements.txt                   # Python dependencies
├── graphs_general.py                  # Combined figure generation for all strategies
├── Models_Conf/                       # Ollama model configuration snapshots
├── Strategy1/                         # S1: Direct Tool Injection (Integrity)
│   ├── Phase1_2_Configuration_and_Expansion/
│   │   ├── 2025_tfm_tool_injection_strategy1.yaml  # Adversarial seed prompts
│   │   ├── setup_execute_benchmark.py              # PyRIT expansion pipeline
│   │   ├── ollama_initializer.py                   # PyRIT target/scorer initializer
│   │   ├── ollama_tool_target.py                   # Custom Ollama PyRIT target
│   │   └── pyrit_results_strategy1.jsonl           # Raw PyRIT expansion output
│   │   └── .env                                    # Local runtime config (excluded from git — see .env.example)
│   ├── Phase3_Normalization/
│   │   ├── parser_pyrit_to_promptfoo.py            # JSONL → Promptfoo JSON
│   │   ├── convert_prompts.js                      # Schema transformation
│   │   └── prompts_temp.json                       # Intermediate normalized output
│   └── Phase4_Evaluation/
│       ├── promptfoo.yaml                          # Evaluation config (local models)
│       ├── promptfoo_commercial.yaml               # Evaluation config (commercial models)
│       ├── prompts_final_fixed.json                # Normalized adversarial dataset (final output from Phase3)
│       ├── parser_promptfoo_csv.py                 # Promptfoo JSON → CSV aggregation
│       ├── eval-S1-locals.json                     # Raw evaluation output (local models)
│       ├── eval-S1-commercial.json                 # Raw evaluation output (commercial models)
│       └── results/                                # Aggregated CSV results
├── Strategy2/                         # S2: System Prompt Exfiltration (Confidentiality)
│   └── ...                            # Same structure as Strategy1
├── Strategy3/                         # S3: Indirect Tool Injection & SDoS (Availability)
│   └── ...                            # Same structure as Strategy1
└── results/
    └── combined/
        └── graphs/                    # Final combined figures for all strategies
```

--- 

## Installation

### Python Environment

```bash
pip install -r requirements.txt
```

### Promptfoo

```bash
npm install -g promptfoo@0.120.7
```

### Ollama

Install and configure Ollama following the official documentation at [https://ollama.com/](https://ollama.com/). Pull the models you intend to evaluate and ensure the inference server is running and accessible before executing the pipeline.

---

## Environment Configuration

### PyRIT `.env`

Create a `.env` file in each `Phase1_2_Configuration_and_Expansion/` directory:

```dotenv
# Ollama inference server
OLLAMA_SERVER_URL=http://localhost:11434

# Target model (uncomment one)
#OLLAMA_ATTACK_MODEL=llama3.2:latest
#OLLAMA_ATTACK_MODEL=gpt-oss:20b
#OLLAMA_ATTACK_MODEL=qwen2.5-coder:latest
OLLAMA_ATTACK_MODEL=mistral:latest

# Scorer model (legacy)
OLLAMA_SCORER_MODEL=mistral:latest

# System prompt hardening level (uncomment one)
PROMPT="You are the target model..."    # Level I (Inductor)
#PROMPT="Role: Security-hardened..."    # Level S (Strict)
#PROMPT="YOU ARE A SECURITY-CRITICAL..." # Level U (Ultra)
```

### Promptfoo API Keys

For commercial model evaluation (`promptfoo_commercial.yaml`), set the following environment variables:

```bash
export ANTHROPIC_API_KEY=your_anthropic_api_key
export OPENROUTER_API_KEY=your_openrouter_api_key
```

> These keys are required only for Phase 4 commercial model evaluation. Local model evaluation with Ollama does not require any API keys.
---

## Execution

The pipeline runs independently for each strategy (S1, S2, S3). The following example uses Strategy 1.

### Phase 1 & 2 — Adversarial Expansion (PyRIT)

```bash
cd Strategy1/Phase1_2_Configuration_and_Expansion
python setup_execute_benchmark.py > pyrit_results_strategy1.jsonl
```

### Phase 3 — Normalization

```bash
cd Strategy1/Phase3_Normalization

# Parse PyRIT JSONL output into intermediate format
python parser_pyrit_to_promptfoo.py ../Phase1_2_Configuration_and_Expansion/pyrit_results_strategy1.jsonl prompts_temp.json

# Convert to final Promptfoo-compatible schema
node convert_prompts.js prompts_temp.json
```

Output: `prompts_final_fixed.json` — copy or move to `Phase4_Evaluation/` before proceeding.

### Phase 4 — Evaluation (Promptfoo)

```bash
cd Strategy1/Phase4_Evaluation

# Run evaluation (local models)
promptfoo eval -c promptfoo.yaml --no-cache --max-concurrency 1

# Run evaluation (commercial models)
promptfoo eval -c promptfoo_commercial.yaml --no-cache --max-concurrency 2

# (Optional) Visualize results in browser at http://localhost:15500
promptfoo view
```

Export results: open the Promptfoo dashboard, navigate to **Eval Actions → Download Results JSON**, and save the file as `eval-S1-locals.json` or `eval-S1-commercial.json` in the `Phase4_Evaluation/` directory.

Then aggregate results into CSV:

```bash
python parser_promptfoo_csv.py eval-S1-locals.json S1-locals results
python parser_promptfoo_csv.py eval-S1-commercial.json S1-commercial results
```

### Generate Combined Figures

Once all strategies have been evaluated and CSVs generated:

```bash
python graphs_general.py ALL
```

Output saved to `results/combined/graphs/`.
