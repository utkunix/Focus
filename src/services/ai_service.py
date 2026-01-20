import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            print("[AI Service] HATA: GROQ_API_KEY bulunamadı! .env dosyasını kontrol et.")
            self.client = None
            return
        
        try:
            self.client = Groq(api_key=self.api_key)
            print("[AI Service] Bağlantı hazır.")
        except Exception as e:
            print(f"[AI Service] Başlatma Hatası: {e}")
            self.client = None

    def get_answer(self, question_text):

        if not self.client:
            return "Hata: API anahtarı hatalı veya eksik."
            
        if not question_text or len(question_text.strip()) < 5:
            return "Metin çok kısa, soru algılanamadı."

        try:
            print("[AI Service] Soru gönderiliyor...")
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Sen yardımsever bir sınav asistanısın. Kullanıcının gönderdiği soruyu analiz et. Cevabı Türkçe olarak, kısa, net ve doğrudan ver. Gereksiz giriş/çıkış cümleleri kurma."
                    },
                    {
                        "role": "user",
                        "content": f"Soru:\n{question_text}"
                    }
                ],
                model="llama-3.3-70b-versatile", 
                temperature=0.3,
            )
            
            answer = chat_completion.choices[0].message.content
            return answer
            
        except Exception as e:
            print(f"[AI Service] Hata: {str(e)}")
            return f"Yapay Zeka Hatası: {str(e)}"
