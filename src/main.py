import arcade
from menuView import GameWindow, MenuView


def main():
    window = GameWindow()
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
