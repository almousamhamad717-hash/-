import os
import json
import requests


def extract_answer_from_response(json_res):
    """حاول استخلاص النص الناتج من أشكال استجابة مختلفة."""
    # 1) شكل يحتوي candidates -> content -> parts -> text
    candidates = json_res.get("candidates")
    if candidates and isinstance(candidates, list):
        try:
            return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        except Exception:
            pass

    # 2) شكل قديم/آخر: outputs -> [ {"content":[{"type":"output_text","text":"..."}]} ]
    outputs = json_res.get("outputs")
    if outputs and isinstance(outputs, list):
        try:
            first = outputs[0]
            content = first.get("content") or []
            for c in content:
                if isinstance(c, dict) and c.get("type") == "output_text":
                    return c.get("text", "")
                # بعض API تعيد أجزاء نصية مباشرة
                if isinstance(c, dict) and c.get("text"):
                    return c.get("text")
        except Exception:
            pass

    # 3) حقل شائع آخر
    if "outputText" in json_res:
        return json_res.get("outputText")

    # 4) حاول الاقتراب من أي نص قابل للطباعة (fallback):
    # ابحث عن أول قيمة نصية داخل الاستجابة
    def find_first_text(obj):
        if isinstance(obj, str):
            return obj
        if isinstance(obj, dict):
            for v in obj.values():
                t = find_first_text(v)
                if t:
                    return t
        if isinstance(obj, list):
            for item in obj:
                t = find_first_text(item)
                if t:
                    return t
        return None

    fallback = find_first_text(json_res)
    return fallback or ""


def ask_ai(prompt_text):
    # دعم أسماء متغيرات البيئة الشائعة
    api_key = os.getenv("KEY_ONE") or os.getenv("GOOGLE_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        print("Error: API key not found. Set environment variable KEY_ONE or GOOGLE_API_KEY or API_KEY.")
        return None

    # نقطة النهاية الأساسية — عدّلها إذا كنت تستخدم endpoint مختلف
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    headers = {"Content-Type": "application/json"}
    params = {}

    # إذا كان المفتاح مُمرَّراً كـ "Bearer ..." فاستخدم Authorization header
    if api_key.lower().startswith("bearer "):
        headers["Authorization"] = api_key
    else:
        # بعض مفاتيح Google تبدأ بـ AIza... وهذه عادة تُمرَّر كـ key= في الـ query
        # سنمررها كـ query param إذا بدا أنها مفتاح API، وإلا سنمررها كبان "Bearer"
        if api_key.startswith("AIza") or len(api_key) < 60:
            params["key"] = api_key
        else:
            headers["Authorization"] = f"Bearer {api_key}"

    data = {"contents": [{"parts": [{"text": prompt_text}]}]}

    try:
        resp = requests.post(url, headers=headers, params=params, json=data, timeout=15)
        # اطبع الجسم عند فشل الحالة لمزيد من التشخيص
        if resp.status_code != 200:
            print(f"Request failed: status={resp.status_code}, body={resp.text}")
            return None

        try:
            json_res = resp.json()
        except ValueError as e:
            print(f"JSON decode error: {e}")
            print("Raw response:", resp.text)
            return None

        answer = extract_answer_from_response(json_res)
        if not answer:
            print("No usable text found in response:", json.dumps(json_res, ensure_ascii=False, indent=2))
            return None

        return answer

    except requests.RequestException as e:
        print(f"Network/request error: {e}")
        return None


if __name__ == "__main__":
    print("Server started successfully...")
    answer = ask_ai("Hello! Please write a short welcome message.")
    if answer:
        print("\n=== AI ANSWER ===")
        print(answer)
        print("=================\n")
