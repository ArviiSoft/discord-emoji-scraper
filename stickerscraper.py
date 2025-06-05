#!/usr/bin/env python
import os, time
import re, requests
from apnggif import apnggif
import platform

yasal_uyari = '''
UYARI! Bu Toolu kullanmak, Disord Web Scraping yapacağı için TOS kurallarını ihlal eder.

Discord'un TOS kurallarını ihlal etmek, hesabının askıya alınmasına veya yasaklanmasına neden olabilir.
Bu Tool, Discord'un TOS kurallarını ihlal etmemek için yalnızca kendi sunucularında emoji indirmeni sağlar.

İşleme devam ederek bu Toolun hesabına karşı veya yasal olarak sana karşı yapılan herhangi bir işlemden sorumlu olmadığını kabul edersin.

Bu Toolu yan hesabınla kullanmanı tavsiye ederim.
Bu Tool ile birlikte Tor, VPN veya Proxy kullanmanı tavsiye ederim.

Lütfen bu Toolu kullanırken dikkatli ol ve sorumluluğunu kabul et.

Scraping işlemine başlamak için "ANLADIM" yaz ve enterla.
'''

bilgilendirme = '''
arviis. (ArviS)

Eğer herhangi bir hata ile karşılaşırsan, sormak istediğin bir şeyler varsa https://discord.gg/uzPUNrrhH2 sunucusuna gelebilirsin.
'''

def is_none_empty_whitespace(any_string):
    if any_string == None:
        return True
    if any_string.strip(" ") == "":
        return True
    return False

def get_list_of_stickers(guild_id, token):
    result=requests.get(url=f"https://discordapp.com/api/v9/guilds/{guild_id}/stickers", headers={"authorization":token})
    return result.json()

def scrape_sticker(id, proxy=None):
    if is_none_empty_whitespace(proxy):
        result=requests.get(url=f"https://media.discordapp.net/stickers/{id}")
        return result.content

def get_guild_name(guild_id, token):
    result=requests.get(url=f"https://discordapp.com/api/v7/guilds/{guild_id}", headers={"authorization":token})
    if platform.system() == "Windows":
        return re.sub(r"[<>:\"/\\|?*]", '-', result.json().get("name"))
    else:
        return result.json().get("name")  

def save(img_bytes, path):
    imagefile = open(path, 'wb')
    imagefile.write(img_bytes)
    imagefile.close()

def make_server_dir(server, config):
    dir_path = os.path.join(config.get("path"), server)
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

def is_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

def try_scraping(guild_name, sticker):
    id = sticker.get("id")
    name = sticker.get("name")
    print(f"{guild_name} sunucusundan '{name}' çıkartması indirilmeye çalışılıyor...")
    sticker_bytes = None
    while True:
        try:
            sticker_bytes = scrape_sticker(id)
        except Exception as exception:
            if exception == KeyboardInterrupt or exception == SystemExit:
                print("KeyboardInterrupt/SystemExit yakalandı. Çıkış yapılıyor...")
                raise
            else:
                print(f"{guild_name} sunucusundan '{name}' çıkartması indirilemedi, yeniden deniyor...")
        else:
            print(f"{guild_name} sunucusundan '{name}' çıkartması indirildi.")
            break
    return sticker_bytes

def scrape(config):
    if not os.path.isdir(config.get("path")):
        os.mkdir(config.get("path"))
    servers = config.get("guilds")
    for server in servers:
        stickers = get_list_of_stickers(server, config.get("token"))
        guild_name = get_guild_name(server, config.get("token"))
        if guild_name == None or stickers == None:
            print(f"{server} sunucusu hiç yok veya yanlış. Çıkartmalar getirilemiyor.")
            continue
        cooldownsec = config.get("cooldownsec")
        make_server_dir(guild_name, config)
        count = 0
        print(f"{guild_name} sunucusundan çıkartma indirme işlemi başlatılıyor...")
        for sticker in stickers:
            if (not config.get("cooldownpersticker") <= 0) & (count >= config.get("cooldownpersticker")):
                print(f"\nCooldown süresi doldu. {cooldownsec} saniye bekleniyor.")
                time.sleep(cooldownsec)
                count = 0
                print("Cooldowndan devam ediliyor...\n")
            sticker_bytes = try_scraping(guild_name, sticker)
            if sticker.get("format_type") == 1:
                save(sticker_bytes, os.path.join(config.get("path"), guild_name, (sticker.get("name") + ".png")))
            else:
                if config.get("convertapngtogif"):
                    pathorigin = os.path.join(config.get("path"), guild_name, (sticker.get("name") + "_original.apng"))
                    pathconv = os.path.join(config.get("path"), guild_name, (sticker.get("name") + ".gif"))
                    stickername = sticker.get("name")
                    save(sticker_bytes, pathorigin)
                    apnggif(pathorigin, pathconv)
                    print(f"'{stickername}' adlı animasyonlu çıkartma {guild_name}'den dönüştürüldü.")
                else:
                    save(sticker_bytes, os.path.join(config.get("path"), guild_name, (sticker.get("name") + ".apng")))
            count += 1
        print(f"{guild_name} sunucusundan çıkartma indirme işlemi tamamlandı.")

def main():
    print(bilgilendirme)
    while True:
        config = {"token":"", "guilds":[], "path":os.getcwd()+"/Stickers", "cooldownsec":0, "cooldownpersticker":0, "convertapngtogif":False}
        config["token"] = input("Hesap Tokenini Gir ( https://discord.gg/uzPUNrrhH2 ) \n> ")

        while True:
            id = input("Çıkartmalarını almak istediğin sunucunun ID'sini gir. (Tamamlandığında sadece enter tuşuna bas) \n> ")
            if is_none_empty_whitespace(id): break
            elif not is_int(id): print("Geçersiz sunucu ID'si.")
            else: config["guilds"].append(id)

        file_path = input("Çıkartmalarını nereye kaydetmek istersin? (Geçerli dizini kullanmak için enter tuşuna bas) \n> ")
        if not is_none_empty_whitespace(file_path):
            config["path"] = file_path

        cooldownpersticker = input("Her çıkartma için Cooldown süresi gir. (Devam etmek için hiçbir şey yazma veya 0 gir) \n> ")
        if (is_int(cooldownpersticker)): config["cooldownpersticker"] = int(cooldownpersticker)

        if config["cooldownpersticker"] != 0:
            cooldownsec = input("Cooldown süresini SANİYE cinsinden gir. \n> ")
            if (not is_none_empty_whitespace(cooldownsec)) & (not is_int(cooldownsec)): break
            else: config["cooldownsec"] = int(cooldownsec)

        convertapngtogif = input("APNG dosyalarını (animasyonlu çıkartmalar) GIF'e dönüştürmek ister misin? Devam etmek için hiçbir şey yazma veya 0 gir. \n> ")
        if not is_none_empty_whitespace(convertapngtogif):
            config["convertapngtogif"] = True

        print("\n")
        print(config)
        if is_none_empty_whitespace(input("Bu ayarlar doğru mu? (Devam etmek için enter tuşuna bas. İptal etmek için başka bir şey yaz) \n> ")):
            if input(yasal_uyari) == "ANLADIM":
                scrape(config)
                print("ArviS Sticker Scraper'ı kullandığın için teşekkür ederim. Dosyanı şu konumda bulabilirsin: " + config["path"])
                break
            print("Doğrulama başarısız oldu.")

main()
