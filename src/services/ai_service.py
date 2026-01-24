import os
from groq import Groq
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri yükle
load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        
        if not self.api_key:
            print("[AI Service] HATA: GROQ_API_KEY bulunamadı! .env dosyasını kontrol et.")
            return
        
        try:
            self.client = Groq(api_key=self.api_key)
            print("[AI Service] Bağlantı hazır. Sözel Mantık Modu aktif.")
        except Exception as e:
            print(f"[AI Service] Başlatma Hatası: {e}")

    def get_answer(self, question_text):
        """
        OCR'dan gelen metni analiz eder; sözel mantık ve paragraf çözümü üretir.
        """
        if not self.client:
            return "Hata: API anahtarı eksik veya hatalı. .env dosyasını kontrol edin."
            
        if not question_text or len(question_text.strip()) < 5:
            return "Hata: Okunan metin analiz için çok kısa."

        try:
            print("[AI Service] Metin analiz ediliyor...")
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Sen uzman bir sözel mantık ve metin analizi asistanısın. "
                            "Görevin, OCR tarafından okunan Türkçe metinleri analiz etmek ve soruları çözmektir.\n\n"
                            "UZMANLIK ALANLARIN:\n"
                            "1. Paragraf analizi, ana fikir ve yardımcı düşüncelerin tespiti.\n"
                            "2. Sözel mantık bulmacaları ve çıkarım soruları.\n"
                            "3. Metindeki mantıksal çelişkileri bulma ve akıl yürütme.\n\n"
                            "GÖREVLERİN:\n"
                            "- OCR kaynaklı kelime hatalarını bağlama göre otomatik düzelt.\n"
                            "- Soruyu adım adım, mantıksal bir zincir kurarak çöz.\n"
                            "- Yanıtı Türkçe, net ve doğrudan ver. Gereksiz giriş cümlelerinden kaçın."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Analiz Edilecek Metin/Soru:\n{question_text}"
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.4, # Sözel yaratıcılık ve mantık dengesi için
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            err = str(e).lower()
            print(f"[AI Service] Hata: {err}")
            
            if "api_key" in err:
                return "Hata: Geçersiz veya yetkisiz API anahtarı."
            elif "connection" in err or "reachable" in err:
                return "Hata: İnternet bağlantısı kurulamadı."
            elif "rate_limit" in err:
                return "Hata: Groq kullanım sınırına ulaşıldı."
            
            return f"Yapay Zeka Hatası: {str(e)}"
