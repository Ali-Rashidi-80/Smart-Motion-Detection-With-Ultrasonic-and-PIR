#https://wokwi.com/projects/406211763057438721

"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                         Raspberry Pi Pico (MicroPython)                                                  |
┃                                                                                                          |
┃  این پروژه یک سیستم امنیتی است که برای تشخیص نفوذ با استفاده از یک سنسور فاصله‌سنج اولتراسونیک و یک سنسور حرکتی PIR (مادون قرمز غیرفعال) طراحی شده است. اگر جسمی در محدوده مشخصی از فاصله تشخیص داده شود و حرکتی توسط سنسور PIR شناسایی شود، سیستم با فعال کردن یک رله و به صدا درآوردن بوق هشدار می‌دهد. این سیستم به گونه‌ای طراحی شده است که به سرعت واکنش نشان داده و هشدارهای دیداری و شنیداری را هنگام شناسایی نفوذگر ارائه دهد.                                                          
┃  This project is a security system designed to detect intruders using an ultrasonic distance sensor and a PIR (Passive Infrared) motion sensor. If an object is detected within a specific distance range and movement is detected by the PIR sensor, the system triggers a relay and sounds an alarm using a buzzer. The system is designed to be responsive and provide visual and auditory alerts when an intruder is detected.                                                                                                        
┃                                                                                                          |
┃ Copyright (c) 2024 Ali Rashidi                                                                           |
┃ GitHub: github.com/Ali-Rashidi-80                                                                        |
┃ License: only by ME                                                                                      |
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

from machine import Pin, PWM
from time import sleep, sleep_us, ticks_us, ticks_diff

# تنظیمات پین‌ها
trig_pin = Pin(28, Pin.OUT)         # پین تریگر سنسور اولتراسونیک (برای ارسال پالس)
echo_pin = Pin(27, Pin.IN)          # پین اکو سنسور اولتراسونیک (برای دریافت پالس بازگشتی)
PIR_pin = Pin(26, Pin.IN, Pin.PULL_DOWN)  # پین PIR برای تشخیص حرکت (با Pull-Down داخلی)
Relay_pin = Pin(22, Pin.OUT)        # پین رله برای فعال و غیرفعال کردن بار
Buzzer_pin = PWM(Pin(21))           # پین بیزر برای تولید صدا با PWM
Buzzer_pin.freq(3000)               # تنظیم فرکانس بیزر به 3000 هرتز
Buzzer_pin.duty_u16(0)              # تنظیم دیوتی سایکل بیزر به 0 (خاموش)

def measuring_distance():
    # ارسال پالس تریگر برای سنجش فاصله
    trig_pin.off()
    sleep_us(2)  # زمان کمی برای خاموش بودن تریگر
    trig_pin.on()
    sleep_us(10) # ارسال پالس 10 میکروثانیه‌ای
    trig_pin.off()
    
    # اندازه‌گیری زمان پالس اکو
    while echo_pin.value() == 0:
        start_time = ticks_us()  # زمان شروع پالس بازگشتی
    while echo_pin.value() == 1:
        end_time = ticks_us()    # زمان پایان پالس بازگشتی

    # محاسبه مدت زمان پالس و تبدیل به فاصله (سانتی‌متر)
    duration = ticks_diff(end_time, start_time)
    distance_cm = (duration * 0.0343) / 2  # تبدیل زمان به فاصله
    return distance_cm

def detect_with_ultrasonic_and_pir():
    distance = measuring_distance()  # اندازه‌گیری فاصله
    min_distance = 2                 # حداقل فاصله برای فعال‌سازی سیستم
    max_distance = 100               # حداکثر فاصله برای فعال‌سازی سیستم
    flag = False

    # بررسی فاصله برای اینکه آیا در محدوده مورد نظر است یا خیر
    if distance > max_distance:
        print(f"No detection because distance {distance:.2f} cm > {max_distance} cm")
        return

    if min_distance <= distance <= max_distance:
        if PIR_pin.value() == 1:   # بررسی وضعیت سنسور PIR
            flag = True
        else:
            flag = False

    # اگر تشخیص واقعی است، رله و بیزر فعال می‌شود
    if flag:
        print("Real detection!")
        for _ in range(20):  # تکرار برای فعال و غیرفعال کردن رله و بیزر
            Relay_pin.on()  # فعال کردن رله
            Buzzer_pin.duty_u16(30000)  # فعال کردن بیزر با دیوتی سایکل بالا
            sleep(0.1)    # مدت زمان روشن بودن بیزر
            Relay_pin.off()  # غیرفعال کردن رله
            Buzzer_pin.duty_u16(0)  # خاموش کردن بیزر
            sleep(0.2)    # مدت زمان خاموش بودن بیزر

    else:
        print("Unexpected motion detected")
        # افزایش تدریجی شدت بیزر
        for duty in range(0, 65535, 5000):  
            Buzzer_pin.duty_u16(duty)  # افزایش دیوتی سایکل بیزر
            sleep(0.01)   # مدت زمان برای تغییر تدریجی

        # کاهش تدریجی شدت بیزر
        for duty in range(65535, 0, -5000):  
            Buzzer_pin.duty_u16(duty)  # کاهش دیوتی سایکل بیزر
            sleep(0.05)   # مدت زمان برای تغییر تدریجی

        Buzzer_pin.duty_u16(0)  # خاموش کردن بیزر

# حلقه اصلی برای اجرای تابع تشخیص به طور مداوم
while True:
    detect_with_ultrasonic_and_pir()  # فراخوانی تابع تشخیص
    sleep(0.1)  # تأخیر کوتاه برای جلوگیری از اجرای سریع برنامه
