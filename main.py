import time
import sys
import threading
import random
from colorama import init, Fore, Style
import sounddevice as sd
import soundfile as sf

# Ініціалізація colorama
init(autoreset=False)

# ----------- Звук -------------
current_sound = None
def play_sound(filepath):
    if not filepath:
        return
    global current_sound
    def _play():
        global current_sound
        try:
            if current_sound:
                sd.stop()
            data, sr = sf.read(filepath, dtype='float32')
            current_sound = sd.play(data, sr)
        except Exception as e:
            sys.stdout.write(Fore.RED + f"Не вдалося відтворити звук: {e}\n" + Style.RESET_ALL)
    threading.Thread(target=_play, daemon=True).start()

# ----------- Анімація -------------
def type_animate(text: str, color: str = Fore.YELLOW, delay: float = 0.02):
    sys.stdout.write(color)
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(Style.RESET_ALL + "\n")

# ----------- Класи -------------
class Scene:
    def __init__(self, key, text, options, sound=None):
        self.key = key
        self.text = text
        self.options = options  # текст кнопки -> ключ наступної сцени
        self.sound = sound

class Player:
    def __init__(self):
        self.inventory = []
        self.hp = 100
        self.gold = 30
        self.rest_used = False
    def add_item(self, item):
        if item not in self.inventory:
            self.inventory.append(item)
    def take_damage(self, dmg):
        self.hp = max(self.hp - dmg, 0)
    def heal(self, amt):
        self.hp = min(self.hp + amt, 100)

class Enemy:
    def __init__(self, name, hp, dmg):
        self.name = name
        self.hp = hp
        self.dmg = dmg

# ----------- Сцени -------------
scenes = {
    "start": Scene("start",
        "Ви прокинулися в темному лісі. Куди підете?",
        {"Ліворуч": "cave", "Праворуч": "forest_path", "Інвентар": "inventory"},
        sound="forest.wav"
    ),
    "forest_path": Scene("forest_path",
        "Ви пробираєтесь через густий ліс. Щось шарудить попереду...",
        {"Далі": "village_gate"}
    ),
    "village_gate": Scene("village_gate",
        "Ви бачите ворота села. Скоро будете в безпеці.",
        {"У село": "village"}
    ),
    "cave": Scene("cave",
        "У печері темно і страшно. Ви знайшли ЗАЧАРОВАНИЙ МЕЧ! (30–40 урону)",
        {"Назад": "start"},
        sound="cave.wav"
    ),
    "village": Scene("village",
        "Ви в селі. Тут вас чекає старий воїн та шинок.",
        {"Поговорити з воїном": "talk_warrior", "Ринок": "market", "Шинок": "tavern", "Інвентар": "inventory"},
        sound="village.wav"
    ),
    "talk_warrior": Scene("talk_warrior",
        "Старий: «Тебе чекає темний зачарований ліс. Пройди його, побори ворогів і дій до головного мага!»",
        {"Йти в ліс": "enchanted_forest_entrance", "Назад": "village"}
    ),
    "enchanted_forest_entrance": Scene("enchanted_forest_entrance",
        "Перед вами початок зачарованого лісу. Приготуйтеся до бою!",
        {"Продовжити": "battle_bandits"}
    ),
    "battle_bandits": Scene("battle_bandits", "", {}, sound="battle.wav"),
    "battle_wolves": Scene("battle_wolves", "", {}, sound="battle.wav"),
    "forest_rest": Scene("forest_rest",
        "Після бою ви знаходите безпечну полянку. Чи відпочинете тут (+25 HP)?",
        {"Відпочити": "rest_done", "Продовжити без відпочинку": "boss_battle"}
    ),
    "rest_done": Scene("rest_done",
        "Ви відпочили та відновили 25 HP.",
        {"Продовжити шлях": "boss_battle"}
    ),
    "market": Scene("market",
        "На ринку: Меч – 50г (15–25 урону), Зілля – 30г (+30 HP).",
        {"Купити меч": "buy_sword", "Купити зілля": "buy_potion", "Назад": "village"}
    ),
    "buy_sword": Scene("buy_sword",
        "Куплено звичайний меч! (15–25 урону)",
        {"Назад": "market"}
    ),
    "buy_potion": Scene("buy_potion",
        "Куплено зілля! (+30 HP)",
        {"Назад": "market"}
    ),
    "tavern": Scene("tavern",
        "Ви зайшли до шинку. Гамірно і затишно. Господар: «Принеси ікону з покинутого дому — 300г!»",
        {"Прийняти роботу": "abandoned", "Назад": "village"},
        sound="tavern.wav"
    ),
    "abandoned": Scene("abandoned",
        "У будинку фантоми атакують!",
        {"Битися": "battle_ghosts", "Втікати": "village"},
        sound="house.wav"
    ),
    # сцена нагороди в шинку
    "tavern_reward": Scene("tavern_reward",
        "Ви принесли ікону в шинок. Господар дякує і дає вам 300 золота!",
        {"Повернутися до шинку": "tavern", "У село": "village"},
        sound="reward.wav"
    ),
    "battle_ghosts": Scene("battle_ghosts", "", {}, sound="battle.wav"),
    "inventory": Scene("inventory", "", {"Назад": "start"}),
    "boss_battle": Scene("boss_battle",
        "Перед вами головний маг! Остання битва!",
        {"Почати битву": "fight_boss"},
        sound="boss.wav"
    ),
    "fight_boss": Scene("fight_boss", "", {}, sound="boss.wav"),
    "victory": Scene("victory",
        "Ви перемогли головного мага та врятували село! Вітаю!",
        {"Почати з початку": "start"},
        sound="victory.wav"
    ),
    "game_over": Scene("game_over",
        "Гру завершено. Ви загинули.",
        {"Почати з початку": "start"},
        sound="gameover.wav"
    ),
}

