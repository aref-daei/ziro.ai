# Ziro.ai 🎬

[English](README.md)

**برنامه دسکتاپ هوشمند برای تولید خودکار زیرنویس دوبله‌زبان (انگلیسی و فارسی)**

این برنامه ویدیوهای انگلیسی را با کمک هوش مصنوعی به ویدیوهایی مجهز به زیرنویس انگلیسی و فارسی تبدیل می‌کند.

![Version](https://img.shields.io/badge/version-1.0._rc-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

---

## ✨ قابلیت‌ها

- 🎙️ **تشخیص گفتار به متن** با مدل Whisper
- 🌐 **ترجمه خودکار** به زبان فارسی با مدل‌های Transformers
- 📝 تولید فایل‌های **SRT** انگلیسی و فارسی
- 🎬 افزودن زیرنویس به ویدیو (**Soft-Subtitle**)
- 🖥️ رابط گرافیکی با **CustomTkinter**
- ⚡ پشتیبانی از **CPU** و **GPU**
- 📦 پردازش **چندین ویدیو به صورت Batch**

---

## 📋 پیش‌نیازها

- Python 3.12 یا بالاتر
- ffmpeg
- حداقل 8 گیگابایت RAM (ترجیحاً 16 گیگ)
- **کارت گرافیک با پشتیبانی CUDA برای عملکرد عالی توصیه می‌شود**

---

## 📖 نحوه استفاده

### رابط گرافیکی (GUI)

1. اجرای دستور `python main.py`
2. انتخاب فایل ویدیو
3. تنظیم گزینه‌های مورد نیاز
4. کلیک روی دکمه "Start Processing"

---

## ⚙️ راه‌اندازی آفلاین مدل ترجمه

> ⚠️ **هشدار:** حجم دانلود مدل M2M100 (418 میلیون پارامتر) بیش از **1.4 گیگابایت** است. قبل از شروع دانلود مطمئن شوید فضای کافی و اینترنت پایدار دارید.
> _مدل M2M100 (1.2 میلیارد پارامتر) به بیش از **4.7 گیگابایت**. [بیشتر بدانید](model_sizes.md)_

برای جلوگیری از اتصال به سرورهای HuggingFace و اجرای کاملاً آفلاین:

### 1. دانلود دستی مدل

در ترمینال اجرا کنید:

```
huggingface-cli download facebook/m2m100_418M --local-dir ./models/m2m100 --local-dir-use-symlinks False
```

### 2. غیرفعال‌سازی اتصال آنلاین در کد

```
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
```

### 3. بارگذاری مدل فقط از فایل‌های محلی

```
self.tokenizer = M2M100Tokenizer.from_pretrained("./models/m2m100", local_files_only=True)
self.model = M2M100ForConditionalGeneration.from_pretrained("./models/m2m100", local_files_only=True)
```

---

## 🚀 برنامه‌های آینده

- ترجمه از طریق Google Translate API با کلید امنیتی
- ارتقا رابط کاربری و انتقال به PyQt 6

---

## 📄 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. برای اطلاعات بیشتر فایل [LICENSE](LICENSE) را مشاهده کنید.
