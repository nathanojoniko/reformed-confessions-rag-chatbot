import boto3
import os

# ============================================================
# CONFIGURATION
# ============================================================

KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID", "YPLR0J3KLZ")
MODEL_ARN = os.environ.get(
    "MODEL_ARN",
    "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0"
)
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

# ============================================================
# SYSTEM PROMPT
# This is the single source of truth for how the chatbot behaves.
# It restricts the model to only the confessions and defines
# the response structure.
# ============================================================

SYSTEM_PROMPT = """You are a Reformed theological research assistant. \
Your ONLY knowledge source is the Westminster Confession of Faith (WCF) \
and the London Baptist Confession of 1689 (LBC), provided via the \
knowledge base.

When answering questions always follow this exact structure:

1. EXPLICIT TEACHING
State what the confessions directly and explicitly teach on this topic.
Cite every claim with the specific confession, chapter and section.
Example citation format: (WCF Chapter 3, Section 2) or (LBC Chapter 1, Section 1)
If both confessions address the topic, compare what each teaches.

2. NOT EXPLICITLY ADDRESSED (only include this section if needed)
If the topic is not directly addressed in either confession, clearly state:
"This topic is not explicitly addressed in the Westminster Confession \
of Faith or the London Baptist Confession of 1689."

3. INFORMED INFERENCE
Based on related teachings in the confessions, make intelligent and \
well-reasoned inferences about the topic. For each inference:
- State the inference clearly
- Explain the reasoning
- Cite the specific confession sections that support the inference

IMPORTANT RULES:
- Never draw on knowledge outside these two documents
- Never speculate without grounding in a cited confession section
- Always cite chapter and section for every claim
- If you cannot make a well-grounded inference, say so honestly
"""

# ============================================================
# BEDROCK CLIENT
# ============================================================

def get_bedrock_client():
    """Create and return a Bedrock agent runtime client."""
    return boto3.client(
        service_name="bedrock-agent-runtime",
        region_name=REGION
    )

# ============================================================
# CORE RAG FUNCTION
# This is the heart of the chatbot — it retrieves relevant
# confession chunks and generates a grounded answer.
# ============================================================

def ask_confessions(question: str) -> dict:
    """
    Ask a question and get an answer grounded in the confessions.
    
    Args:
        question: The theological question to ask
        
    Returns:
        dict with 'answer' and 'citations' keys
    """
    client = get_bedrock_client()
    
    prompt_template = SYSTEM_PROMPT + "\n\n$search_results$\n\nQuestion: $query$"
    
    try:
        response = client.retrieve_and_generate(
            input={'text': question},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                    'modelArn': MODEL_ARN,
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': 5
                        }
                    },
                    'generationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': prompt_template
                        }
                    }
                }
            }
        )
        
        # Extract the answer
        answer = response['output']['text']
        
        # Extract citations if available
        citations = []
        if 'citations' in response:
            for citation in response['citations']:
                for reference in citation.get('retrievedReferences', []):
                    location = reference.get('location', {})
                    content = reference.get('content', {}).get('text', '')
                    citations.append({
                        'content': content[:200],
                        'location': location
                    })
        
        return {
            'answer': answer,
            'citations': citations,
            'success': True
        }
        
    except Exception as e:
        return {
            'answer': f"Error: {str(e)}",
            'citations': [],
            'success': False
        }


# ============================================================
# LOCAL TEST
# Run this file directly to test without the UI
# python src/chatbot.py
# ============================================================

if __name__ == "__main__":
    print("Reformed Confessions RAG Chatbot")
    print("=" * 50)
    print("Type 'quit' to exit\n")
    
    while True:
        question = input("Your question: ").strip()
        
        if question.lower() == 'quit':
            print("Goodbye!")
            break
            
        if not question:
            continue
        
        print("\nSearching the confessions...\n")
        result = ask_confessions(question)
        
        print("ANSWER:")
        print("-" * 40)
        print(result['answer'])
        
        if result['citations']:
            print(f"\nSOURCES: {len(result['citations'])} confession chunks retrieved")
        
        print("\n" + "=" * 50 + "\n")