from blessed import Terminal
from subprocess import call
import menu_helper    
import sys


helper = menu_helper.Helper()
term = Terminal()

w,h = term.width, term.height
options = [' Create Game ', ' Join Game ', ' Settings ', ' Exit ']
brief = ['Creates an new game and waits for an opponent to join','Join a pre-existing game of your choice','Change your game settings','Exit the game']
curr_highlight = 0
term_positions = [int(w*0.38),int(w*0.46),int(w*0.54),int(w*0.62)]


def print_options():
    for i,option in enumerate(options):
        if i == curr_highlight and i != 3: 
            print(term.move_x(term_positions[i])+ term.underline_bold_white_on_green + str(option) + term.normal+ term.move_x(0), end="")
        elif i == curr_highlight and i == 3:
            print(term.move_x(term_positions[i])+ term.underline_bold_white_on_red + str(option) + term.normal+ term.move_x(0), end="")
        elif i == 3:
            print(term.move_x(term_positions[i])+ term.bold_red+str(option)+term.normal+ term.move_x(0), end="")
        else:
            print(term.move_x(term_positions[i])+ term.bold_green+str(option)+ term.move_x(0), end="")
        sys.stdout.flush()
    if curr_highlight != 9:
        print(term.move_down(3)+term.green+term.center(brief[curr_highlight])+term.move_x(0) +'\n\n'+term.white+term.center('Press [ENTER] to confirm') + term.move_up(5), end = "")
    else:
        print(term.move_down(3)+term.white+term.center('Press [TAB] for option selection') +term.normal+ term.move_up(4)+term.move_x(0))

def select_option(key):
  global curr_highlight
  if curr_highlight < 3:
    curr_highlight += 1
  else:
    curr_highlight = 0

def next():
    if not curr_highlight:
        print('Created a new game') #Executes something when 'Create Game' is called
    elif curr_highlight == 1:
        call(["python", "game_manager.py"]) #Link to the actual game when selected
    elif curr_highlight == 2:
        print('Settings Selected') #Link to settings file to access settings
    else:
        print('Exited the game')

def main():
    global curr_highlight
    curr_highlight = 9
    title_split = helper.title.split("\n")
    with term.fullscreen(), term.cbreak():
        print(term.home + term.clear + term.move_y(int(h*.30))) 
        for component in title_split:     
            print(term.center(component))
        print(term.home + term.move_y(int(h*.60)))
        print_options()
        pressed = ''
        while pressed != 'KEY_ENTER':
            pressed = term.inkey().name
            if pressed == 'KEY_TAB':    
                select_option(pressed) 
                print_options()
    term.exit_fullscreen
    print(term.home+term.clear)
    next()

if __name__ == '__main__':
  main()