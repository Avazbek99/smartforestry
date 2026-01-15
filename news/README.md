# Yangiliklar Sayti

Flask da yozilgan ko'p foydalanuvchili yangiliklar sayti. SuperAdmin va Admin rollari bilan ishlaydi.

## Xususiyatlari

- **SuperAdmin**: Hududlar yaratishi, adminlar biriktirishi, barcha yangiliklarni boshqarishi
- **Admin**: Faqat o'z hududi uchun yangiliklar qo'shishi, o'zi yozganlarni tahrirlashi/o'chirishi
- **Ommaviy sahifa**: Barcha yangiliklarni ko'rish imkoniyati
- **Zamonaviy UI**: Bootstrap 5 bilan chiroyli interfeys

## O'rnatish

1. Python 3.7+ o'rnatilgan bo'lishi kerak
2. Kerakli paketlarni o'rnatish:
```bash
pip install -r requirements.txt
```

## Ishga tushirish

```bash
python app.py
```

Dastlabki ishga tushirishda avtomatik ravishda SuperAdmin yaratiladi:
- **Login**: `superadmin`
- **Parol**: `admin123`

## URL Strukturasi

- Asosiy sahifa: `http://localhost:5000/`
- SuperAdmin login: `http://localhost:5000/admin/login`
- SuperAdmin panel: `http://localhost:5000/admin/dashboard`
- Admin login: `http://localhost:5000/{hudud_slug}/login`
- Admin panel: `http://localhost:5000/{hudud_slug}/dashboard`

## Foydalanish

### SuperAdmin uchun:

1. `http://localhost:5000/admin/login` ga kirib, login: `superadmin`, parol: `admin123`
2. Panel orqali hududlar qo'shing (masalan: Toshkent, Samarqand)
3. Har bir hudud uchun adminlar yarating va ularga parol belgilang
4. Adminlar o'z hududlariga kirib yangiliklar qo'shishi mumkin

### Admin uchun:

1. SuperAdmin tomonidan berilgan hudud URLiga kiring (masalan: `http://localhost:5000/toshkent/login`)
2. Login va parol bilan kiring
3. O'z hududingiz uchun yangiliklar qo'shing
4. Faqat o'zingiz yozgan yangiliklarni tahrirlashingiz mumkin

## Ma'lumotlar bazasi

SQLite ma'lumotlar bazasi ishlatiladi. `news.db` fayli avtomatik yaratiladi.

## Xavfsizlik

- Parollar xeshlab saqlanadi
- Session asosida autentifikatsiya
- Adminlar faqat o'z yangiliklarini tahrirlay oladi

## Rivojlantirish

- `app.py` - asosiy Flask ilovasi
- `templates/` - HTML shablonlar
- `requirements.txt` - Python paketlari
