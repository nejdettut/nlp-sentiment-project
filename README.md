# AI Duygu Analizi (Sentiment Analysis)

Bu proje, metinlerin duygu durumunu analiz eden bir web uygulamasıdır. Google Gemini AI kullanılarak geliştirilmiştir.

## Özellikler
- **Gemini 2.5 Flash Entegrasyonu:** Gerçek zamanlı ve yüksek doğruluklu analiz.
- **Standalone Streamlit App:** Herhangi bir dış backend gerektirmeden çalışabilir.
- **Hızlı ve Kullanıcı Dostu Arayüz:** Streamlit ile modern tasarım.

## Kurulum
1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/nejdettut/nlp-sentiment-project.git
   ```
2. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. Uygulamayı çalıştırın:
   ```bash
   streamlit run streamlit_app.py
   ```

## Streamlit Cloud Yayına Alma
1. [share.streamlit.io](https://share.streamlit.io/) adresine gidin.
2. `nlp-sentiment-project` reposunu seçin.
3. Main file path: `streamlit_app.py`.
4. **Secrets** kısmına `API_KEY` değerini eklemeyi unutmayın!

Geliştiren: [Nejdet TUT](https://github.com/nejdettut)
