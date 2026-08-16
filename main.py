
import os
import http.client
import json

def ask_ai(prompt_text):
    api_key = os.getenv("KEY_ONE")
    if not api_key:
        print("Error: KEY_ONE not found.")
        return

    host = "://googleapis.com"
    endpoint = f"/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt_text}]}]}
    
    try:
        conn = http.client.HTTPSConnection(host)
        conn.request("POST", endpoint, body=json.dumps(data), headers=headers)
        response = conn.getresponse()
        res_data = response.read().decode("utf-8")
        json_res = json.loads(res_data)
        
        answer = json_res['candidates'][0]['content']['parts'][0]['text']
        print("\n=== AI ANSWER ===")
        print(answer)
        print("=================\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Server started successfully...")
    ask_ai("Hello! Please write a short welcome message.")
