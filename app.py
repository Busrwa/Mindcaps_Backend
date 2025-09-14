from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import re
import os

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = os.getenv("DEBUG", "False") == "True"
#ollama run mistral:instruct
#ollama run refinedneuro/turkcell-llm-7b-v1
#ollama serve


API_URL = os.getenv("API_URL")

MISTRAL_MODEL = os.getenv("MISTRAL_MODEL")
TURKCELL_MODEL = os.getenv("TURKCELL_MODEL")

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

QUESTIONS_BY_LANG = {
    "tr": [
        "Geçmişte seni en çok etkileyen olay neydi?",
        "Çocukken en büyük hayalin neydi?",
        "Geçmişte pişmanlık duyduğun bir karar var mı?",
        "Seni en çok ne mutlu ederdi?",
        "Kendine geçmişte ne öğüt verirdin?"
    ],
    "en": [
        "What was the most impactful event in your past?",
        "What was your biggest dream as a child?",
        "Is there a decision from the past you regret?",
        "What used to make you happiest?",
        "What advice would you give to your past self?"
    ]
}

QUESTIONS_NOW_BY_LANG = {
    "tr": [
        "Şu anda seni en çok mutlu eden şey nedir?",
        "Bugünlerde seni en çok zorlayan konu nedir?",
        "Kendini en çok hangi anlarda huzurlu hissediyorsun?",
        "Kendinle ilgili şu anda en çok gurur duyduğun şey nedir?",
        "Bugünkü ruh halini tek kelimeyle nasıl tanımlarsın?"
    ],
    "en": [
        "What currently brings you the most joy?",
        "What is the most challenging thing you're facing these days?",
        "When do you feel most at peace with yourself?",
        "What are you most proud of about yourself right now?",
        "If you could describe your mood today in one word, what would it be?"
    ]
}


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

def call_model_api(user_prompt: str, language: str, question: str = ""):
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

    # 💡 Soruyu prompt'a dahil et
    if question:
        prompt_text = (
            f"{system_prompt}\n\n"
            f"Soru: {question}\n"
            f"{user_label}: {user_prompt}\n"
            f"{assistant_label}:"
        )
    else:
        prompt_text = f"{system_prompt}\n\n{user_label}: {user_prompt}\n{assistant_label}:"

    try:
        payload = {
            "model": model_name,
            "prompt": prompt_text,
            "max_tokens": 200,
            "temperature": 0.7
        }

        response = requests.post(API_URL, json=payload, timeout=40)
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
    question = data.get("question", "")
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

    ai_response = call_model_api(user_text, language, question)
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

EXPECTED_KEYS = ["sevinç", "üzüntü", "korku", "öfke", "tiksinti", "şaşkınlık"]

def fix_keys(emotion_data):
    fixed = {}
    for key in EXPECTED_KEYS:
        fixed[key] = emotion_data.get(key, 0)
    return fixed

@app.route("/analyze-emotions", methods=["POST"])
def analyze_emotions():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Geçersiz JSON verisi"}), 400

    texts = data.get("texts", [])
    language = data.get("language", "en").lower()

    if not texts or not isinstance(texts, list):
        return jsonify({"error": "Geçerli bir 'texts' listesi gerekli"}), 400

    full_text = "\n".join(texts).strip()
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
            "Anahtarlar kesinlikle şu olmalı ve sadece şu anahtarları kullanmalısın: "
            "\"sevinç\", \"üzüntü\", \"korku\", \"öfke\", \"tiksinti\", \"şaşkınlık\". "
            "Başka hiçbir anahtar veya açıklama ekleme. "
            "Her değer 0 ile 100 arasında tam sayı olmalıdır. "
            "Cevabın kesinlikle sadece JSON formatında olmalıdır.\n\n"
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
        emotion_data_raw = json.loads(json_str)

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

        # ---- Burada key sabitleme ----
        emotion_data = fix_keys(emotion_data)

        # Normalize et
        emotion_data = normalize_emotions(emotion_data)

        return jsonify({"emotions": emotion_data})

    except json.JSONDecodeError:
        return jsonify({"error": "Modelden JSON ayrıştırma hatası."}), 500
    except requests.RequestException as e:
        return jsonify({"error": f"API hatası: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Beklenmeyen hata: {str(e)}"}), 500

