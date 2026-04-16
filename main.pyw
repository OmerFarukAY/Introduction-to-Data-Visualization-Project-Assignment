import pyperclip
from pynput import keyboard
import pyautogui
import tkinter as tk
from tkinter import messagebox
import time
import threading
import requests
import queue

try:
    from google import genai
except ImportError:
    genai = None


# --- AYARLAR ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_ADI = "gemma3:1b"  # Ana model (F8)
TEXT_MODEL_CANDIDATES = [
    MODEL_ADI,
    "gemma3:1b",
]

GEMINI_MODEL = "gemini-3-flash-preview"
GEMINI_API_KEY = "kendi api keyinizi girin"

KISAYOL_METIN = keyboard.Key.f8  # Ollama icin kisayol
KISAYOL_GEMINI = keyboard.Key.f9  # Gemini icin kisayol


# Global değişkenler
root = None
gui_queue = queue.Queue()
kisayol_basildi_key = None


# --- MENÜ SEÇENEKLERİ VE PROMPT'LAR ---
ISLEMLER = {
    "👔 Kurumsala Çevir (Öfke Kontrolü)": (
        "Bu metindeki kaba, duygusal, argo veya sitemkar ifadeleri tamamen temizle. "
        "Yerine son derece profesyonel, kibar, çözüm odaklı ve kurumsal bir e-posta dili yaz. "
        "Sadece çevrilmiş profesyonel metni ver, başka açıklama yapma."
    ),
    "📋 Özetle ve Görevleri Çıkar": (
        "Bu uzun metni dikkatlice oku. Metnin ana fikrini 2 cümleyle özetle. "
        "Ardından, eğer metinde yapılması gereken işler, tarihler veya görev dağılımları varsa "
        "bunları kısa bir 'Yapılacaklar Listesi' (Madde Madde) olarak çıkar."
    ),
    "🚀 Staj/İş Başvurusu Yaz (Cover Letter)": (
        "Bu seçili metin bir iş veya staj ilanıdır. Bu ilana başvurmak isteyen hevesli ve "
        "öğrenmeye açık bir öğrenci ağzından; ilandaki anahtar kelimeleri içeren, "
        "etkileyici ve profesyonel bir ön yazı (cover letter) taslağı oluştur."
    ),
    "🛒 Alışveriş Listesi Çıkar": (
        "Bu metin bir yemek tarifidir. Bu tarifi yapmak için gereken malzemeleri çıkar ve "
        "onları marketteki reyonlara göre (Manav, Süt Ürünleri, Kasap vb.) "
        "gruplandırarak temiz bir alışveriş listesi yap."
    ),
     "🍷 Buna Ne Gider? (Eşleşme Önerici)": (
        "Bu malzemeye veya yemeğe en iyi eşlik edecek diğer malzemeleri, baharatları ve içecek eşleşmelerini öner. "
        "Neden yakıştıklarını kısaca açıkla. Madde madde ve iştah açıcı bir dille yaz."
    ),
    "⚖️ Kalori & Besin Değeri Analizi": (
        "Bu tarifteki malzemelerin miktarlarına göre yaklaşık toplam kalori, protein, karbonhidrat ve yağ değerlerini hesapla. "
        "Eğer miktar belirtilmemişse genel porsiyon üzerinden tahmin yap. Sonucu okunaklı bir tablo veya liste halinde ver."
    ),
    "🔄 Malzeme Değiştirici (Alternatif)": (
        "Bu tarifteki ana malzemelerden biri eksikse veya alerji/tercih nedeniyle değiştirilmek isteniyorsa "
        "yerine ne kullanılabileceğini, bu değişikliğin tadı ve kıvamı nasıl etkileyeceğini anlat."
    ),
    "📏 Birim Dönüştürücü (Metrik)": (
        "Metindeki tüm yabancı ölçü birimlerini (cup, oz, lb, fahrenheit, vb.) metrik sisteme (gram, ml, celsius) çevir. "
        "Sadece güncellenmiş metni ver, açıklama yapma."
    )
}


