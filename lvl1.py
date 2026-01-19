import arcade
import random

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 820
SCREEN_TITLE = "Уровень 1 — Мышата"
PLAYER_SPEED = 5


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        try:
            self.player = arcade.Sprite("data/mouse.png", scale=0.1)
            self.player.flip_horizontal = True
        except FileNotFoundError:
            print("Файл data/mouse.png не найден. Используем замену.")
            self.player = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", scale=0.3)
            self.player.texture = self.player.texture.flip_left_right()

        self.player.center_x = 100
        self.player.center_y = 100
        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player)

        self.cheese_list = arcade.SpriteList()
        self.trap_list = arcade.SpriteList()

        for _ in range(10):
            cheese = arcade.Sprite("data/cheese.png", scale=0.05)
            cheese.center_x = random.randint(50, SCREEN_WIDTH - 50)
            cheese.center_y = random.randint(50, SCREEN_HEIGHT - 50)
            self.cheese_list.append(cheese)

        for _ in range(5):
            trap = arcade.Sprite("data/mousetrap.png", scale=0.15)
            trap.center_x = random.randint(50, SCREEN_WIDTH - 50)
            trap.center_y = random.randint(50, SCREEN_HEIGHT - 50)
            self.trap_list.append(trap)

        self.score = 0
        self.pause = False

    def on_draw(self):
        self.clear()
        if not self.pause:
            self.player_spritelist.draw()
            self.cheese_list.draw()
            self.trap_list.draw()
        else:
            self.game_over_text.draw()
        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 24)

    def on_update(self, delta_time):
        if self.pause:
            return
        if self.score == 10:
            arcade.close_window()

        self.player.update()

        collected = arcade.check_for_collision_with_list(self.player, self.cheese_list)
        for item in collected:
            item.remove_from_sprite_lists()
            self.score += 1

        if arcade.check_for_collision_with_list(self.player, self.trap_list):
            self.game_over()

    def on_key_press(self, key, modifiers):
        if self.pause:
            if key == arcade.key.R:
                self.setup()
            elif key == arcade.key.Q or key == arcade.key.ESCAPE:
                arcade.close_window()
            return

        speed = PLAYER_SPEED
        if key == arcade.key.UP:
            self.player.change_y = speed
        elif key == arcade.key.DOWN:
            self.player.change_y = -speed
        elif key == arcade.key.LEFT:
            self.player.change_x = -speed
        elif key == arcade.key.RIGHT:
            self.player.change_x = speed

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player.change_x = 0
        if key in (arcade.key.UP, arcade.key.DOWN):
            self.player.change_y = 0

    def game_over(self):
        self.pause = True
        self.game_over_text = arcade.Text(
            "Вы проиграли!\nНажмите 'R' для перезапуска\nили 'Esc' для выхода",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.RED,
            24,
            anchor_x="center",
            anchor_y="center"
        )


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()