# ----------- Битва ------------- 
def battle(player, enemy, final=False):
    type_animate(f"Битва з {enemy.name}!", Fore.RED)
    play_sound("battle.wav")
    while player.hp > 0 and enemy.hp > 0:
        type_animate(f"HP: {player.hp} | {enemy.name} HP: {enemy.hp}", Fore.YELLOW)
        sys.stdout.write(Fore.MAGENTA)
        print("1.Атакувати   2.Зілля   3.Відступити")
        sys.stdout.write(Style.RESET_ALL)
        ch = input(Fore.CYAN + "Введіть номер: " + Style.RESET_ALL)
        if ch == "1":
            if "ЗАЧАРОВАНИЙ МЕЧ" in player.inventory:
                dmg = random.randint(30, 40)
            elif "Меч" in player.inventory:
                dmg = random.randint(15, 25)
            else:
                dmg = random.randint(5, 10)
            enemy.hp -= dmg
            type_animate(f"Ви завдали {dmg} урону!", Fore.GREEN)
        elif ch == "2" and "Зілля" in player.inventory:
            player.inventory.remove("Зілля")
            player.heal(30)
            type_animate("Відновлено 30 HP", Fore.GREEN)
        elif ch == "3":
            type_animate("Ви втекли...", Fore.RED)
            return False
        else:
            type_animate("Невірний вибір!", Fore.RED)
            continue
        if enemy.hp > 0:
            player.take_damage(enemy.dmg)
            type_animate(f"{enemy.name} завдав {enemy.dmg} урону!", Fore.RED)
    return "victory" if final else True

# ----------- Основний цикл гри -------------
def main():
    player = Player()
    visited_cave = False
    key = "start"

    while True:
        sc = scenes[key]

        # при першому вході в печеру даємо зачар. меч
        if key == "cave" and not visited_cave:
            player.add_item("ЗАЧАРОВАНИЙ МЕЧ")
            visited_cave = True

        # бойові сцени
        if key == "battle_ghosts":
            res = battle(player, Enemy("Фантом", 50, 15))
            key = "tavern_reward" if res else "game_over"
            continue
        if key == "battle_bandits":
            res = battle(player, Enemy("Бандити", 60, 12))
            key = "battle_wolves" if res else "game_over"
            continue
        if key == "battle_wolves":
            res = battle(player, Enemy("Вовки", 70, 15))
            key = "forest_rest" if res else "game_over"
            continue
        if key == "fight_boss":
            res = battle(player, Enemy("Головний маг", 120, 25), final=True)
            key = res
            continue

        # показ тексту та музики
        type_animate(sc.text, Fore.YELLOW)
        play_sound(sc.sound)

        # сцена нагороди в шинку
        if key == "tavern_reward":
            player.gold += 300
            # показуємо текст і варіанти
            opts = list(scenes["tavern_reward"].options.items())
            sys.stdout.write(Fore.MAGENTA)
            for i, (txt, _) in enumerate(opts, 1):
                print(f"{i}. {txt}")
            sys.stdout.write(Style.RESET_ALL)
            sel = input(Fore.CYAN + "Введіть номер: " + Style.RESET_ALL)
            if sel == "1":
                key = "tavern"
            elif sel == "2":
                key = "village"
            else:
                type_animate("Невірний вибір!", Fore.RED)
            continue

        # інвентар
        if key == "inventory":
            type_animate("Інвентар:", Fore.YELLOW)
            for it in player.inventory or ["(порожньо)"]:
                type_animate(f"- {it}", Fore.WHITE)
            type_animate(f"Золото: {player.gold}", Fore.CYAN)
            input(Fore.CYAN + "Enter, щоб повернутись" + Style.RESET_ALL)
            key = "start"
            continue

        # показ опцій
        opts = list(sc.options.items())
        sys.stdout.write(Fore.MAGENTA)
        for i, (txt, _) in enumerate(opts, 1):
            print(f"{i}. {txt}")
        sys.stdout.write(Style.RESET_ALL)

        sel = input(Fore.CYAN + "Введіть номер: " + Style.RESET_ALL)
        if not sel.isdigit() or not (1 <= int(sel) <= len(opts)):
            type_animate("Невірний вибір!", Fore.RED)
            continue

        nxt = opts[int(sel) - 1][1]

        # покупки
        if nxt == "buy_sword":
            if player.gold >= 50:
                player.gold -= 50
                player.add_item("Меч")
                type_animate("Куплено звичайний меч!", Fore.GREEN)
            else:
                type_animate("Недостатньо золота!", Fore.RED)
            key = "market"
            continue
        if nxt == "buy_potion":
            if player.gold >= 30:
                player.gold -= 30
                player.add_item("Зілля")
                type_animate("Куплено зілля!", Fore.GREEN)
            else:
                type_animate("Недостатньо золота!", Fore.RED)
            key = "market"
            continue

        # відпочинок
        if nxt == "rest_done":
            if not player.rest_used:
                player.heal(25)
                player.rest_used = True
            nxt = "boss_battle"

        key = nxt
        if key in ("victory", "game_over"):
            type_animate(scenes[key].text, Fore.CYAN if key == "victory" else Fore.RED)
            break

if __name__ == "__main__":
    main()
