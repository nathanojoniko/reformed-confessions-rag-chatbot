import json
import os
import sys

# Add src directory to path so we can import chatbot
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import ask_confessions

# ============================================================
# CORS HEADERS
# Required so the Streamlit UI can call this API
# ============================================================

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def success_response(data: dict) -> dict:
    """Return a successful API response."""
    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps(data)
    }

def error_response(message: str, status_code: int = 500) -> dict:
    """Return an error API response."""
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps({'error': message})
    }

# ============================================================
# MAIN LAMBDA HANDLER
# This is the entry point AWS Lambda calls
# ============================================================

def handler(event, context):
    """
    AWS Lambda entry point.

    Accepts POST requests with a JSON body:
    {
        "question": "What do the confessions teach about grace?"
    }

    Returns:
    {
        "answer": "...",
        "citations": [...],
        "success": true
    }
    """

    # Handle CORS preflight request from browser
    if event.get('httpMethod') == 'OPTIONS':
        return success_response({})

    # Only allow POST requests
    if event.get('httpMethod') != 'POST':
        return error_response('Method not allowed. Use POST.', 405)

    # Parse the request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return error_response('Invalid JSON in request body.', 400)

    # Get the question from the request
    question = body.get('question', '').strip()

    # Validate the question
    if not question:
        return error_response('Question is required.', 400)

    if len(question) > 1000:
        return error_response('Question must be under 1000 characters.', 400)

    # Log the question for CloudWatch
    print(f"Question received: {question}")

    # Call the core chatbot function
    result = ask_confessions(question)

    # Log the outcome
    if result['success']:
        print(f"Answer generated successfully")
    else:
        print(f"Error generating answer: {result['answer']}")

    # Return the response
    return success_response(result)


# ============================================================
# LOCAL TEST
# Run this file directly to test the Lambda handler locally
# python src/lambda_handler.py
# ============================================================

if __name__ == "__main__":
    # Simulate a Lambda event
    test_event = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'question': 'What do the confessions teach about justification?'
        })
    }

    print("Testing Lambda handler locally...")
    print("=" * 50)

    response = handler(test_event, None)

    print(f"Status Code: {response['statusCode']}")
    print("\nResponse Body:")
    print("-" * 40)

    body = json.loads(response['body'])
    print(body['answer'])

    if body.get('citations'):
        print(f"\nSources: {len(body['citations'])} chunks retrieved")

    print("\n" + "=" * 50)