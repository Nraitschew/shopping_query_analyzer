from flask import Flask, render_template, jsonify, request
import requests
import json
from datetime import datetime

app = Flask(__name__)

# Webhook URLs
QUERY_EVALUATOR_WEBHOOK = "http://172.18.32.1:5678/webhook/5063a70b-f51b-4a3a-b4ca-414143e36845"
LLM_COMPARISON_WEBHOOK = "http://172.18.32.1:5678/webhook/553c16ba-1923-464a-a318-878470bb24da"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query-evaluator')
def query_evaluator():
    return render_template('query_evaluator.html')

@app.route('/llm-comparison')
def llm_comparison():
    return render_template('llm_comparison.html')

@app.route('/api/evaluate-query', methods=['POST'])
def evaluate_query():
    try:
        data = request.json
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Call the webhook
        response = requests.post(QUERY_EVALUATOR_WEBHOOK, json={'query': query})
        
        if response.status_code != 200:
            return jsonify({'error': 'Webhook request failed'}), 500
        
        # Parse the response
        response_data = response.json()
        
        # Extract actual values from schema (if needed)
        if isinstance(response_data, list) and len(response_data) > 0 and 'output' in response_data[0]:
            # Handle n8n schema format
            parsed_data = parse_schema_response(response_data[0]['output'])
            return jsonify(parsed_data)
        else:
            return jsonify(response_data)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare-llms', methods=['POST'])
def compare_llms():
    try:
        data = request.json
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Call the webhook
        response = requests.post(LLM_COMPARISON_WEBHOOK, json={'query': query})
        
        if response.status_code != 200:
            return jsonify({'error': 'Webhook request failed'}), 500
        
        # Parse the response
        response_data = response.json()
        
        # Extract actual values from schema (if needed)
        if isinstance(response_data, list) and len(response_data) > 0 and 'output' in response_data[0]:
            # Handle n8n schema format
            parsed_data = parse_llm_comparison_response(response_data[0]['output'])
            return jsonify(parsed_data)
        else:
            return jsonify(response_data)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_schema_response(schema):
    """Parse n8n schema response for query evaluator"""
    data = {}
    
    # Extract scores
    if 'specificity_score' in schema and 'description' in schema['specificity_score']:
        desc = schema['specificity_score']['description']
        # Try to extract number from description
        import re
        match = re.search(r'\d+', desc)
        data['specificity_score'] = int(match.group()) if match else 5
    
    if 'quality_score' in schema and 'description' in schema['quality_score']:
        desc = schema['quality_score']['description']
        match = re.search(r'\d+', desc)
        data['quality_score'] = int(match.group()) if match else 5
    
    # Extract other fields
    data['category'] = schema.get('category', {}).get('description', 'General')
    data['subcategory'] = schema.get('subcategory', {}).get('description', '')
    data['improvement_advice'] = schema.get('improvement_advice', {}).get('description', '')
    data['improved_query_suggestion'] = schema.get('improved_query_suggestion', {}).get('description', '')
    
    # Extract arrays
    if 'missing_information' in schema and 'description' in schema['missing_information']:
        desc = schema['missing_information']['description']
        data['missing_information'] = [item.strip() for item in desc.split(',') if item.strip()]
    else:
        data['missing_information'] = []
    
    if 'strengths' in schema and 'description' in schema['strengths']:
        desc = schema['strengths']['description']
        data['strengths'] = [item.strip() for item in desc.split(',') if item.strip()]
    else:
        data['strengths'] = []
    
    # Extract search intent
    if 'search_intent' in schema:
        if 'description' in schema['search_intent']:
            data['search_intent'] = schema['search_intent']['description']
        elif 'enum' in schema['search_intent'] and len(schema['search_intent']['enum']) > 0:
            data['search_intent'] = schema['search_intent']['enum'][0]
        else:
            data['search_intent'] = 'unclear'
    
    return data

def parse_llm_comparison_response(schema):
    """Parse n8n schema response for LLM comparison"""
    # For now, return a mock response since the actual values aren't in the schema
    # In production, this would parse the actual response data
    return {
        'shopping_query': schema.get('shopping_query', {}).get('description', 'Unknown query'),
        'evaluation_timestamp': datetime.now().isoformat(),
        'chatgpt_evaluation': {
            'scores': {
                'relevance': 8,
                'completeness': 9,
                'actionability': 8,
                'accuracy': 9,
                'structure': 8,
                'added_value': 7,
                'overall_score': 8.2
            },
            'strengths': ['Comprehensive coverage', 'Clear structure', 'Practical recommendations'],
            'weaknesses': ['Could include more specific models', 'Limited price comparisons'],
            'unique_features': ['Detailed spec explanations', 'Future-proofing advice']
        },
        'perplexity_evaluation': {
            'scores': {
                'relevance': 9,
                'completeness': 8,
                'actionability': 9,
                'accuracy': 9,
                'structure': 7,
                'added_value': 8,
                'overall_score': 8.3
            },
            'strengths': ['Current market data', 'Specific model recommendations', 'Price tracking'],
            'weaknesses': ['Less detailed explanations', 'Fewer alternatives'],
            'unique_features': ['Real-time pricing', 'Source citations'],
            'source_usage': {
                'source_count': 8,
                'source_quality': 'high'
            }
        },
        'direct_comparison': {
            'winner': 'Perplexity',
            'winning_margin': 0.1,
            'winning_rationale': 'More current information and specific recommendations',
            'category_winners': {
                'best_relevance': 'Perplexity',
                'best_completeness': 'ChatGPT',
                'best_actionability': 'Perplexity',
                'best_structure': 'ChatGPT'
            }
        },
        'usage_recommendation': {
            'for_this_query': 'Perplexity for current pricing and availability',
            'general_recommendation': 'Use ChatGPT for understanding concepts, Perplexity for current data',
            'optimal_combination': 'Start with ChatGPT for background, then Perplexity for specifics',
            'next_steps': ['Check current prices on manufacturer sites', 'Compare warranty options', 'Read user reviews']
        },
        'summary': {
            'consensus_points': ['Focus on dedicated GPU', 'Minimum 16GB RAM', 'Consider cooling'],
            'differences': ['Price recommendations vary', 'Different brand preferences'],
            'missing_information': ['Specific store availability', 'Upcoming model releases']
        }
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)