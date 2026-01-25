import arcade
import subprocess
import sys
import json
import os

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 820
SCREEN_TITLE = "Мышата"

MAIN_MENU = "main"
RULES = "rules"
CONTROLS = "controls"
LEVELS = "levels"
PROGRESS_FILE = "progress.json"

def save_progress(data):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        # По умолчанию только уровень 1 доступен
        default = {
            "level_1_unlocked": True,
            "level_2_unlocked": False,
            "level_3_unlocked": False
        }
        save_progress(default)
        return default
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        # На случай повреждения файла
        default = {"level_1_unlocked": True, "level_2_unlocked": False, "level_3_unlocked": False}
        save_progress(default)
        return default


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.current_state = MAIN_MENU
        try:
            self.background_texture = arcade.load_texture("data/background.png")
        except FileNotFoundError:
            self.background_texture = None
            print("Фон не найден. Используем чёрный фон.")

    

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()

        if self.background_texture:
            arcade.draw_texture_rect(
                self.background_texture,
                arcade.rect.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT)
            )

        if self.current_state == MAIN_MENU:
            arcade.draw_text("Мышата", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
                            arcade.color.WHITE, font_size=48, anchor_x="center", bold=True)
            self.draw_menu_item("К уровням", 0)
            self.draw_menu_item("Правила", 1)
            self.draw_menu_item("Управление", 2)

        elif self.current_state == RULES:
            self.draw_header("Правила")
            self.draw_multiline_text(
                "Цель игры — собрать весь сыр на уровне.\n\n"
                "Опасности:\n"
                "• Кошка — +15 секунд к времени\n"
                "• Мышеловка — +10 секунд к времени\n"
                "• Стены — непроходимы\n\n"
                "Пройдите уровень быстрее, чем раньше!"
            )
            self.draw_back_button()

        elif self.current_state == CONTROLS:
            self.draw_header("Управление")
            self.draw_multiline_text(
                "• WASD или стрелки — движение мышонка\n"
                "• Esc — открыть меню во время игры\n\n"
                "Собирайте сыр и избегайте опасностей!"
            )
            self.draw_back_button()

        elif self.current_state == LEVELS:
            self.draw_header("Выбор уровня")
            
            progress = load_progress()  # ← загружаем прогресс

            # Уровень 1 — всегда доступен
            color1 = arcade.color.GREEN
            # Уровень 2
            color2 = arcade.color.GREEN if progress.get("level_2_unlocked", False) else arcade.color.RED
            # Уровень 3
            color3 = arcade.color.GREEN if progress.get("level_3_unlocked", False) else arcade.color.RED

            arcade.draw_text("Уровень 1", SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 30,
                            color1, font_size=22, anchor_x="center")
            arcade.draw_text("Уровень 2", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30,
                            color2, font_size=22, anchor_x="center")
            arcade.draw_text("Уровень 3", SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT // 2 + 30,
                            color3, font_size=22, anchor_x="center")
            self.draw_back_button()

    def draw_header(self, text):
        arcade.draw_text(text, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120,
                        arcade.color.WHITE, font_size=36, anchor_x="center", bold=True)

    def draw_menu_item(self, text, index):
        y = SCREEN_HEIGHT - 350 - index * 50
        arcade.draw_text(text, SCREEN_WIDTH // 2, y,
                        arcade.color.LIGHT_GRAY, font_size=24, anchor_x="center")

    def draw_multiline_text(self, text):
        arcade.draw_text(
            text,
            x=SCREEN_WIDTH // 2,
            y=SCREEN_HEIGHT // 2 + 100,
            color=arcade.color.WHITE,
            font_size=18,
            anchor_x="center",
            width=600,
            align="center",
            multiline=True
        )

    def draw_back_button(self):
        arcade.draw_text("Назад", 80, 50, arcade.color.BLUE, font_size=18)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.current_state == LEVELS:
            progress = load_progress()
            level_y = SCREEN_HEIGHT // 2 + 30

            # Уровень 1 (всегда активен)
            if abs(x - (SCREEN_WIDTH // 2 - 200)) < 100 and abs(y - level_y) < 20:
                subprocess.Popen([sys.executable, "src/lvl1.py"])
                return

            # Уровень 2 (только если разблокирован)
            if (progress.get("level_2_unlocked", False) and
                abs(x - (SCREEN_WIDTH // 2)) < 100 and abs(y - level_y) < 20):
                subprocess.Popen([sys.executable, "src/lvl2.py"])
                return

            # Уровень 3 (позже)
            if (progress.get("level_3_unlocked", False) and
                abs(x - (SCREEN_WIDTH // 2 + 200)) < 100 and abs(y - level_y) < 20):
                subprocess.Popen([sys.executable, "src/lvl3.py"])
                return

            # Кнопка "Назад"
            if 20 <= x <= 140 and 40 <= y <= 80:
                self.current_state = MAIN_MENU
        elif self.current_state == MAIN_MENU:
            for i, _ in enumerate(["К уровням", "Правила", "Управление"]):
                btn_y = SCREEN_HEIGHT - 340 - i * 50
                if abs(x - SCREEN_WIDTH // 2) < 120 and abs(y - btn_y) < 20:
                    if i == 0:
                        self.current_state = LEVELS
                    elif i == 1:
                        self.current_state = RULES
                    elif i == 2:
                        self.current_state = CONTROLS
                    return
        else:
            if 20 <= x <= 140 and 40 <= y <= 80:
                self.current_state = MAIN_MENU

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.current_state = MAIN_MENU


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)


def main():
    window = GameWindow()
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()