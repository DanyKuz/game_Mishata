import arcade

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
MOVE_SPEED = 5
SCREEN_TITLE = "Real Walk"


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        self.player = arcade.Sprite(
            ":resources:/images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            scale=0.5
        )
        self.player.center_x = 100
        self.player.center_y = 100

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        self.tile_map = arcade.load_tilemap(":resources:/tiled_maps/level_1.json", scaling=0.5)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.coin_list = self.scene['Coins']
        self.score = 0

        self.up = self.down = self.left = self.right = False


    def on_draw(self):
        self.clear()
        self.scene.draw()
        self.player_list.draw()
        arcade.draw_text(f'Score: {self.score}', 10, self.height - 30,
                        arcade.color.WHITE, 24)
    def on_update(self, delta_time):
        start_x = self.player.center_x
        start_y = self.player.center_y

        if self.up:
            self.player.center_y += MOVE_SPEED
        if self.down:
            self.player.center_y -= MOVE_SPEED
        if self.left:
            self.player.center_x -= MOVE_SPEED
        if self.right:
            self.player.center_x += MOVE_SPEED

        walls = self.scene['Platforms']
        if arcade.check_for_collision_with_list(self.player, walls):
            self.player.center_x = start_x
            self.player.center_y = start_y

        coins_hit = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.score += 1

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = True
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = False


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()