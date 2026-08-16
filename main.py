import os
import json
import requests

def ask_ai(prompt_text):
    api_key = os.getenv("KEY_ONE")
    if not api_key:
        print("Error: KEY_ONE not found. Set environment variable KEY_ONE.")
        return

    # ضع هنا المضيف وendpoint الصحيح لخدمة الـ API التي تستخدمها.
    # مثال عام (استبدل URL بالمسار الصحيح إن اختلف):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt_text}]}]}

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=15)
        if resp.status_code != 200:
            print(f"Request failed: status={resp.status_code}, body={resp.text}")
            return

        json_res = resp.json()
        # تحقق من بنية الاستجابة قبل الوصول للحقل
        candidates = json_res.get("candidates")
        if not candidates:
            print("No candidates found in response:", json_res)
            return

        answer = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        print("\n=== AI ANSWER ===")
        print(answer)
        print("=================\n")
    except requests.RequestException as e:
        print(f"Network/request error: {e}")
    except ValueError as e:
        print(f"JSON decode error: {e}")

if __name__ == "__main__":
    print("Server started successfully...")
    ask_ai("Hello! Please write a short welcome message.")
