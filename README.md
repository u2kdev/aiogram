# Telegram-bot: Vakansiyalarni boshqarish tizimi

Ushbu loyiha xorijiy mamlakatlardagi ish o‘rinlarini e’lon qilish, foydalanuvchilarni ro‘yxatdan o‘tkazish va ma’murlar tomonidan boshqarish uchun mo‘ljallangan Telegram-bot hisoblanadi. Bot ma’muriy panel va foydalanuvchi arizalari tizimi bilan ta’minlangan.

## 1. Imkoniyatlar

### Foydalanuvchilar uchun:
- Kontakt orqali ro‘yxatdan o‘tish
- Mamlakatlar bo‘yicha vakansiyalarni ko‘rish
- Vakansiya haqida batafsil ma’lumot olish
- Vakansiyaga ariza yuborish (ma’murlarga xabar)
- Kompaniya haqida ma’lumot olish

### Administratorlar uchun:
- Mamlakat qo‘shish yoki o‘chirish
- Vakansiya qo‘shish yoki o‘chirish
- Foydalanuvchilarni Excel formatida eksport qilish
- Ma’muriy harakatlar logini ko‘rish
- Vakansiyalar bo‘yicha kelgan arizalarni ko‘rish

## 2. O‘rnatish bo‘yicha ko‘rsatmalar
```bash
mkdir vacancy_bot
cd vacancy_bot
pip install -r requirements.txt
```
`config.py` faylini tahrirlang:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_IDS = [123456789]
```
`photo.jpg` faylini loyiha papkasiga joylashtiring (ixtiyoriy).

Botni ishga tushirish:
```bash
python main.py
```

## 3. Loyihaning tuzilmasi
```
vacancy_bot/
├── main.py
├── config.py
├── requirements.txt
├── photo.jpg
├── data.json
├── vacancies.json
├── admin_log.txt
├── applications_log.txt
└── users.xlsx
```

## 4. Foydalanish bo‘yicha ma’lumot
### Asosiy buyruqlar
- `/start` – botni ishga tushirish
- `/data` – foydalanuvchilarni Excel formatida yuklab olish (admin)
- `/log` – ma’muriy loglarni olish
- `/applog` – vakansiyalarga yuborilgan arizalar logini olish
- `/stats` – statistika

### Vakansiyalar bilan ishlash
1. "Vakansiyalar" bo‘limiga o‘ting  
2. Agar kerak bo‘lsa, yangi mamlakat qo‘shing  
3. Mamlakat nomini kiriting (masalan, "AQSH")  
4. "Vakansiya qo‘shish"ni tanlang  
5. Vakansiya nomini kiriting (masalan, "Haydovchi")  
6. Tavsifni kiriting  
O‘chirish uchun tegishli "Mamlakatni o‘chirish" yoki "Vakansiyani o‘chirish" tugmasini bosing.

## 5. Ma’lumotlar formati
**data.json**
```json
{
  "users": [
    {
      "id": 123456789,
      "username": "username",
      "name": "Ism Familiya",
      "phone": "+998901234567",
      "registered_at": "2025-01-15T10:30:00"
    }
  ]
}
```
**vacancies.json**
```json
{
  "countries": {
    "AQSH": {
      "jobs": {
        "Haydovchi": {
          "description": "Haydovchi toifasi C talab qilinadi...",
          "created_by": 123456789,
          "date": "2025-01-15 10:30:00"
        }
      }
    }
  }
}
```

## 6. Tavsiyalar
1. `data.json` va `vacancies.json` fayllarining zaxira nusxasini muntazam saqlang  
2. Qisqa va aniq nomlardan foydalaning  
3. `photo.jpg` o‘lchami ~800x600 px bo‘lishi kerak  
4. Log fayllarini (`/log`, `/applog`) vaqti-vaqti bilan tekshirib turing

## 7. Muammolarni bartaraf etish
- Administrator funksiyalari ishlamasa, `ADMIN_IDS` ichida o‘zingizning ID raqamingiz borligiga ishonch hosil qiling  
- ID raqamini olish uchun [@userinfobot](https://t.me/userinfobot) dan foydalaning  
- Excel eksportida xatolik yuz bersa:
```bash
pip install openpyxl pandas
```
- `photo.jpg` chiqmasa, fayl nomi va formatini tekshiring

## 8. Litsenziya
Lexore Cloud N0003.

## 9. Muallif
Lexore Cloud, 2025–2026 yillar.

## 10. Versiya
- Versiya: 2.3 (tuzatilgan)  
- Sana: 2025-10-10  
- Python: 3.8+

---

# Telegram-бот для управления вакансиями

Профессиональный бот для публикации зарубежных вакансий, управления пользователями и обработки откликов. Включает админ-панель и систему логирования.

## 1. Возможности
### Для пользователей:
- Регистрация через контакт
- Просмотр вакансий по странам
- Детальная информация по каждой вакансии
- Отклик на вакансию (заявка администраторам)
- Просмотр информации о компании

### Для администраторов:
- Добавление и удаление стран
- Добавление и удаление вакансий
- Экспорт пользователей в Excel
- Просмотр административных логов
- Просмотр откликов пользователей

## 2. Установка
```bash
mkdir vacancy_bot
cd vacancy_bot
pip install -r requirements.txt
```
Откройте `config.py` и укажите:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_IDS = [123456789]
```
Добавьте `photo.jpg` в директорию проекта (опционально).  
Запуск:
```bash
python main.py
```

## 3. Структура проекта
```
vacancy_bot/
├── main.py
├── config.py
├── requirements.txt
├── photo.jpg
├── data.json
├── vacancies.json
├── admin_log.txt
├── applications_log.txt
└── users.xlsx
```

## 4. Использование
### Основные команды
- `/start` – запуск бота  
- `/data` – экспорт пользователей (только для администраторов)  
- `/log` – лог действий администраторов  
- `/applog` – лог откликов  
- `/stats` – статистика бота  

### Работа с вакансиями
1. Перейдите в раздел «Вакансии»  
2. Добавьте страну при необходимости  
3. Введите название страны (например, "США")  
4. Выберите «Добавить вакансию»  
5. Укажите название и описание вакансии  
Удаление выполняется кнопками «Удалить страну» или «Удалить вакансию».

## 5. Формат данных
**data.json**
```json
{
  "users": [
    {
      "id": 123456789,
      "username": "username",
      "name": "Имя Фамилия",
      "phone": "+998901234567",
      "registered_at": "2025-01-15T10:30:00"
    }
  ]
}
```
**vacancies.json**
```json
{
  "countries": {
    "США": {
      "jobs": {
        "Водитель": {
          "description": "Требуется водитель категории C...",
          "created_by": 123456789,
          "date": "2025-01-15 10:30:00"
        }
      }
    }
  }
}
```

## 6. Рекомендации
1. Регулярно создавайте резервные копии `data.json` и `vacancies.json`  
2. Используйте короткие и понятные названия  
3. Рекомендуемый размер изображения меню — 800×600 px  
4. Проверяйте логи `/log` и `/applog`

## 7. Устранение ошибок
- Проверьте, что ваш ID добавлен в `ADMIN_IDS`  
- Узнайте ID через [@userinfobot](https://t.me/userinfobot)  
- При ошибке Excel-экспорта:
```bash
pip install openpyxl pandas
```
- Если изображение меню не отображается, проверьте файл `photo.jpg`

## 8. Лицензия
Lexore Cloud N0003.

## 9. Автор
Lexore Cloud, 2025–2026.

## 10. Версия
- Версия: 2.3 (исправленная)  
- Дата: 2025-10-10  
- Python: 3.8+
