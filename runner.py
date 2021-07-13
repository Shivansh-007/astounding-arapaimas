from app.game_manager import Game

if "__main__" == __name__:
    game = Game()
    try:
        print(game.term.enter_fullscreen)
        # Enter full screen once
        game.start_game()
    except KeyboardInterrupt:
        # catch if user wants to exit by ctrl+c
        # and exit full-screen

        print(game.term.home + game.term.clear + game.term.exit_fullscreen)
