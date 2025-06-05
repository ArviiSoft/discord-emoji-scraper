import os, time
import re, requests
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

def get_list_of_emojis(guild_id, token):
    result=requests.get(url=f"https://discordapp.com/api/v7/guilds/{guild_id}/emojis", headers={"authorization":token})
    return result.json()

def scrape_emoji(id, proxy=None):
    if is_none_empty_whitespace(proxy):
        result=requests.get(url=f"https://cdn.discordapp.com/emojis/{id}")
        return result.content

def get_guild_name(guild_id, token):
    result=requests.get(url=f"https://discordapp.com/api/v7/guilds/{guild_id}", headers={"authorization":token})
    if platform.system() == "Windows":
        return re.sub(r"[<>:\"/\\|?*]", '-', result.json().get("name"))
    else:
        return result.json().get("name")  

def get_image_file_extension_from_bytes(image_bytes):
    if str(image_bytes)[0:7].find("PNG") != -1:
        return ".png"
    if str(image_bytes)[0:7].find("GIF") != -1:
        return ".gif"
    return ".png"

def save(img_bytes, path):
    imagefile = open(path, 'wb')
    imagefile.write(img_bytes)
    imagefile.close()

def make_server_dir(server, config):
    dir_path = os.path.join(config.get("path"), server)
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

def try_scraping(guild_name, emoji):
    id = emoji.get("id")
    name = emoji.get("name")
    print(f"{guild_name} sunucusundan :{name}: ({id}) emojisi indirilmeye çalışılıyor...")
    emoji_bytes = None
    while True:
        try:
            emoji_bytes = scrape_emoji(id)
        except Exception as exception:
            if exception == KeyboardInterrupt or exception == SystemExit:
                print("KeyboardInterrupt/SystemExit yakalandı. Çıkış yapılıyor...")
                raise
            else:
                print(f"{guild_name} sunucusundan :{name}: ({id}) emojisi indirilemedi, yeniden deniyor.")
        else:
            print(f"{guild_name} sunucusundan :{name}: ({id}) emojisi indirildi.")
            break
    return emoji_bytes
    
def is_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

def scrape(config):
    if not os.path.isdir(config.get("path")):
        os.mkdir(config.get("path"))
    servers = config.get("guilds")
    for server in servers:
        emojis = get_list_of_emojis(server, config.get("token"))
        guild_name = get_guild_name(server, config.get("token"))
        if guild_name == None or emojis == None:
            print(f"{server} sunucusu hiç yok veya yanlış. Emojiler getirilemiyor.")
            continue
        cooldownsec = config.get("cooldownsec")
        make_server_dir(guild_name, config) 
        count = 0
        print(f"{guild_name} sunucusundan emoji indirme işlemi başlatılıyor...")
        for emoji in emojis:
            if (not config.get("cooldownperemoji") <= 0) & (count >= config.get("cooldownperemoji")):
                print(f"\nCooldown süresi doldu. {cooldownsec} saniye bekleniyor.")
                time.sleep(cooldownsec)
                count = 0
                print("Cooldowndan devam ediliyor...\n")
            emoji_bytes = try_scraping(guild_name, emoji)
            save(emoji_bytes, os.path.join(config.get("path"), guild_name, (emoji.get("name") + get_image_file_extension_from_bytes(emoji_bytes))))
            count += 1
        print(f"{guild_name} sunucusundan emoji indirme işlemi tamamlandı.")

def main():
    print(bilgilendirme)
    while True:
        config = {"token":"", "guilds":[], "path":os.getcwd()+"/Emojis", "cooldownsec":0, "cooldownperemoji":0}
        config["token"] = input("Hesap Tokenini Gir ( https://discord.gg/uzPUNrrhH2 ) \n> ")

        while True:
            id = input("Sunucu ID'si Gir ( https://discord.gg/uzPUNrrhH2 ) \n> ")
            if is_none_empty_whitespace(id): break
            elif not is_int(id): print("Geçersiz sunucu ID'si.")
            else: config["guilds"].append(id)

        file_path = input("Emojilerini nereye kaydetmek istersin? (Geçerli dizini kullanmak için enter tuşuna bas) \n> ")
        if not is_none_empty_whitespace(file_path):
            config["path"] = file_path

        cooldownperemoji = input("Her emoji için Cooldown süresi gir. (Devam etmek için hiçbir şey yazma veya 0 gir) \n> ")
        if (is_int(cooldownperemoji)): config["cooldownperemoji"] = int(cooldownperemoji)

        if config["cooldownperemoji"] != 0:
            cooldownsec = input("Cooldown süresini SANİYE cinsinden gir. \n>")
            if (not is_none_empty_whitespace(cooldownsec)) & (not is_int(cooldownsec)): break
            else: config["cooldownsec"] = int(cooldownsec)

        print("\n")
        print(config)
        if is_none_empty_whitespace(input("Ayarların doğru mu? (Devam etmek için enter tuşuna bas. İptal etmek için başka bir şey yaz) \n> ")):
            if input(yasal_uyari) == "ANLADIM":
                scrape(config)
                print("ArviS Emoji Scraper'ı kullandığın için teşekkür ederim. Dosyanı şu konumda bulabilirsin: " + config["path"])
                break
            print("Doğrulama başarısız oldu.")

main()