import arcade
import json
import os

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 820
SCREEN_TITLE = "Уровень 2 — Мышата: Сбор монеток"
PLAYER_SPEED = 5
GRAVITY = 1.0
JUMP_SPEED = 21
CAT_SPEED = 2

PLAYER_SCALING = 0.06
COIN_SCALING = 0.3
CAT_SCALING = 0.08
PAUSE_SIGN_PATH = "data/pauseboard.png"


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.player_list = None
        self.coin_list = None
        self.wall_list = None
        self.death_list = None
        self.cat_list = None

        self.player = None
        self.physics_engine = None

        self.score = 0
        self.total_coins = 0
        self.game_over = False
        self.paused = False

        self.left_pressed = False
        self.right_pressed = False
        self.facing_left = False

        self.player_texture_right = None
        self.player_texture_left = None
        
        self.is_frozen = False
        self.freeze_timer = 0.0
        self.freeze_duration = 2.0
        
        self.cat_texture_right = None
        self.cat_texture_left = None

        self.pause_sign_sprite = None
        self.pause_sign_list = arcade.SpriteList()

        self.game_time = 0.0
        self.timer_running = False
        self.best_time = None 

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.cat_list = arcade.SpriteList()

        map_name = "data/titlemap2/titlemap4.tmx"
        tile_map = arcade.load_tilemap(map_name, scaling=0.5)

        self.wall_list = tile_map.sprite_lists.get("Platform", arcade.SpriteList())
        self.wall2_list = tile_map.sprite_lists.get("wall", arcade.SpriteList())
        self.coin_list = tile_map.sprite_lists.get("Money", arcade.SpriteList())
        self.death_list = tile_map.sprite_lists.get("Trap", arcade.SpriteList())

        self.walls = [self.wall_list, self.wall2_list]
        
        enemy_layer = tile_map.sprite_lists.get("Enemy", arcade.SpriteList())
        for enemy_sprite in enemy_layer:
            try:
                cat = arcade.Sprite("data/cat.png", scale=CAT_SCALING)
                self.cat_texture_right = arcade.load_texture("data/cat.png")
                self.cat_texture_left = self.cat_texture_right.flip_left_right()
            except FileNotFoundError:
                print("Файл data/cat.png не найден. Используем замену.")
                cat = arcade.Sprite(":resources:images/enemies/wormGreen.png", scale=CAT_SCALING)
                self.cat_texture_right = arcade.load_texture(":resources:images/enemies/wormGreen.png")
                self.cat_texture_left = self.cat_texture_right.flip_left_right()
            
            cat.center_x = enemy_sprite.center_x
            cat.center_y = enemy_sprite.center_y
            
            cat.boundary_left = cat.center_x - 150
            cat.boundary_right = cat.center_x + 150
            cat.change_x = CAT_SPEED
            
            cat.texture = self.cat_texture_left
            cat.facing_left = False
            
            self.cat_list.append(cat)

        self.total_coins = len(self.coin_list)

        try:
            texture_right = arcade.load_texture("data/mouse.png")
        except FileNotFoundError:
            print("Файл data/mouse.png не найден. Используем замену.")
            texture_right = arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_idle.png")
            global PLAYER_SCALING
            PLAYER_SCALING = 0.3

        texture_left = texture_right.flip_left_right()

        self.player_texture_right = texture_right
        self.player_texture_left = texture_left

        self.player = arcade.Sprite()
        self.player.texture = self.player_texture_right
        self.player.scale = PLAYER_SCALING
        self.player.center_x = 100
        self.player.center_y = 200
        self.player_list.append(self.player)
        

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            platforms=self.walls,
            gravity_constant=GRAVITY
        )

        self.pause_sign_list.clear()
        try:
            self.pause_sign_sprite = arcade.Sprite(PAUSE_SIGN_PATH)
            self.pause_sign_sprite.center_x = SCREEN_WIDTH // 2
            self.pause_sign_sprite.center_y = SCREEN_HEIGHT // 2
            self.pause_sign_sprite.scale = 0.6
            self.pause_sign_list.append(self.pause_sign_sprite)
            print(f"Табличка паузы загружена: {PAUSE_SIGN_PATH}")
        except Exception as e:
            print(f"Не удалось загрузить табличку паузы: {e}")
            self.pause_sign_sprite = None

        self.score = 0
        self.game_over = False
        self.paused = False
        self.facing_left = False
        self.left_pressed = False
        self.right_pressed = False

        self.game_time = 0.0
        self.timer_running = True
        self.is_frozen = False
        self.freeze_timer = 0.0

        self.load_best_time()

    def load_best_time(self):
        PROGRESS_FILE = "progress.json"
        self.best_time = None
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                    progress = json.load(f)
                    self.best_time = progress.get("level_2_best_time")
            except:
                pass

    def save_progress(self):
        PROGRESS_FILE = "progress.json"
        progress = {"level_1_unlocked": True, "level_2_unlocked": True, "level_3_unlocked": False}
        
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                    progress = json.load(f)
            except:
                pass
        
        progress["level_3_unlocked"] = True
        
        current_time = self.game_time
        if "level_2_best_time" in progress:
            if current_time < progress["level_2_best_time"]:
                progress["level_2_best_time"] = current_time
        else:
            progress["level_2_best_time"] = current_time
        
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=4, ensure_ascii=False)

    def format_time(self, seconds):
        minutes = int(seconds) // 60
        seconds_remainder = seconds % 60
        return f"{minutes:02d}:{seconds_remainder:05.2f}"

    def update_player_direction(self):
        if self.right_pressed and not self.left_pressed:
            if self.facing_left:
                self.player.texture = self.player_texture_right
                self.facing_left = False
        elif self.left_pressed and not self.right_pressed:
            if not self.facing_left:
                self.player.texture = self.player_texture_left
                self.facing_left = True

    def on_draw(self):
        self.clear()

        self.wall_list.draw()
        self.coin_list.draw()
        self.death_list.draw()
        self.cat_list.draw()
        self.player_list.draw()

        arcade.draw_text(f"Сыр: {self.score}/{self.total_coins}", 10, SCREEN_HEIGHT - 30,
                         arcade.color.WHITE, 24, bold=True)

        timer_text = f"Время: {self.format_time(self.game_time)}"
        arcade.draw_text(timer_text, SCREEN_WIDTH - 450, SCREEN_HEIGHT - 30,
                         arcade.color.WHITE, 24, bold=True)

        if self.best_time is not None:
            best_text = f"Рекорд: {self.format_time(self.best_time)}"
            arcade.draw_text(best_text, SCREEN_WIDTH - 450, SCREEN_HEIGHT - 60,
                             arcade.color.GOLD, 20, bold=True)
        
        if self.is_frozen:
            remaining = max(0, self.freeze_duration - self.freeze_timer)
            arcade.draw_text(f"ЗАМОРОЗКА: {remaining:.1f}с", 
                           SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                           arcade.color.BLUE, 36, bold=True, anchor_x="center")
            
        if self.paused:
            if self.pause_sign_sprite:
                self.pause_sign_list.draw()
                arcade.draw_text(
                    "ПАУЗА\n\n\n"
                    "Нажмите 'P' чтобы продолжить\n"
                    "'R' для перезапуска\n"
                    "'Esc' или 'Q' для выхода",
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 40,
                    arcade.color.BLACK,
                    24,
                    anchor_x="center",
                    anchor_y="center",
                    align="center",
                    multiline=True,
                    width=500
                )
            else:
                arcade.draw_text(
                    "ПАУЗА\n\n"
                    "Нажмите 'P' чтобы продолжить\n"
                    "'R' для перезапуска\n"
                    "'Esc' или 'Q' для выхода",
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2,
                    arcade.color.WHITE,
                    36,
                    anchor_x="center",
                    anchor_y="center",
                    align="center",
                    multiline=True,
                    width=600
                )
            
        if self.game_over:
            arcade.draw_text(
                "Вы собрали весь сыр!\n"
                f"Время: {self.format_time(self.game_time)}\n"
                f"Рекорд: {self.format_time(self.best_time) if self.best_time and self.game_time >= self.best_time else 'НОВЫЙ РЕКОРД!'}\n\n"
                "Нажмите 'R' для перезапуска\nили 'Esc' для выхода",
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
        if self.game_over:
            return

        if self.paused:
            self.player.change_x = 0
            return

        self.game_time += delta_time

        if self.is_frozen:
            self.freeze_timer += delta_time
            if self.freeze_timer >= self.freeze_duration:
                self.is_frozen = False
                self.freeze_timer = 0.0

        if not self.is_frozen:
            self.player.change_x = 0
            if self.left_pressed:
                self.player.change_x = -PLAYER_SPEED
            if self.right_pressed:
                self.player.change_x = PLAYER_SPEED
            self.update_player_direction()
        else:
            self.player.change_x = 0

        self.physics_engine.update()

        for cat in self.cat_list:
            cat.center_x += cat.change_x
            
            if cat.boundary_left and cat.center_x <= cat.boundary_left:
                cat.change_x = CAT_SPEED
                cat.texture = self.cat_texture_left
                cat.facing_left = False
            elif cat.boundary_right and cat.center_x >= cat.boundary_right:
                cat.change_x = -CAT_SPEED
                cat.texture = self.cat_texture_right
                cat.facing_left = True

        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1

        if self.score >= self.total_coins and not self.game_over:
            self.game_over = True
            self.timer_running = False
            self.save_progress()

        death_hit_list = arcade.check_for_collision_with_list(self.player, self.death_list)
        if death_hit_list:
            self.setup()
            
        cat_hit_list = arcade.check_for_collision_with_list(self.player, self.cat_list)
        if cat_hit_list and not self.is_frozen:
            self.is_frozen = True
            self.freeze_timer = 0.0
            self.player.change_x = 0
            if cat_hit_list[0].facing_left:
                self.player.center_x += 30
            else:
                self.player.center_x -= 30

    def on_key_press(self, key, modifiers):
        if key == arcade.key.P:
            self.paused = not self.paused
            if not self.paused:
                self.left_pressed = False
                self.right_pressed = False
                self.player.change_x = 0
            return

        if self.paused or self.game_over:
            if key == arcade.key.R:
                self.setup()
            elif key == arcade.key.ESCAPE or key == arcade.key.Q:
                arcade.close_window()
            return

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.SPACE or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player.change_y = JUMP_SPEED

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()