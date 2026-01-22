import arcade
import random

# Константы
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 820
SCREEN_TITLE = "Уровень 1 — Мышата: Сбор монеток"
PLAYER_SPEED = 5
GRAVITY = 1.0
JUMP_SPEED = 20

# Масштабы спрайтов
PLAYER_SCALING = 0.3
COIN_SCALING = 0.3
PLATFORM_SCALING = 0.5


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # Списки спрайтов
        self.player_list = None
        self.coin_list = None
        self.platform_list = None

        # Игрок
        self.player = None

        # Физический движок
        self.physics_engine = None

        # Счёт
        self.score = 0

        # Пауза / конец игры
        self.game_over = False

    def setup(self):
        """Инициализация уровня с фиксированными платформами."""
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.platform_list = arcade.SpriteList()

        # === Игрок ===
        try:
            self.player = arcade.Sprite("data/mouse.png", scale=0.1)
            self.player.flip_horizontal = True
        except FileNotFoundError:
            print("Файл data/mouse.png не найден. Используем замену.")
            self.player = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", scale=PLAYER_SCALING)
            self.player.texture = self.player.texture.flip_left_right()

        self.player.center_x = 100
        self.player.center_y = 200
        self.player_list.append(self.player)

        # === Пол (фиксированный, без random) ===
        for x in range(0, SCREEN_WIDTH + 1, 64):
            platform = arcade.Sprite(":resources:images/tiles/grassMid.png", PLATFORM_SCALING)
            platform.center_x = x
            platform.center_y = 32
            self.platform_list.append(platform)

        # === Дополнительные платформы — строго по координатам ===
        extra_platforms = [
            (300, 200),
            (500, 300),
            (700, 250),
            (900, 400),
            (1100, 350),
            (1300, 500),
            (200, 450),   # можно добавить ещё
            (800, 600),
        ]

        for x, y in extra_platforms:
            try:
                platform = arcade.Sprite("data/polka.png", scale=0.3)
            except FileNotFoundError:
                print("Файл data/polka.png не найден. Используем замену.")
                platform = arcade.Sprite(":resources:images/tiles/grassHalf.png", PLATFORM_SCALING)
            platform.center_x = x
            platform.center_y = y
            self.platform_list.append(platform)

        # === Монетки — тоже можно сделать фиксированными, но пока оставим как есть или сделаем фиксированными ===
        # Вариант 1: оставить случайные, но выше земли
        # Вариант 2: задать вручную — покажу оба

        # --- Вариант: фиксированные монетки (рекомендуется для контроля уровня) ---
        coin_positions = [
            (300, 250), (500, 350), (700, 300),
            (900, 450), (1100, 400), (1300, 550),
            (200, 550), (800, 650), (400, 150),
            (600, 180), (1000, 220), (1200, 300),
            (1400, 400), (1500, 100), (100, 300)
        ]

        for x, y in coin_positions:
            try:
                coin = arcade.Sprite("data/cheese.png", scale=0.05)
            except FileNotFoundError:
                print("Файл data/cheese.png не найден. Используем монетку.")
                coin = arcade.Sprite(":resources:images/items/coinGold.png", COIN_SCALING)
            coin.center_x = x
            coin.center_y = y
            self.coin_list.append(coin)

        # === Физический движок ===
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            platforms=self.platform_list,
            gravity_constant=GRAVITY
        )

        self.score = 0
        self.game_over = False

    def on_draw(self):
        """Отрисовка всего."""
        self.clear()

        self.platform_list.draw()
        self.coin_list.draw()
        self.player_list.draw()

        arcade.draw_text(f"Сыр: {self.score}/15", 10, SCREEN_HEIGHT - 30,
                         arcade.color.WHITE, 24, bold=True)

        if self.game_over:
            arcade.draw_text(
                "Вы собрали все монетки!\nНажмите 'R' для перезапуска\nили 'Esc' для выхода",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.GREEN,
                36,
                anchor_x="center",
                anchor_y="center",
                align="center",
                multiline=True,
                width=600
            )

    def on_update(self, delta_time):
        """Логика обновления."""
        if self.game_over:
            return

        self.physics_engine.update()

        # Сбор монеток
        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1

        # Проверка победы
        if self.score >= 15:
            self.game_over = True

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш."""
        if self.game_over:
            if key == arcade.key.R:
                self.setup()
            elif key == arcade.key.ESCAPE or key == arcade.key.Q:
                arcade.close_window()
            return

        if key == arcade.key.LEFT:
            self.player.change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = PLAYER_SPEED
        elif key == arcade.key.UP or key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.change_y = JUMP_SPEED

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш."""
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player.change_x = 0


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()