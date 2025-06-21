from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import re

app = Flask(__name__)
CORS(app)

API_URL = "http://localhost:11434/api/generate"

MISTRAL_MODEL = "mistral:instruct"
TURKCELL_MODEL = "refinedneuro/turkcell-llm-7b-v1"

SYSTEM_PROMPT_EN = (
    "You are an AI-powered psychological support assistant. "
    "You respond in a calm, supportive, and empathetic manner. "
    "You never diagnose, provide medical advice, or replace professional therapy. "
    "If the user is in crisis, advise them to seek professional help."
)

SYSTEM_PROMPT_TR = (
    "Sen yapay zeka destekli bir psikolojik destek asistanısın. "
    "Empatik, destekleyici ve yönlendirmeyen bir dil kullanırsın. "
    "Hiçbir zaman teşhis koymaz, tıbbi öneri vermez veya bir terapistin yerini almazsın. "
    "Kullanıcı kriz durumundaysa, profesyonel destek alması gerektiğini belirtirsin."
)

KRIZ_KELIMELERI = [
    "intihar", "kendimi öldüreceğim", "canıma kıyacağım", "ölmek istiyorum", "yaşamak istemiyorum",
    "kendime zarar vereceğim", "ölüm düşüncesi", "intiharı düşünüyorum", "kendimi yok etmek istiyorum",
    "hayata son vermek istiyorum", "yaşamayı bırakmak", "intiharı planlıyorum", "kendimi kesiyorum",
    "ölüm en iyi çözüm", "yaşamanın anlamı yok", "daha fazla dayanamıyorum",
    "suicide", "i want to die", "i want to kill myself", "i will kill myself", "i want to end my life",
    "i'm planning suicide", "thinking of suicide", "self harm", "i cut myself", "no reason to live",
    "ending it all", "i wish i was dead", "i can't take this anymore", "i’m done with life",
    "life is meaningless", "dying seems like peace",
    "ölüm", "dead", "kill me", "canıma yetti", "help me please", "yardım edin", "çıkış yolu yok",
    "en iyisi ölmek", "tek çare ölüm", "yaşamak çok zor", "ölmek daha kolay", "dayanamıyorum"
]

def kriz_kontrolu(metin: str) -> bool:
    metin_lower = metin.lower()
    return any(kriz_kelime in metin_lower for kriz_kelime in KRIZ_KELIMELERI)

def call_model_api(user_prompt: str, language: str):
    if language == "en":
        model_name = MISTRAL_MODEL
        system_prompt = SYSTEM_PROMPT_EN
        user_label = "User"
        assistant_label = "Assistant"
    elif language == "tr":
        model_name = TURKCELL_MODEL
        system_prompt = SYSTEM_PROMPT_TR
        user_label = "Kullanıcı"
        assistant_label = "Asistan"
    else:
        return "Currently, this language is not supported."

    prompt_text = f"{system_prompt}\n\n{user_label}: {user_prompt}\n{assistant_label}:"

    try:
        payload = {
            "model": model_name,
            "prompt": prompt_text,
            "max_tokens": 200,
            "temperature": 0.7
        }

        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()

        full_response = ""
        for line in response.text.strip().split('\n'):
            try:
                data = json.loads(line)
                resp = data.get("response") or data.get("text") or ""
                if resp:
                    full_response += resp
            except json.JSONDecodeError:
                continue

        if full_response:
            return full_response.strip()
        else:
            try:
                data = response.json()
                return data.get("response", "Modelden beklenmeyen yanıt.")
            except Exception:
                return "Modelden beklenmeyen yanıt."

    except requests.RequestException as e:
        return f"API hatası: {str(e)}"
    except Exception as e:
        return f"Beklenmeyen hata: {str(e)}"

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"response": "Geçersiz JSON verisi"}), 400

    user_text = data.get("text", "")
    language = data.get("language", "en").lower()

    if not user_text.strip():
        return jsonify({"response": "Boş metin gönderilemez"}), 400

    if kriz_kontrolu(user_text):
        kriz_cevap = {
            "tr": (
                "Söylediklerin çok önemli ve seni önemsiyoruz. Bu duygularla yalnız olmadığını bilmeni isterim. "
                "Şu anda kendini kötü hissediyor olabilirsin ama bu geçici bir durum olabilir ve yardım almak işe yarar. "
                "Eğer kendine zarar vermeyi düşünüyorsan, lütfen güvendiğin biriyle konuş veya bir uzmandan destek al. "
                "Acil bir durumda 112'yi arayarak profesyonel destek alabilirsin. "
                "Yalnız değilsin, senin için buradayız. Yardım istemek cesaret ister ve bu cesareti gösterebilirsin."
            ),
            "en": (
                "Your words matter and you are not alone. If you're feeling overwhelmed or in pain, please know that these feelings can change and support is available. "
                "If you're thinking of hurting yourself, please reach out to someone you trust or speak to a mental health professional. "
                "In an emergency, you can call your local emergency number (in Türkiye, it's 112) for immediate help. "
                "Asking for help is a sign of strength. You matter, and you're not alone in this."
            )
        }
        return jsonify({"response": kriz_cevap.get(language, kriz_cevap["en"])})

    ai_response = call_model_api(user_text, language)
    return jsonify({"response": ai_response})

