from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging

import google.generativeai as genai

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Sentiment Analysis API")

API_KEY = os.getenv("API_KEY")
if API_KEY and API_KEY.startswith("AIza"):
    genai.configure(api_key=API_KEY)
    HAS_GEMINI = True
    logging.info("Gemini AI is enabled and configured.")
else:
    HAS_GEMINI = False
    logging.warning("Gemini AI is NOT enabled. Using local model or heuristic fallback.")


class TextRequest(BaseModel):
    text: str

# Local model placeholders
try:
    import tensorflow as tf
    from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
    HAS_LOCAL_MODEL = True
except ImportError:
    HAS_LOCAL_MODEL = False
    logging.warning("TensorFlow or Transformers not found. Local model analysis will be unavailable.")

tokenizer = None
model = None

def load_local_model():
    global tokenizer, model
    if not HAS_LOCAL_MODEL:
        return
    try:
        model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = TFAutoModelForSequenceClassification.from_pretrained(model_name)
        logging.info("Local model loaded successfully")
    except Exception as e:
        logging.error(f"Failed to load local model: {e}")
        tokenizer = None
        model = None

@app.on_event("startup")
def startup_event():
    # Only load local model if we don't have Gemini or user specifically wants local
    if not HAS_GEMINI:
        load_local_model()

async def get_gemini_sentiment(text: str):
    if not HAS_GEMINI:
        return None
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Analyze the sentiment of the following text and return ONLY a JSON response in this format:
        {{"positive": score, "negative": score}}
        where score is a float between 0 and 1.
        
        Text: "{text}"
        """
        response = model.generate_content(prompt)
        # Simple extraction of JSON from response
        import json
        import re
        content = response.text
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
    return None

@app.post("/predict")
async def predict(request: TextRequest, x_api_key: str = Header(None)):
    # Simple API Key check
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 1. Try Gemini
    if HAS_GEMINI:
        gemini_result = await get_gemini_sentiment(request.text)
        if gemini_result:
            gemini_result["method"] = "gemini_ai"
            return gemini_result

    # 2. Try Local Model
    if tokenizer and model:
        try:
            inputs = tokenizer(request.text, return_tensors="tf", padding=True, truncation=True)
            outputs = model(inputs)
            probs = tf.nn.softmax(outputs.logits, axis=1).numpy()[0]
            return {
                "negative": float(probs[0]),
                "positive": float(probs[1]),
                "method": "local_model"
            }
        except Exception as e:
            logging.error(f"Local model prediction error: {e}")

    # 3. Fallback Heuristic
    text_lower = request.text.lower()
    positive_words = ["good", "great", "awesome", "beautiful", "happy", "love", "wonderful", "amazing", "güzel", "harika", "sevindim", "seviyorum", "aşk"]
    negative_words = ["bad", "terrible", "sad", "angry", "hate", "awful", "horrible", "kötü", "berbat", "üzgün", "nefret"]
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    total = pos_count + neg_count
    if total == 0:
        return {"negative": 0.5, "positive": 0.5, "method": "heuristic"}
    
    pos_score = pos_count / total
    return {
        "negative": 1.0 - pos_score,
        "positive": pos_score,
        "method": "heuristic"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))