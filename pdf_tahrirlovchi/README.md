# PDF Tahrirlovchi

PDF fayllarida so'z topish, almashtirish va o'chirish uchun Streamlit ilovasi.

## O'rnatish

```bash
pip install -r requirements.txt
```

## Ishga tushirish

```bash
streamlit run app.py
```

Brauzer avtomatik ochiladi. Agar ochilmasa, `http://localhost:8501` manziliga o'ting.

## Foydalanish

1. PDF faylni yuklang (drag & drop yoki fayl tanlash).
2. Matn sahifalar bo'yicha ko'rsatiladi.
3. "Topish va almashtirish" bo'limida so'zlarni kiriting:
   - Topish maydoniga almashtirilishi kerak bo'lgan so'zni yozing.
   - Almashtirish maydoniga yangi so'zni yozing (bo'sh qoldirsangiz, so'z o'chiriladi).
4. Bir nechta juftlik qo'shish mumkin.
5. Sozlamalar: katta-kichik harf farqi va faqat butun so'z.
6. "O'zgarishlarni qo'llash" tugmasini bosing.
7. Natijani PDF, Word, Markdown yoki TXT formatida yuklab oling.

## Modullar

- `app.py` - Streamlit UI
- `pdf_engine.py` - PDF o'qish, topish va almashtirish (PyMuPDF)
- `exporters.py` - Eksport funksiyalari (PDF, Word, Markdown, TXT)
