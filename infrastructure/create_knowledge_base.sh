#!/bin/bash
# ============================================================
# Create Bedrock Knowledge Base for Reformed Confessions RAG
# Run this script once after CloudFormation deployment
# ============================================================

REGION="us-east-1"
PROJECT="reformed-confessions-rag"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
DOCUMENTS_BUCKET="${PROJECT}-documents-${ACCOUNT_ID}"
VECTORS_BUCKET="${PROJECT}-vectors-${ACCOUNT_ID}"
KB_ROLE_ARN=$(aws cloudformation describe-stacks \
  --stack-name reformed-confessions-rag \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`BedrockKnowledgeBaseRoleArn`].OutputValue' \
  --output text)

echo "Creating Knowledge Base..."
echo "Documents bucket: $DOCUMENTS_BUCKET"
echo "Vectors bucket: $VECTORS_BUCKET"
echo "KB Role ARN: $KB_ROLE_ARN"

# Create the Knowledge Base
KB_ID=$(aws bedrock-agent create-knowledge-base \
  --name "${PROJECT}-kb" \
  --description "Reformed Confessions RAG Knowledge Base - WCF and LBC 1689" \
  --role-arn "$KB_ROLE_ARN" \
  --knowledge-base-configuration '{
    "type": "VECTOR",
    "vectorKnowledgeBaseConfiguration": {
      "embeddingModelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
    }
  }' \
  --storage-configuration "{
    \"type\": \"S3_VECTORS\",
    \"s3VectorsConfiguration\": {
      \"bucketArn\": \"arn:aws:s3:::${VECTORS_BUCKET}\"
    }
  }" \
  --region $REGION \
  --query 'knowledgeBase.knowledgeBaseId' \
  --output text)

echo "Knowledge Base created with ID: $KB_ID"

# Add S3 data source
echo "Adding confession documents as data source..."
DS_ID=$(aws bedrock-agent create-data-source \
  --knowledge-base-id "$KB_ID" \
  --name "confession-documents" \
  --description "Westminster Confession of Faith and London Baptist Confession 1689" \
  --data-source-configuration "{
    \"type\": \"S3\",
    \"s3Configuration\": {
      \"bucketArn\": \"arn:aws:s3:::${DOCUMENTS_BUCKET}\"
    }
  }" \
  --region $REGION \
  --query 'dataSource.dataSourceId' \
  --output text)

echo "Data source created with ID: $DS_ID"

# Start ingestion job to process documents
echo "Starting ingestion — processing confession documents..."
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id "$KB_ID" \
  --data-source-id "$DS_ID" \
  --region $REGION

echo ""
echo "================================================"
echo "Knowledge Base setup complete!"
echo "Knowledge Base ID: $KB_ID"
echo "IMPORTANT: Copy this ID — you will need it for your Lambda function"
echo "================================================"

# Save KB ID to a local file for reference
echo $KB_ID > kb_id.txt
echo "KB ID saved to kb_id.txt"