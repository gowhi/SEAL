# SEAL: Security Evaluation of Agentic LLMs

## Abstract

The adoption of large language models (LLMs) as agentic systems introduces security risks that extend beyond traditional prompt-based interactions. This repository contains the dataset, evaluation artifacts, and source code associated with the paper **SEAL: A Novel Experimental Methodology for Evaluating the Security of Agentic LLMs**.

SEAL integrates automated red teaming through PyRIT for adversarial prompt generation and Promptfoo for structured evaluation under controlled inference-time settings, without requiring training-time modifications or external guardrails. The evaluation covers three adversarial strategies intended to measure confidentiality, integrity, and availability: direct tool injection, system prompt exfiltration, and indirect prompt injection with semantic denial-of-service (SDoS) effects.

---

## Authors

**I. Gosálvez-White, P. García-Teodoro, R. Magán-Carrion**  
Network Engineering & Security Group  
School of Computer Science and Telecommunication Engineering — CITIC  
University of Granada, Granada (Spain)  
irenegwh@ugr.es · pgteodor@ugr.es · rmagan@ugr.es

---

## Funding

This work is a result of the project VIGILANT (Ref. PID2024-161902OB-I00), funded by the Spanish Ministry of Science, Innovation and Universities.

---

## Repository Structure

--- 

## Installation

### Requirements

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com/) (for local model inference)
- Promptfoo (`npm install -g promptfoo`)

### Python dependencies

```bash
pip install -r requirements.txt
```

---

## Execution

The pipeline is organized in four phases, executed independently for each strategy (S1, S2, S3).

### Phase 1 & 2 — Seed Configuration and Adversarial Expansion

```bash
cd Strategy1/Phase1_2_Configuration_and_Expansion
python setup_execute_benchmark.py > pyrit_results_strategy1.jsonl
```

Requires a `.env` file with:

.... INCLUIR ARCHIVO

### Phase 3 — Normalization

```bash
cd Strategy1/Phase3_Normalization
python parser_pyrit_to_promptfoo.py ../Phase1_2_Configuration_and_Expansion/pyrit_results_strategy1.jsonl prompts_temp.json
node convert_prompts.js prompts_temp.json
```

### Phase 4 — Evaluation

```bash
cd Strategy1/Phase4_Evaluation
promptfoo eval --config promptfoo.yaml --output eval-S1-locals.json
python parser_promptfoo_csv.py eval-S1-locals.json S1-locals results
```

### Generate Figures

```bash
python graphs_general.py ALL
```

Output saved to `results/combined/graphs/`.