def get_available_text_model():
    """Metin işlemede kullanılabilir modeli seçer."""
    preferred_models = []
    for model in TEXT_MODEL_CANDIDATES:
        if model and model not in preferred_models:
            preferred_models.append(model)

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            return MODEL_ADI

        models = response.json().get("models", [])
        installed_lower = {m.get("name", "").lower(): m.get("name", "") for m in models}

        for candidate in preferred_models:
            candidate_lower = candidate.lower()
            if candidate_lower in installed_lower:
                return installed_lower[candidate_lower]

            candidate_base = candidate_lower.split(":")[0]
            for installed_name_lower, installed_name in installed_lower.items():
                if installed_name_lower.startswith(candidate_base + ":"):
                    return installed_name
    except Exception:
        pass

    return MODEL_ADI


def ollama_cevap_al(prompt):
    """Ollama API'den cevap al."""
    try:
        aktif_model = get_available_text_model()
        payload = {
            "model": aktif_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            },
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=60)

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()

        err_msg = (
            f"Ollama API Hatası: {response.status_code}\n"
            f"Model: {aktif_model}\n"
            f"Cevap: {response.text}"
        )
        print(f"❌ {err_msg}")
        gui_queue.put((messagebox.showerror, ("API Hatası", err_msg)))
        return None

    except requests.exceptions.ConnectionError:
        err_msg = (
            "Ollama'ya bağlanılamadı.\n"
            "Programın çalıştığından emin olun!\n"
            "(http://localhost:11434)"
        )
        print(f"❌ {err_msg}")
        gui_queue.put((messagebox.showerror, ("Bağlantı Hatası", err_msg)))
        return None
    except Exception as e:
        err_msg = f"Beklenmeyen Hata: {e}"
        print(f"❌ {err_msg}")
        gui_queue.put((messagebox.showerror, ("Hata", err_msg)))
        return None


def gemini_cevap_al(prompt):
    """Gemini AI API'den cevap al."""
    if not genai:
        err_msg = "google-genai kütüphanesi yüklü değil! 'kurulum.bat'ı çalıştırın."
        gui_queue.put((messagebox.showerror, ("Kütüphane Hatası", err_msg)))
        return None

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        err_msg = (
            f"Gemini API Hatası: {e}\n\n"
            "Not: 'gcloud auth application-default login' yaptığınızdan emin olun."
        )
        print(f"❌ {err_msg}")
        gui_queue.put((messagebox.showerror, ("Gemini Hatası", err_msg)))
        return None


def strip_code_fence(text):
    if not text:
        return text
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:] if lines else []
        while lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def secili_metni_kopyala(max_deneme=4):
    sentinel = f"__AI_ASISTAN__{time.time_ns()}__"
    try:
        pyperclip.copy(sentinel)
    except Exception:
        pass

    for _ in range(max_deneme):
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.2)
        metin = pyperclip.paste()
        if metin and metin.strip() and metin != sentinel:
            return metin
    return ""


def pencere_modunda_gosterilsin_mi(komut_adi):
    return "PS5 Oyun Skor" in komut_adi


def sonuc_penceresi_goster(baslik, icerik):
    pencere = tk.Toplevel(root)
    pencere.title(baslik)
    pencere.geometry("780x520")
    pencere.minsize(520, 320)
    pencere.attributes("-topmost", True)

    frame = tk.Frame(pencere, bg="#1f1f1f")
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    text_alani = tk.Text(
        frame,
        wrap="word",
        bg="#2b2b2b",
        fg="white",
        insertbackground="white",
        font=("Segoe UI", 10),
        padx=10,
        pady=10,
    )
    kaydirma = tk.Scrollbar(frame, command=text_alani.yview)
    text_alani.configure(yscrollcommand=kaydirma.set)

    text_alani.pack(side="left", fill="both", expand=True)
    kaydirma.pack(side="right", fill="y")

    text_alani.insert("1.0", icerik)
    text_alani.config(state="disabled")

    alt_frame = tk.Frame(pencere, bg="#1f1f1f")
    alt_frame.pack(fill="x", padx=10, pady=(0, 10))

    def panoya_kopyala():
        pyperclip.copy(icerik)

    tk.Button(
        alt_frame,
        text="Panoya Kopyala",
        command=panoya_kopyala,
        bg="#3d3d3d",
        fg="white",
        activebackground="#4d4d4d",
        activeforeground="white",
        relief="flat",
        padx=12,
        pady=6,
    ).pack(side="left")

    tk.Button(
        alt_frame,
        text="Kapat",
        command=pencere.destroy,
        bg="#3d3d3d",
        fg="white",
        activebackground="#4d4d4d",
        activeforeground="white",
        relief="flat",
        padx=12,
        pady=6,
    ).pack(side="right")

    pencere.focus_force()
    pencere.lift()


