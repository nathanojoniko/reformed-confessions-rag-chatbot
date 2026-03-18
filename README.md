# ✝️ Reformed Confessions RAG Chatbot

A retrieval-augmented generation (RAG) chatbot built on AWS that answers 
theological questions exclusively from the **Westminster Confession of Faith (WCF)** 
and the **London Baptist Confession of 1689 (LBC)** — with cited sources.

---

## What It Does

Ask any theological question and the chatbot will:

- Answer **only** from the WCF and LBC 1689 — no outside sources
- Cite the **specific chapter and section** for every claim
- Clearly distinguish between **explicit confession teaching** and **informed inference**
- When making inferences, ground them in **orthodox, conservative, Reformed 
  and Protestant scholarship** — unashamedly Biblical
- Include a **disclaimer** on every response distinguishing direct confession 
  teaching from AI-generated inference

---

## Why I Built This

As someone passionate about Reformed theology and learning AWS, I wanted a 
project that was both technically meaningful and personally useful. The historic 
Reformed confessions are rich, authoritative documents — but searching through 
them manually is time consuming.

This chatbot makes them instantly searchable by meaning, not just keywords, 
using the power of vector embeddings and retrieval-augmented generation.

---

## Architecture
```
User (Browser)
      ↓
Streamlit UI (Streamlit Community Cloud)
      ↓
Amazon Bedrock — retrieve_and_generate API
      ↓
Bedrock Knowledge Base
      ↙                    ↘
S3 Bucket               S3 Vectors
(confession documents)  (vector embeddings)
      ↓
Amazon Titan Text Embeddings V2
      ↓
Amazon Nova Micro (answer generation)
```

---

## AWS Services Used

| Service | Purpose |
|---|---|
| Amazon Bedrock | RAG orchestration and answer generation |
| Bedrock Knowledge Base | Document ingestion, chunking and retrieval |
| Amazon Titan Text Embeddings V2 | Converts confession text to vectors |
| Amazon Nova Micro | Generates grounded answers (cheapest model) |
| Amazon S3 | Stores source confession documents |
| Amazon S3 Vectors | Stores vector embeddings (90% cheaper than OpenSearch) |
| AWS Lambda | Serverless API backend |
| Amazon API Gateway | HTTPS endpoint |
| Amazon Cognito | Invite-only user authentication |
| AWS CloudFormation | Infrastructure as code — entire stack in one file |
| AWS IAM | Least privilege roles — no hardcoded credentials |

---

## Cost Design

One of the deliberate goals of this project was to build a production-grade 
RAG pipeline at near-zero cost:

| Component | Cost |
|---|---|
| S3 document storage | ~$0.00/month |
| S3 Vectors (vector store) | ~$0.001/month |
| Titan Embeddings (one-time ingestion) | ~$0.001 total |
| Nova Micro inference | ~$0.0001 per question |
| Lambda + API Gateway | Free tier |
| **Total running cost** | **Under $1/month** |

Key cost decision: **S3 Vectors over OpenSearch Serverless** saves ~$175/month 
minimum. OpenSearch Serverless has a floor cost regardless of usage — 
S3 Vectors is pure pay-per-use.

---

## Data Sources

| Document | Chapters | Words |
|---|---|---|
| Westminster Confession of Faith (1647) | 33 | ~31,000 |
| London Baptist Confession of 1689 | 32 | ~13,000 |

Both documents are in the public domain. The confession text is 
100% intact — no content was removed or altered.

---

## RAG Pipeline

1. **Ingestion** — Confession documents uploaded to S3
2. **Chunking** — Documents split into 200-token chunks with 10% overlap
3. **Embedding** — Each chunk converted to 1024-dimension vectors via Titan Embeddings V2
4. **Storage** — Vectors stored in S3 Vectors index
5. **Retrieval** — User question converted to vector, 5 most similar chunks retrieved
6. **Generation** — Nova Micro reads retrieved chunks and generates cited answer
7. **Response** — Answer returned with confession citations and disclaimer

---

## Project Structure
```
reformed-confessions-rag-chatbot/
├── README.md                        ← This file
├── requirements.txt                 ← Python dependencies
├── .gitignore                       ← Credential protection
├── data/
│   ├── london_baptist_1689.json     ← Source confession documents
│   └── westminster_confession_of_faith.json
├── src/
│   ├── chatbot.py                   ← Core RAG logic and system prompt
│   ├── app.py                       ← Streamlit chat UI
│   └── lambda_handler.py            ← AWS Lambda entry point
└── infrastructure/
    ├── cloudformation.yaml          ← Complete AWS infrastructure as code
    └── create_knowledge_base.sh     ← Knowledge Base setup script
```

---

## System Prompt Design

The chatbot is instructed to follow a strict three-part response structure:

1. **Explicit Teaching** — What the confessions directly say, with citations
2. **Not Explicitly Addressed** — Honest acknowledgment when topic is absent
3. **Informed Inference** — Reasoned conclusions from related confession 
   teaching, grounded in orthodox Reformed and Protestant scholarship

Inferences are never presented as confession teaching. Every response 
ends with a disclaimer distinguishing direct citations from AI inference.

---

## Key Technical Decisions

**Why S3 Vectors over OpenSearch Serverless?**
OpenSearch Serverless costs ~$175/month minimum regardless of usage. 
S3 Vectors is pay-per-use — for this project it costs less than a penny 
per month.

**Why Amazon Nova Micro over Claude Haiku?**
Nova Micro is 7x cheaper than Claude Haiku and requires no third-party 
approval process. For structured document retrieval where the model 
is summarizing retrieved content, it performs excellently.

**Why plain text over JSON for ingestion?**
S3 Vectors has a 2048-byte metadata limit per chunk. The confession JSON 
files included large metadata sections that exceeded this limit. 
Converting to plain text resolved the issue while preserving 100% of 
the confession content.

---

## What I Learned

- Designing and deploying a complete RAG pipeline on AWS from scratch
- Infrastructure as code with CloudFormation — entire stack in one YAML file
- AWS IAM least privilege design — no hardcoded credentials anywhere
- Cost optimization on AWS Bedrock — S3 Vectors vs OpenSearch Serverless
- Prompt engineering for theological research — structured outputs, 
  citation requirements, inference disclaimers
- The difference between S3 Vectors and regular S3 buckets
- Debugging CloudFormation validation errors systematically
- Using AWS CloudShell as an authenticated CLI environment

---

## Setup

### Prerequisites
- AWS account with Bedrock model access enabled for:
  - Amazon Titan Text Embeddings V2
  - Amazon Nova Micro
- Python 3.10+
- AWS CLI configured

### Deploy Infrastructure
```bash
aws cloudformation deploy \
  --template-file infrastructure/cloudformation.yaml \
  --stack-name reformed-confessions-rag \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Create Knowledge Base
```bash
chmod +x infrastructure/create_knowledge_base.sh
./infrastructure/create_knowledge_base.sh
```

### Run Locally
```bash
pip install -r requirements.txt
streamlit run src/app.py
```

---

## Built With

- [Amazon Bedrock](https://aws.amazon.com/bedrock/)
- [Amazon S3 Vectors](https://aws.amazon.com/s3/features/vectors/)
- [Streamlit](https://streamlit.io)
- [Claude](https://claude.ai) by Anthropic — AI pair programming assistant

---

## Author

Built by a software developer learning AWS generative AI services, 
passionate about Reformed theology.

---

## License

MIT License — see LICENSE file for details.