from blessed import Terminal

term = Terminal()

print(term.home + term.clear + term.move_y(0))
print(term.bold_black_on_green(term.center("press any key to continue.")))
print("\n")
print(term.green("press any key to continue."))
