import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables from the root .env
load_dotenv(dotenv_path="../.env")

st.set_page_config(page_title="AI Sentiment Analysis", page_icon="🧠")

st.title("🧠 AI Duygu Analizi")
st.write("Metnin duygu durumunu analiz edin")

text = st.text_area(
    "Metni girin:",
    height=150,
    placeholder="Bugün hava çok güzel..."
)

# Configuration
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/predict")
API_KEY = os.getenv("API_KEY")

if st.button("Analiz Et"):
    if not text.strip():
        st.warning("Lütfen bir metin girin.")
    else:
        headers = {"x-api-key": API_KEY}
        try:
            with st.spinner("Analiz ediliyor..."):
                response = requests.post(
                    API_URL,
                    json={"text": text},
                    headers=headers,
                    timeout=10
                )

            if response.status_code == 200:
                result = response.json()
                st.success(f"Analiz tamamlandı (Yöntem: {result.get('method', 'bilinmiyor')})")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Pozitif", f"{result['positive']:.2%}")
                with col2:
                    st.metric("Negatif", f"{result['negative']:.2%}")
                
                if result['positive'] > result['negative']:
                    st.info("Bu metin genel olarak **Pozitif** bir duygu taşıyor.")
                elif result['positive'] < result['negative']:
                    st.info("Bu metin genel olarak **Negatif** bir duygu taşıyor.")
                else:
                    st.info("Bu metin **Nötr** bir duygu taşıyor.")
            elif response.status_code == 401:
                st.error("API Anahtarı hatası (Unauthorized). Lütfen .env dosyasını kontrol edin.")
            else:
                st.error(f"API hatası: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Sunucuya bağlanılamadı. Lütfen backend'in çalıştığından emin olun (Liman: 8000).")
        except Exception as e:
            st.error(f"Beklenmedik bir hata oluştu: {e}")

st.divider()
st.caption("Geliştirilmiştir: Nejdet TUT")