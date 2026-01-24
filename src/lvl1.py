import arcade

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 820
SCREEN_TITLE = "Уровень 1 — Мышата: Сбор монеток"
PLAYER_SPEED = 5
GRAVITY = 1.0
JUMP_SPEED = 21

PLAYER_SCALING = 0.3
COIN_SCALING = 0.3


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.player_list = None
        self.coin_list = None
        self.collision_list = None
        self.wall_list = None
        self.death_list = None

        self.player = None

        self.physics_engine = None

        self.score = 0
        self.total_coins = 0

        self.game_over = False

    def setup(self):
        """Инициализация уровня из Tiled-карты."""
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        map_name = "data/titlemap2/titlemap4.tmx"
        tile_map = arcade.load_tilemap(map_name, scaling=0.5)

        self.wall_list = tile_map.sprite_lists.get("Platform", arcade.SpriteList())
        self.collision_list = self.wall_list
        self.coin_list = tile_map.sprite_lists.get("Money", arcade.SpriteList())
        self.death_list = tile_map.sprite_lists.get("Trap", arcade.SpriteList())

        self.total_coins = len(self.coin_list)

        try:
            self.player = arcade.Sprite("data/mouse.png", scale=0.06)
            self.player.flip_horizontal = True
        except FileNotFoundError:
            print("Файл data/mouse.png не найден. Используем замену.")
            self.player = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", scale=PLAYER_SCALING)
            self.player.texture = self.player.texture.flip_left_right()

        self.player.center_x = 100
        self.player.center_y = 200
        self.player_list.append(self.player)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            platforms=self.collision_list,
            gravity_constant=GRAVITY
        )

        self.score = 0
        self.game_over = False

    def on_draw(self):
        """Отрисовка всего."""
        self.clear()

        self.wall_list.draw()
        self.coin_list.draw()
        self.death_list.draw()
        self.player_list.draw()

        arcade.draw_text(f"Сыр: {self.score}/{self.total_coins}", 10, SCREEN_HEIGHT - 30,
                         arcade.color.WHITE, 24, bold=True)

        if self.game_over:
            arcade.draw_text(
                "Вы собрали весь сыр!\nНажмите 'R' для перезапуска\nили 'Esc' для выхода",
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

        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1

        if self.score >= self.total_coins:
            self.game_over = True

        death_hit_list = arcade.check_for_collision_with_list(self.player, self.death_list)
        if death_hit_list:
            # Перезапуск уровня при касании ловушки
            self.setup()

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