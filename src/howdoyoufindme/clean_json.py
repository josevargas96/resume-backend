# src/howdoyoufindme/clean_json.py

import json
import re


def extract_json_string(response: str) -> str:
    """
    Attempts to extract just the JSON part from a string.
    Finds the first '{' and the matching last '}' and returns the substring.
    Also handles potential formatting issues.
    """
    try:
        # First, try to directly parse it
        json.loads(response)
        return response
    except json.JSONDecodeError:
        # If direct parsing fails, try to clean it up
        pass

    # Find JSON structure beginning and end
    start_idx = response.find('{')
    end_idx = response.rfind('}')
    
    if start_idx == -1 or end_idx == -1:
        raise ValueError("No JSON object braces found in response.")
    
    json_str = response[start_idx:end_idx + 1]
    
    # Clean up common formatting issues
    # Remove markdown code block markers
    json_str = re.sub(r'```json\s*', '', json_str)
    json_str = re.sub(r'\s*```', '', json_str)
    
    # Fix nested quotes issues
    json_str = re.sub(r'(?<!\\)"(?!,|\s*}|\s*]|\s*:)', '\\"', json_str)
    
    # Fix common JSON formatting issues
    json_str = json_str.replace('\n', ' ')  # Remove newlines
    json_str = re.sub(r',(\s*})', r'\1', json_str)  # Remove trailing commas in objects
    json_str = re.sub(r',(\s*])', r'\1', json_str)  # Remove trailing commas in arrays
    json_str = re.sub(r'}\s*{', '},{', json_str)  # Fix adjacent objects
    json_str = re.sub(r']\s*\[', '],[', json_str)  # Fix adjacent arrays
    
    # Try to verify proper quote pairing
    try:
        # Attempt to parse the cleaned JSON
        json.loads(json_str)
        return json_str
    except json.JSONDecodeError as e:
        # If parsing still fails, try to locate problematic area
        problem_char = e.pos
        context = json_str[max(0, problem_char - 50):min(len(json_str), problem_char + 50)]
        print(f"JSON parse error near: ...{context}...")
        raise ValueError(f"Failed to parse JSON after cleaning: {str(e)}. Error location: {context}")


def clean_and_parse_json(response: str) -> dict:
    """
    Clean and parse JSON from a string response.
    Handles common formatting issues and returns a parsed JSON object.
    """
    try:
        # First try direct parsing
        return json.loads(response)
    except json.JSONDecodeError:
        try:
            # Try to extract and clean JSON
            json_str = extract_json_string(response)
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            # If still failing, add more context to the error
            print(f"Full response that failed to parse: {response}")
            raise ValueError(f"Failed to parse JSON after cleaning: {str(e)}. Content: {response[:100]}...")