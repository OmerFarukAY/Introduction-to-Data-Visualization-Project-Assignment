# AI Assistant: Hybrid Clipboard Master 🚀

AI Assistant, günlük metin işleme ve mutfak/tarif analiz süreçlerinizi hızlandırmak için tasarlanmış, **Ollama** (Yerel LLM) ve **Gemini 3 Flash** (Cloud LLM) destekli bir arka plan yardımcı aracıdır.

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-white?style=flat-square)](https://ollama.com)
[![Gemini](https://img.shields.io/badge/Gemini%203-Flash%20Preview-teal?style=flat-square)](https://aistudio.google.com/)

</div>

---

## ✨ Temel Özellikler

Bu uygulama, herhangi bir uygulama içindeyken seçtiğiniz metin üzerinde akıllı AI işlemleri yapmanızı sağlar.

### 🏠 Yerel & Bulut Hibrit Yapı
- **F8 Tuşu (Yerel):** Ollama üzerinden `gemma3:1b` modelini kullanır. İnternet gerektirmeden hızlı ve gizli işlemler yapar.
- **F9 Tuşu (Bulut):** Google Gemini 3 Flash modelini kullanır. Karmaşık analizler ve karmaşık tarifler için üstün zeka sunar.

### 🛠️ Gelişmiş AI Komutları
- **💼 Kurumsal Çeviri:** Kaba veya duygusal metinleri profesyonel e-posta diline çevirir.
- **📝 Akıllı Özetleme:** Uzun metinleri özetler ve çıkarılması gereken görevleri (TODO) listeler.
- **🍷 Mutfak Asistanı:** 
    - *Buna Ne Gider?* (Eşleşme önerileri)
    - *Kalori Analizi* (Besin değerleri hesaplama)
    - *Alternatif Malzeme* (İçerik değiştirme önerileri)
- **📏 Birim Dönüştürücü:** Cup, Oz, Lb gibi birimleri metrik (Gr, Ml) sisteme çevirir.
- **🚀 Kariyer Desteği:** İş ve staj ilanları için hızlı kapak yazısı (cover letter) taslağı oluşturur.

---

## 🚀 Hızlı Başlangıç

### 1. Hazırlık
Uygulamayı çalıştırmadan önce sisteminizde şunların olduğundan emin olun:
- **Ollama Kurulumu:** [ollama.com](https://ollama.com/) adresinden kurun ve terminalde `ollama run gemma3:1b` komutunu çalıştırın.
- **Python 3.13:** En güncel Python sürümü önerilir.

### 2. Kurulum ve Çalıştırma
Projeyi kendi bilgisayarınıza kurmak için sadece `BASLAT.bat` dosyasını çalıştırmanız yeterlidir.
- `BASLAT.bat` otomatik olarak bir sanal ortam (`.venv`) oluşturur.
- Gerekli tüm kütüphaneleri (`requirements.txt`) yükler.
- `main.pyw` dosyasını arka planda başlatır.

### 3. Gemini API Yapılandırması
Gemini Flash özelliklerini (F9) kullanmak için:
1. `main.pyw` dosyasını açın.
2. `GEMINI_API_KEY` değişkenine [Google AI Studio](https://aistudio.google.com/app/apikey)'dan aldığınız anahtarı ekleyin.

---

## ⌨️ Kullanım Kılavuzu

1. Herhangi bir programda (Tarayıcı, Word, Not Defteri vb.) bir metni fare ile seçin.
2. Yerel AI için **F8**'e, Gemini için **F9**'a basın.
3. Açılan şık menüden istediğiniz işlemi seçin.
4. AI, sonucu hazırlayıp seçtiğiniz metnin yerine otomatik olarak **yapıştıracaktır**.

---

## 📂 Dosya Yapısı

- `main.pyw`: Görsel arayüz (Tkinter) ve klavye dinleyici motoru.
- `kurulum.bat`: Sanal ortam ve paket kurulum otomasyonu.
- `BASLAT.bat`: Uygulamayı tek tıkla başlatan script.
- `requirements.txt`: Proje bağımlılıkları.

---

## 🤝 Katkıda Bulunma

Bu bir ödev/proje çalışmasıdır. Geliştirmek isterseniz lütfen:
1. Projeyi **Fork** edin.
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniozellik`).
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`).
4. Branch'inizi push edin (`git push origin feature/yeniozellik`).
5. Bir **Pull Request** açın.

---

<div align="center">
Geliştiren: <b>Ömer F. AY</b>
</div>
