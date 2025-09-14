# 🌿 Yapay Zeka Destekli Psikolojik Destek Asistanı / AI-Powered Psychological Support Assistant

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-green?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/Busrwa/Mindcaps_Backend)

**Frontend:** [MindCaps React App](https://github.com/Busrwa/MindCaps)

---

## 📌 Türkçe Açıklama

Bu proje, **empatik ve destekleyici bir psikolojik destek AI asistanı** sunan bir Flask API uygulamasıdır. Kullanıcıların geçmiş ve şimdiki deneyimlerini dikkate alarak, güvenli bir şekilde motive edici mesajlar üretir ve metinlerin duygusal analizini yapar.  

### 🔹 Özellikler

- Kullanıcı metinlerine dayalı **psikolojik destek mesajları üretir**.
- Metinlerin **duygusal analizini** JSON formatında sağlar (sevinç, üzüntü, korku, öfke, tiksinti, şaşkınlık).
- **Kriz durumlarını** tespit eder ve güvenli yönlendirmeler sunar.
- Çok dilli destek: Türkçe ve İngilizce.
- Soru-cevap ve kullanıcı etkileşimleri için endpointler içerir.
- Gelecek benlikten motive edici mesajlar üretir.
- Frontend React uygulaması ile entegre çalışabilir.

### 🔹 Kurulum

1. Repo klonlanır:

```bash
git clone https://github.com/Busrwa/Mindcaps_Backend.git
cd Mindcaps_Backend
```

2. Sanal ortam oluştur ve aktifleştir:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

3. Gerekli paketleri yükle:

```bash
pip install -r requirements.txt
```

4. `.env` dosyasını oluştur ve aşağıdaki değişkenleri ekle:

```env
API_URL=<model_api_url>
MISTRAL_MODEL=<mistral_model_name>
TURKCELL_MODEL=<turkcell_model_name>
DEBUG=True
```

5. Sunucuyu çalıştır:

```bash
python app.py
```

Sunucu varsayılan olarak `localhost` adresinde çalışacaktır.

### 🔹 Endpointler

| Endpoint                   | Yöntem | Açıklama                                             |
| -------------------------- | ------ | ---------------------------------------------------- |
| `/generate`                | POST   | Kullanıcı mesajına yanıt üretir                      |
| `/analyze-emotions`        | POST   | Metinlerin duygusal analizini yapar                  |
| `/get-next-question`       | GET    | Sıralı geçmiş soruların bir sonraki sorusunu getirir |
| `/get-now-question`        | GET    | Sıralı mevcut soruların bir sonraki sorusunu getirir |
| `/generate-future-message` | POST   | Gelecek benlikten motive edici mesaj üretir          |

### 🔹 Örnek Kullanım

```bash
POST /generate
Content-Type: application/json

{
  "text": "Bugün çok üzgünüm.",
  "language": "tr",
  "question": ""
}
```

Yanıt:

```json
{
  "response": "Söylediklerin çok önemli ve seni önemsiyoruz..."
}
```

---

## 📌 English Description

This project is a **Flask API for an empathetic AI-powered psychological support assistant**. It generates motivational messages based on the user's past and present experiences and analyzes the emotional content of texts.

### 🔹 Features

- Generates **supportive psychological messages** based on user input.
- Performs **emotional analysis** in JSON format (joy, sadness, fear, anger, disgust, surprise).
- Detects **crisis situations** and provides safe guidance.
- Supports multiple languages: Turkish and English.
- Provides endpoints for questions and user interactions.
- Generates motivational messages from the user's "future self".
- Can be integrated with the React frontend.

**Frontend:** [MindCaps React App](https://github.com/Busrwa/MindCaps)

### 🔹 Installation

1. Clone the repo:

```bash
git clone https://github.com/Busrwa/Mindcaps_Backend.git
cd Mindcaps_Backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with:

```env
API_URL=<model_api_url>
MISTRAL_MODEL=<mistral_model_name>
TURKCELL_MODEL=<turkcell_model_name>
DEBUG=True
```

5. Run the server:

```bash
python app.py
```

Server will run at `localhost`.

### 🔹 Endpoints

| Endpoint                   | Method | Description                                     |
| -------------------------- | ------ | ----------------------------------------------- |
| `/generate`                | POST   | Generates AI response to user input             |
| `/analyze-emotions`        | POST   | Analyzes emotional content of texts             |
| `/get-next-question`       | GET    | Retrieves next past question in sequence        |
| `/get-now-question`        | GET    | Retrieves next current question in sequence     |
| `/generate-future-message` | POST   | Generates motivational message from future self |

### 🔹 Example Request

```bash
POST /generate
Content-Type: application/json

{
  "text": "I feel very sad today.",
  "language": "en",
  "question": ""
}
```

Response:

```json
{
  "response": "Your words matter and you are not alone..."
}
```
