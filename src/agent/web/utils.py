import re
import ast

def read_markdown_file(file_path: str) -> str:
    with open(file_path, 'r',encoding='utf-8') as f:
        markdown_content = f.read()
    return markdown_content

def extract_agent_data(text):
    # Dictionary to store extracted values
    result = {}
    # Check if it's Option 1 (Action-based)
    if re.search(r"<Route>Action</Route>", text):
        # Extract Memory
        evaluate_memory = re.search(r"<Memory>(.*?)<\/Memory>", text, re.DOTALL)
        if evaluate_memory:
            result['Memory'] = evaluate_memory.group(1).strip()
        # Extract Evaluate
        evaluate_match = re.search(r"<Evaluate>(.*?)<\/Evaluate>", text, re.DOTALL)
        if evaluate_match:
            result['Evaluate'] = evaluate_match.group(1).strip()
        # Extract Thought
        thought_match = re.search(r"<Thought>(.*?)<\/Thought>", text, re.DOTALL)
        if thought_match:
            result['Thought'] = thought_match.group(1).strip()
        # Extract Action-Name
        action_name_match = re.search(r"<Action-Name>(.*?)<\/Action-Name>", text, re.DOTALL)
        if action_name_match:
            result['Action Name'] = action_name_match.group(1).strip()
        # Extract and convert Action-Input to a dictionary
        action_input_match = re.search(r"<Action-Input>(.*?)<\/Action-Input>", text, re.DOTALL)
        if action_input_match:
            action_input_str = action_input_match.group(1).strip()
            try:
                # Convert string to dictionary safely using ast.literal_eval
                result['Action Input'] = ast.literal_eval(action_input_str)
            except (ValueError, SyntaxError):
                # If there's an issue with conversion, store it as raw string
                result['Action Input'] = action_input_str
        # Extract Route (should always be 'Action' in Option 1)
        route_match = re.search(r"<Route>(.*?)<\/Route>", text, re.DOTALL)
        if route_match:
            result['Route'] = route_match.group(1).strip()
    # Check if it's Option 2 (Final Answer)
    elif re.search(r"<Route>Answer</Route>", text):
        # Extract Memory
        evaluate_memory = re.search(r"<Memory>(.*?)<\/Memory>", text, re.DOTALL)
        if evaluate_memory:
            result['Memory'] = evaluate_memory.group(1).strip()
        # Extract Evaluate
        evaluate_match = re.search(r"<Evaluate>(.*?)<\/Evaluate>", text, re.DOTALL)
        if evaluate_match:
            result['Evaluate'] = evaluate_match.group(1).strip()
        # Extract Thought
        thought_match = re.search(r"<Thought>(.*?)<\/Thought>", text, re.DOTALL)
        if thought_match:
            result['Thought'] = thought_match.group(1).strip()
        # Extract Final Answer
        final_answer_match = re.search(r"<Final-Answer>(.*?)<\/Final-Answer>", text, re.DOTALL)
        if final_answer_match:
            result['Final Answer'] = final_answer_match.group(1).strip()
        # Extract Route (should always be 'Final' in Option 2)
        route_match = re.search(r"<Route>(.*?)<\/Route>", text, re.DOTALL)
        if route_match:
            result['Route'] = route_match.group(1).strip()
    return result