@app.route("/get-next-question", methods=["GET"])
def get_next_question():
    index = int(request.args.get("index", 0))
    language = request.args.get("language", "tr").lower()

    questions = QUESTIONS_BY_LANG.get(language, QUESTIONS_BY_LANG["tr"])

    if index < len(questions):
        return jsonify({
            "question": questions[index],
            "has_more": index < len(questions) - 1
        })
    return jsonify({"question": None, "has_more": False})

@app.route("/get-now-question", methods=["GET"])
def get_now_question():
    index = int(request.args.get("index", 0))
    language = request.args.get("language", "tr").lower()

    questions_now = QUESTIONS_NOW_BY_LANG.get(language, QUESTIONS_NOW_BY_LANG["tr"])

    if index < len(questions_now):
        return jsonify({
            "question": questions_now[index],
            "has_more": index < len(questions_now) - 1
        })
    return jsonify({"question": None, "has_more": False})


@app.route("/generate-future-message", methods=["POST"])
def generate_future_message():
    data = request.get_json(force=True, silent=True)
    history = data.get("history", [])  # geçmiş ve şimdiki cevaplar listesi
    language = data.get("language", "tr")

    if not history or not isinstance(history, list):
        return jsonify({"error": "Geçmiş yanıtlar gerekli"}), 400

    full_text_input = "\n".join(history).strip()
    if not full_text_input:
        return jsonify({"error": "Boş içerik gönderilemez"}), 400

    if language == "tr":
        prompt = (
            "Gelecekten şu ana yazılmış, kişiye özel olmayan, motive edici bir mesaj oluştur. "
            "Mesajda doğrudan kullanıcıya hitap et, sadece 'sen' tarzı hitap ifadeleri kullan. "
            "'Sevgili şimdiki benliğim' ifadesini mutlaka kullan. "
            "‘Siz’, ‘sizler’, ‘olacaksınız’, ‘gideceksiniz’ gibi çoğul veya resmi ifadeler kullanma. "
            "Kullanıcının yanıtlarına veya durumuna asla atıfta bulunma. "
            "Mesaj pozitif, şiirsel ve ilham verici olsun. "
            "Ana tema: Her şeyin yoluna gireceğini söyle, gelecekte mutlu ve huzurlu olduğumuzu vurgula, "
            "gelecekte mutluluğun kesin olduğunu belirt. "
            "Sadece yazıyı oluştur; başka bir şey ekleme. "
            f"Kullanıcının bazı deneyimleri:\n{full_text_input}\n\n"
            "Yukarıdaki kurallara tam uy ve sadece mesajı yaz."
        )

        model_name = TURKCELL_MODEL
    else:
        prompt = (
            "Below are heartfelt responses from a user reflecting on their past and present self. "
            "Carefully read and understand these answers, then write a deeply emotional, motivational, and compassionate letter "
            "as if it is from the user's future self to their current self.\n\n"

            "The letter must begin with this exact line:\n"
            "\"From My Future Self to My Present Self:\"\n\n"

            "❗ The tone of the letter should be supportive, warm, encouraging, and empathetic. "
            "Speak as their future self — not as a therapist, not as an AI assistant. Be *them*, just further along.\n\n"

            "Please make sure to:\n"
            "- Acknowledge the struggles and emotional journey shown in their answers.\n"
            "- Highlight the lessons learned from past experiences.\n"
            "- Reassure the user that their current efforts are meaningful and shaping a stronger self.\n"
            "- Include hope, strength, and belief in them.\n"
            "- End the letter with a gentle, warm, and inspiring closing message.\n"
            "- DO NOT include any explanations, formatting instructions, or system messages. Only return the letter.\n\n"

            f"The user's answers:\n{full_text_input}\n\n"
            "Generate the letter in one single block of text. No explanations. Only the letter content in natural English."
        )

        model_name = MISTRAL_MODEL

    payload = {
        "model": model_name,
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.7,
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=40)
        response.raise_for_status()

        # Hem JSON satır satır (stream) hem düz metin desteklenir
        full_text = ""
        for line in response.text.strip().split("\n"):
            try:
                data = json.loads(line)
                if isinstance(data, dict) and "response" in data:
                    full_text += data["response"]
            except json.JSONDecodeError:
                continue

        if not full_text:
            full_text = response.text.strip()

        return jsonify({"message": full_text.strip()})

    except Exception as e:
        import traceback
        print("HATA:", traceback.format_exc())
        return jsonify({
            "error": "Sunucu hatası oluştu.",
            "details": str(e),
            "traceback": traceback.format_exc()
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
