from app.game_manager import Game

game = Game()
try:
    with game.term.fullscreen():
        # clear the second buffer screen
        print(game.term.home + game.term.clear)

    print(game.term.enter_fullscreen)
    # Enter full screen once
    game.start_game()
except KeyboardInterrupt:
    # catch if user wants to exit by ctrl+c
    # and exit full-screen

    print(game.term.home + game.term.clear + game.term.exit_fullscreen)
