@echo off

cd /d "D:\python AIML\AI_HELTH_ASSISTANT"

call "D:\python AIML\AI_HELTH_ASSISTANT\sebin\Scripts\activate.bat"

python manage.py send_medicine_reminders

pause