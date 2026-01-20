import os
import sys
import unittest
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.ai_service import AIService

class TestFocusApp(unittest.TestCase):
    def setUp(self):
        load_dotenv()

    def test_api_key_exists(self):
        """Test 1: .env dosyası ve API Key var mı?"""
        api_key = os.getenv("GROQ_API_KEY")
        self.assertIsNotNone(api_key, "HATA: GROQ_API_KEY bulunamadı!")
        self.assertTrue(api_key.startswith("gsk_"), "HATA: API Key formatı yanlış (gsk_ ile başlamalı).")
        print("\n✅ API Key kontrolü başarılı.")

    def test_ai_service_initialization(self):
        """Test 2: AI Servisi başlatılabiliyor mu?"""
        service = AIService()
        self.assertIsNotNone(service.client, "HATA: Groq istemcisi başlatılamadı.")
        print("✅ AI Servisi başlatma testi başarılı.")

if __name__ == "__main__":
    unittest.main()
