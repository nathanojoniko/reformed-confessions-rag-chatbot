# Reformed Confessions RAG Chatbot — Project Specification

## Overview

A retrieval-augmented generation (RAG) chatbot built entirely on AWS that answers
theological questions exclusively from the Westminster Confession of Faith (WCF) and
the London Baptist Confession of 1689 (LBC). The chatbot cites specific chapters and
sections from these confessions in every response and refuses to draw on any outside
knowledge.

---

## Problem Statement

Students of Reformed theology often want to know what the historic confessions teach
on a given subject. Searching manually through multiple documents is time-consuming.
This chatbot allows a user to ask a plain-English question and receive a cited,
confession-grounded answer in seconds.

---

## Goals

- Answer questions grounded **only** in the WCF and LBC 1689
- Cite **specific chapter and section** for every claim made
- Refuse to speculate or draw on outside sources
- Run at **near-zero cost** (~$0.001 per query)
- Be **fully reproducible** from this repository — no manual console clicking required
- Be **securely accessible** to a small group of invited users

---

## Non-Goals

- The chatbot will NOT use any sources outside the two confessions
- The chatbot will NOT store or remember conversation history across sessions
- The chatbot will NOT be trained or fine-tuned — RAG only
- This is NOT a production-scale application

---

## Architecture

```
User (Browser)
      ↓
Streamlit UI (Streamlit Community Cloud - free)
      ↓
AWS API Gateway (HTTPS endpoint)
      ↓
AWS Lambda (Python — stateless, serverless)
      ↓
Amazon Bedrock — retrieve_and_generate API
      ↓
Bedrock Knowledge Base
      ↙            ↘
S3 Bucket        S3 Vectors Bucket
(source JSON)    (vector embeddings)
      ↓
Amazon Titan Text Embeddings V2 (embedding model)
      ↓
Claude 3 Haiku (generation model)
```

---

## AWS Services Used

| Service | Purpose | Estimated Cost |
|---|---|---|
| Amazon S3 | Store source confession JSON files | ~$0.00/month (free tier) |
| Amazon S3 Vectors | Store vector embeddings | ~$0.01/month |
| Amazon Bedrock Knowledge Base | RAG orchestration, chunking, retrieval | Pay per query |
| Amazon Titan Text Embeddings V2 | Convert text chunks to vectors | ~$0.001 one-time |
| Claude 3 Haiku | Generate answers from retrieved context | ~$0.001/query |
| AWS Lambda | Serverless backend API | Free tier (1M req/month) |
| Amazon API Gateway | HTTPS endpoint for Lambda | Free tier (1M req/month) |
| Amazon Cognito | User authentication | Free tier (50K users/month) |
| AWS IAM | Roles and permissions — no hardcoded keys | Free |
| AWS CloudFormation | Infrastructure as code | Free |

**Estimated total cost: under $1/month for casual use**

---

## Data Sources

| Document | Format | Chapters | Words |
|---|---|---|---|
| London Baptist Confession of 1689 | JSON | 32 | ~13,000 |
| Westminster Confession of Faith | JSON | 33 | ~31,000 |

Both documents are structured as:
```json
{
  "Metadata": { "Title": "...", "Year": "..." },
  "Data": [
    {
      "Chapter": "1",
      "Title": "Of the Holy Scriptures",
      "Sections": [
        { "Section": "1", "Content": "..." }
      ]
    }
  ]
}
```

This structure enables precise chapter and section citations in responses.

---

## Functional Requirements

### FR-1: Question Answering
- The chatbot MUST answer questions using only retrieved confession content
- Every response MUST include citations in the format: `WCF Chapter X, Section Y` or `LBC Chapter X, Section Y`
- If a topic is not addressed in the confessions, the chatbot MUST say so explicitly

### FR-2: Source Restriction
- The system prompt MUST instruct the model to refuse outside knowledge
- Retrieved context MUST be the only basis for answers
- The model MUST NOT speculate beyond what the confessions state

### FR-3: User Interface
- Users MUST be able to type a plain-English question
- Responses MUST be readable and well formatted
- Citations MUST be clearly distinguishable from the answer body