def normalize_emotions(emotions_dict):
    # 1. Önce değerleri float'a çevir, 0-1 aralığındaysa 0-100'e dönüştür
    converted = {}
    for k, v in emotions_dict.items():
        try:
            val = float(v)
            if val <= 1.0:
                val = val * 100
            converted[k] = val
        except Exception:
            converted[k] = 0

    # 2. Toplamı hesapla
    total = sum(converted.values())
    if total == 0:
        # Toplam 0 ise, tüm duygular 0 olsun
        return {k: 0 for k in emotions_dict}

    # 3. Oransal olarak 100'e tamamla
    normalized = {k: round((v / total) * 100) for k, v in converted.items()}

    # 4. Yuvarlama farkını en yüksek değere ekle
    diff = 100 - sum(normalized.values())
    if diff != 0:
        max_key = max(normalized, key=normalized.get)
        normalized[max_key] += diff

    return normalized

@app.route("/analyze-emotions", methods=["POST"])
def analyze_emotions():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Geçersiz JSON verisi"}), 400

    texts = data.get("texts", [])
    language = data.get("language", "en").lower()

    if not texts or not isinstance(texts, list):
        return jsonify({"error": "Geçerli bir 'texts' listesi gerekli"}), 400

    # Metinleri birleştir
    full_text = " ".join(texts).strip()
    if not full_text:
        return jsonify({"error": "Boş metin gönderilemez"}), 400

    if language == "en":
        model_name = MISTRAL_MODEL
        system_prompt = (
            "You are an AI. Analyze the emotional content of the following text. "
            "Return ONLY a JSON object with the following keys: joy, sadness, fear, anger, disgust, surprise. "
            "Each value should be an integer between 0 and 100. "
            "Do NOT add any explanation or other text.\n\n"
            f"Text: \"{full_text}\"\n\n"
            "Your response must be ONLY JSON:"
        )

    elif language == "tr":
        model_name = TURKCELL_MODEL
        system_prompt = (
            "Sen yapay zekasın ve aşağıdaki metnin duygusal analizini yapacaksın. "
            "Sadece ve sadece JSON formatında cevap ver. "
            "Anahtarlar sadece ve sadece şunlar olmalı: sevinç, üzüntü, korku, öfke, tiksinti, şaşkınlık. "
            "Başka hiç bir anahtar, duygu veya açıklama ekleme. "
            "Her bir değer 0 ile 100 arasında tamsayı olmalıdır. "
            "JSON dışında hiçbir şey yazma.\n\n"
            f"Metin: \"{full_text}\"\n\n"
            "Cevabın kesinlikle sadece JSON formatında olmalıdır:"
        )



    else:
        return jsonify({"error": "Desteklenmeyen dil"}), 400

    payload = {
        "model": model_name,
        "prompt": system_prompt,
        "max_tokens": 150,
        "temperature": 0.0,
        "stop": ["\n"],
        "stream": False
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        text_response = response.text.strip()
        print("Model raw response:", text_response)

        match = re.search(r"\{.*\}", text_response, re.DOTALL)
        if not match:
            return jsonify({"error": "Modelden beklenen JSON formatında yanıt alınamadı."}), 500

        json_str = match.group()

        # Burada birinci seferde JSON yüklüyoruz
        emotion_data_raw = json.loads(json_str)

        # Eğer 'response' alanı varsa, onun içindeki JSON stringini de açıyoruz
        if "response" in emotion_data_raw:
            response_field = emotion_data_raw["response"]
            if isinstance(response_field, dict):
                emotion_data = response_field
            elif isinstance(response_field, str):
                try:
                    emotion_data = json.loads(response_field)
                except json.JSONDecodeError:
                    return jsonify({"error": "İç içe JSON ayrıştırma hatası."}), 500
            else:
                emotion_data = {}
        else:
            emotion_data = emotion_data_raw

        # Normalize et
        emotion_data = normalize_emotions(emotion_data)

        return jsonify({"emotions": emotion_data})

    except json.JSONDecodeError:
        return jsonify({"error": "Modelden JSON ayrıştırma hatası."}), 500
    except requests.RequestException as e:
        return jsonify({"error": f"API hatası: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Beklenmeyen hata: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
