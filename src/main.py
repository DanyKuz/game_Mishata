import arcade
from gameWindow import GameWindow
from menuView import MenuView


def main():
    window = GameWindow()
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