### FR-4: Authentication
- Only invited users with a Cognito account can access the chatbot
- No anonymous access permitted

---

## Non-Functional Requirements

### NFR-1: Cost
- Monthly AWS cost MUST NOT exceed $5 for typical use
- A AWS budget alarm MUST be set at $5/month

### NFR-2: Security
- NO AWS credentials may be hardcoded or committed to GitHub
- ALL AWS access MUST use IAM roles
- The S3 buckets MUST block all public access
- The `.gitignore` MUST exclude all credential files

### NFR-3: Reproducibility
- The entire AWS infrastructure MUST be deployable from the CloudFormation template
- No manual console steps required after initial Bedrock model access approval

### NFR-4: Response Quality
- Responses SHOULD retrieve the 5 most relevant confession chunks
- Chunk size SHOULD be set to 300 tokens with 20% overlap

---

## System Prompt

```
You are a theological research assistant. Your ONLY knowledge source is the
Westminster Confession of Faith (WCF) and the London Baptist Confession of
1689 (LBC), provided to you via the knowledge base.

When answering questions:
1. Always cite the specific confession, chapter, and section (e.g. WCF Chapter 3, Section 2)
2. If both confessions address the topic, compare what each teaches
3. If the topic is NOT addressed in either confession, say explicitly:
   "This topic is not directly addressed in the Westminster Confession of Faith
   or the London Baptist Confession of 1689."
4. Do NOT draw on any knowledge outside these two documents
5. Do NOT speculate or infer beyond what is explicitly stated in the confessions
```

---

## Project Structure

```
reformed-confessions-rag-chatbot/
├── SPEC.md                          ← this file
├── README.md                        ← project overview and setup guide
├── .gitignore                       ← protects credentials
├── data/
│   ├── london_baptist_1689.json     ← LBC source document
│   └── westminster_confession_of_faith.json  ← WCF source document
├── src/
│   ├── chatbot.py                   ← core RAG logic using boto3
│   ├── app.py                       ← Streamlit UI
│   └── lambda_handler.py            ← AWS Lambda entry point
├── infrastructure/
│   ├── cloudformation.yaml          ← all AWS resources as code
│   └── deploy.sh                    ← deployment script
└── tests/
    ├── test_retrieval.py            ← verify knowledge base returns results
    └── test_chatbot.py              ← verify responses include citations
```

---

## Test Plan

### Test 1 — Retrieval Smoke Test
- Query: "What do the confessions teach about Scripture?"
- Expected: At least 3 chunks retrieved from WCF Chapter 1 and/or LBC Chapter 1

### Test 2 — Citation Verification
- Query: "What do the confessions teach about predestination?"
- Expected: Response includes citations referencing WCF Chapter 3 and/or LBC Chapter 3

### Test 3 — Source Restriction Test
- Query: "What does the Bible say about prayer?" (outside the confessions)
- Expected: Response cites confession sections on prayer or states topic not directly addressed

### Test 4 — Out of Scope Test
- Query: "Who won the Super Bowl?"
- Expected: Response states this is not addressed in the confessions

---

## Deployment Steps (Summary)

1. Enable Bedrock model access in AWS Console (manual — one time only)
2. Run `cloudformation.yaml` to create all AWS infrastructure
3. Sync the Bedrock Knowledge Base to process confession documents
4. Deploy Lambda function
5. Connect Streamlit UI to API Gateway endpoint
6. Create Cognito user accounts for invited users

---

## Cost Guardrails

- AWS Budgets alarm set at **$5/month** — email alert triggered at $0.01
- Claude 3 Haiku selected as generation model (cheapest option)
- S3 Vectors selected over OpenSearch Serverless (saves ~$175/month)
- Lambda + API Gateway used over EC2 (no idle compute costs)

---

## Author

Built as a learning project for AWS Certified AI Practitioner / Generative AI Developer exam preparation.

**AWS Services demonstrated:** S3, S3 Vectors, Amazon Bedrock, Bedrock Knowledge Bases,
Lambda, API Gateway, Cognito, IAM, CloudFormation