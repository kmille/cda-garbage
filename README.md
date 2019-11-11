# cda-garbage
This code notifies hackspace member on day $x via IRC (that they should put the garbage bin outside) if the garbage is fetched on day $x+1. EAD is responsible for fetching the garbage in Darmstadt. They provide an email notification service.

# How does it work
1. Register on https://www.muellmax.de/abfallkalender/ead/res/EadStart.php?login and add your street
2. Now you will get a mail the day before the collection of the garbage
3. The script fetches the last 5 emails (imap) and checks the subject
4. Via regex we will get something like this: Freitag, 02.08.2019 Wertstoffe
5. On 01.08.2019 (the day before collection) we will write a message to notify the space member


# Setup
```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
mv settings.yaml.template settings.yaml
adjust settings.yaml
python garbage-anounce.py
```


# Settings
Check settings.yaml.template. Via daily_jobs you can specify when the emails


# Sample E-Mail
```
Guten Tag Frau ok,
wir erinnern Sie an die Termine der Müllabfuhr.


64283 Darmstadt - Innenstadt, Wilhelminenstraße 1-35, 2-10
- Freitag, 02.08.2019 Wertstoffe


Diese Erinnerungsmail wurde am Donnerstag, 01.08.2019 - 06:00:01 versendet.
Entsprechend der Auswahl in Ihrem Infomail Eintrag erfolgt der Versand mit
Option 1: am Tag vor der Abfuhr (Standard).
```

# Register account on IRC
1. go to https://webirc.hackint.org/
2. use the username you want to use
3. /msg NickServ REGISTER yourpassword yourmail@adomain.de
4. You will get a mail with a command like this: /msg NickServ VERIFY REGISTER cda-garbage somesecret
5. Now if someone uses your nick you can kick him with: /msg NickServer GHOST <your username> <yourrpassword>. Then /nick <your username> to switch.
