import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv
import re
from error_handler import safe_query_processing, handle_api_error, handle_execution_error

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY environment variable not set")
    sys.exit(1)

try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API: {handle_api_error(e)}")
    sys.exit(1)

def execute_python_code(code):
    """Execute Python code in a safe environment and return the result"""
    try:
        # Create a restricted local environment for execution
        local_env = {}
        # Execute the code and capture the result
        exec(f"result = {code}", {"__builtins__": __builtins__}, local_env)
        return local_env.get("result")
    except Exception as e:
        return handle_execution_error(e)

@safe_query_processing
def process_query(query):
    """Process user query using Gemini to determine if tools are needed"""
    
    # Prompt for Gemini to classify and handle the query
    system_prompt = """
    You are an AI assistant that can use Python as a tool to solve problems.
    
    For each user query:
    1. Determine if the query requires:
       - Math calculations
       - Character/string counting
       - Or can be answered directly
    
    2. If math or counting is needed:
       - Generate ONLY the Python code needed (no explanation)
       - Keep the code simple and minimal
       - Don't include print statements
    
    3. If no tools are needed:
       - Respond with "DIRECT_ANSWER:" followed by your answer
    
    4. If the query is about how you work:
       - Respond with "DIRECT_ANSWER:" followed by a brief explanation
    
    Example responses:
    - For "What is 25 * 16?": 25 * 16
    - For "How many 'e's in 'excellent'?": "excellent".count("e")
    - For "What is the capital of France?": DIRECT_ANSWER: Paris
    - For "How do you solve math problems?": DIRECT_ANSWER: I use Python code to perform calculations
    
    Only respond with the code or DIRECT_ANSWER format. No explanations.
    """
    
    # Create the generative model - using Gemini 1.5 Flash model
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    
    # Get Gemini's response for classification and code generation
    response = model.generate_content([system_prompt, query])
    
    # Process the response
    ai_response = response.text.strip()
    
    if ai_response.startswith("DIRECT_ANSWER:"):
        # Direct answer from AI
        return ai_response.replace("DIRECT_ANSWER:", "").strip()
    else:
        # Python code to execute
        # Clean up the code (remove markdown code blocks if present)
        code = re.sub(r'```python|```', '', ai_response).strip()
        
        # Execute the code
        result = execute_python_code(code)
        
        # Format the response based on the query type
        if "count" in query.lower() or "how many" in query.lower():
            return format_counting_response(query, code, result)
        else:
            return format_math_response(query, code, result)

def format_counting_response(query, code, result):
    """Format response for counting queries"""
    # Extract what was being counted from the code if possible
    match = re.search(r'\.count\([\'\"](.*?)[\'\"]', code)
    if match:
        char = match.group(1)
        text = re.search(r'[\'\"]([^\'\"]*)[\'\"]\.count', code)
        if text:
            text = text.group(1)
            return f"There {'is' if result == 1 else 'are'} {result} '{char}' in '{text}'"
    
    # Fallback format
    return f"The count is: {result}"

def format_math_response(query, code, result):
    """Format response for math queries"""
    return f"The result is: {result}"

def main():
    """Main function to run the application"""
    print("\n===== Tool-Using AI Assistant =====")
    print("Ask me questions about math or character counting!")
    print("Type 'exit' to quit.\n")
    
    while True:
        # Get user query
        query = input("\nYour question: ")
        
        # Exit condition
        if query.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        
        # Process the query
        response = process_query(query)
        
        # Display response
        print(f"\nAnswer: {response}")

if __name__ == "__main__":
    main() 