def islemi_yap(komut_adi, secili_metin, engine="ollama"):
    prompt_emri = ISLEMLER[komut_adi]
    full_prompt = f"{prompt_emri}:\n\n'{secili_metin}'"

    print(f"🤖 İşlem: {komut_adi} ({engine})")
    print(f"⏳ {engine.capitalize()} ile işleniyor...")

    if engine == "gemini":
        sonuc = gemini_cevap_al(full_prompt)
    else:
        sonuc = ollama_cevap_al(full_prompt)

    if not sonuc:
        print("❌ Sonuç alınamadı.")
        return

    sonuc = strip_code_fence(sonuc)
    if sonuc.startswith("'") and sonuc.endswith("'"):
        sonuc = sonuc[1:-1]

    if pencere_modunda_gosterilsin_mi(komut_adi):
        gui_queue.put((sonuc_penceresi_goster, (komut_adi, sonuc)))
        print("âœ… SonuÃ§ ayrÄ± pencerede gÃ¶sterildi.")
        return

    time.sleep(0.2)
    pyperclip.copy(sonuc)
    time.sleep(0.1)
    pyautogui.hotkey("ctrl", "v")
    print("✅ İşlem tamamlandı!")


def process_queue():
    """Kuyruktaki GUI işlemlerini ana thread'de çalıştırır."""
    try:
        while True:
            try:
                task = gui_queue.get_nowait()
            except queue.Empty:
                break
            func, args = task
            func(*args)
    finally:
        if root:
            root.after(100, process_queue)


def menu_goster(engine="ollama"):
    """Metni kopyalar ve menüyü gösterir (ana thread)."""
    secili_metin = secili_metni_kopyala()
    if not secili_metin.strip():
        gui_queue.put(
            (
                messagebox.showwarning,
                (
                    "Secim Bulunamadi",
                    "Lutfen once metin secin, sonra F8 ile menuyu acin.",
                ),
            )
        )
        return

    menu = tk.Menu(
        root,
        tearoff=0,
        bg="#2b2b2b",
        fg="white",
        activebackground="#4a4a4a",
        activeforeground="white",
        font=("Segoe UI", 10),
    )

    def komut_olustur(k_adi, s_metin, eng):
        def komut_calistir():
            threading.Thread(
                target=islemi_yap, args=(k_adi, s_metin, eng), daemon=True
            ).start()

        return komut_calistir

    for baslik in ISLEMLER.keys():
        menu.add_command(
            label=baslik, command=komut_olustur(baslik, secili_metin, engine)
        )

    menu.add_separator()
    menu.add_command(label="❌ İptal", command=lambda: None)

    try:
        x, y = pyautogui.position()
        menu.tk_popup(x, y)
    finally:
        menu.grab_release()


def on_press(key):
    global kisayol_basildi_key
    try:
        if (key == KISAYOL_METIN or key == KISAYOL_GEMINI) and kisayol_basildi_key is None:
            kisayol_basildi_key = key
            engine = "gemini" if key == KISAYOL_GEMINI else "ollama"
            gui_queue.put((menu_goster, (engine,)))
    except AttributeError:
        pass


def on_release(key):
    global kisayol_basildi_key
    try:
        if key == KISAYOL_METIN or key == KISAYOL_GEMINI:
            kisayol_basildi_key = None
    except AttributeError:
        pass


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI Asistan - Metin İşleme")
    print("=" * 60)
    aktif_text_model = get_available_text_model()
    print(f"📦 Yerel Model (F8): {aktif_text_model}")
    print(f"☁️ Gemini Model (F9): {GEMINI_MODEL}")
    print()
    print("🔧 Kullanım:")
    print("   F8 - Metin seç ve Yerel AI işlemleri yap")
    print("   F9 - Metin seç ve Gemini 3 Flash işlemleri yap")
    print()
    print("⚠️ Programı kapatmak için bu pencereyi kapatın veya Ctrl+C yapın.")
    print("=" * 60)

    try:
        test_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if test_response.status_code == 200:
            print("✅ Ollama bağlantısı başarılı!")
        else:
            print("⚠️ Ollama'ya bağlanılamadı, servisi kontrol edin!")
    except Exception:
        print("⚠️ Ollama çalışmıyor olabilir! 'ollama serve' ile başlatın.")

    print()

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    root = tk.Tk()
    root.withdraw()
    root.after(100, process_queue)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Kapatılıyor...")
