"""
Error handler module for Tool-Using AI Assistant
"""

class QueryError(Exception):
    """Exception raised for errors in query processing"""
    pass

def handle_api_error(error):
    """Handle API-related errors"""
    if "quota" in str(error).lower():
        return "API quota exceeded. Please check your Gemini API usage limits."
    elif "invalid" in str(error).lower() and "key" in str(error).lower():
        return "Invalid API key. Please check your GOOGLE_API_KEY in the .env file."
    else:
        return f"API error occurred: {str(error)}"

def handle_execution_error(error):
    """Handle Python code execution errors"""
    error_str = str(error).lower()
    
    if "syntax" in error_str:
        return "There was a problem with the generated code syntax."
    elif "name" in error_str and "not defined" in error_str:
        return "The code tried to use an undefined variable or function."
    elif "zero division" in error_str:
        return "Cannot divide by zero."
    elif "type" in error_str:
        return "There was a type mismatch in the calculation."
    else:
        return f"Error executing code: {str(error)}"

def safe_query_processing(func):
    """Decorator for safe query processing"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "generativeai" in str(e).lower() or "api" in str(e).lower():
                return handle_api_error(e)
            else:
                return handle_execution_error(e)
    return wrapper 