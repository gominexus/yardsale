import pyglet
import random
import numpy as np
from pyglet import shapes


# Pyglet graphics batches to use to display circles and trades
trader_batch = pyglet.graphics.Batch()
interact_batch = pyglet.graphics.Batch()


# DEFINE THE LAYOUT FOR TRADERS ON THE SCREEN
# -------------------------------------------

# Layout of traders (100 = 10 rows x 10 columns)
rows, columns = 10,10
window_width, window_height = 1920,1080

#Determine spacing
x_offset = int(window_width / (columns+1))
y_offset = int(window_height / (rows+1))
x_coords = np.linspace(0+x_offset,window_width-x_offset,columns,dtype=int)
y_coords = np.linspace(0+y_offset,window_height-y_offset,rows,dtype=int)

trader_x_coords = np.zeros(x_coords.size * y_coords.size)
trader_y_coords = np.zeros(x_coords.size * y_coords.size)
n=0
trader_colour = []
for x in x_coords:
    for y in y_coords:
        trader_x_coords[n] = x
        trader_y_coords[n] = y
        trader_colour.append((random.randint(100,255),random.randint(100,255),random.randint(100,255)))
        n += 1


# THE YARD SALE MODEL ITSELF
# --------------------------
# Trading logic is defined using definition from here:
# https://www.physics.umd.edu/hep/drew/math_general/yard_sale.html
# "Label them $A$ and $B$ such that $A$ is wealthier than $B$.
# Then for each transaction, you flip a coin, and if it comes
# up heads, $A$ gives an amount equal to $20\%$ of $B$'s wealth to $B$.
# If it comes up tails, then $A$ takes an amount equal to $17\%$ of $B$'s
# wealth, so that $B$ never loses more than their wealth"

number_of_traders = rows * columns
starting_cash = 100
trader_money = np.repeat(starting_cash, number_of_traders) # Define the starting amount of money

def trading_event():
    
    # Pick random traders
    i = random.randint(0,number_of_traders-1)
    j = random.randint(0,number_of_traders-1)
    # Just in case we pick the same trader twice, try again
    while j == i:
        j = random.randint(0,number_of_traders-1)    
    
    # Choose trader A and B such that A is always the richer one
    if trader_money[i] > trader_money[j]:
        trader_A = i; trader_B = j
    else:
        trader_A = j; trader_B = i
    
    # Simulate the coin flip exchange
    if random.uniform(0,1) > 0.5:
        exchanged_money = trader_money[trader_B] * 0.17
        trader_money[trader_A] += exchanged_money
        trader_money[trader_B] -= exchanged_money
    else:
        exchanged_money = trader_money[trader_B] * 0.2
        trader_money[trader_B] += exchanged_money
        trader_money[trader_A] -= exchanged_money
        
    return (trader_A,trader_B)

# DRAWING / DISPLAY FUNCTIONS
# ---------------------------

# draw a trader, area being proportional to money
def draw_trader(money,x,y,colour,batch):

    # Scale the circle size up
    area = money * 30

    # A = money; A = pi * r^2, therefore r = sqrt(A/pi)
    radius = np.sqrt(area/np.pi).astype(int)
    circle = shapes.Circle(x,y,radius=max(radius,1),color=colour,batch=batch)
    min_opacity = 120

    # If radius > 1, set to full opacity
    if radius > 1:
        circle.opacity = 255
    # If radius < 1, scale opacity with money, whilst setting a min value
    else:
        # Radius = 1 when money = pi, so when radius is < 1,
        # we can scale the capacity down as a proporiton of pi
        circle.opacity = max(int(255 * area / np.pi),min_opacity)
    return circle
        
# Initial setup - draw all circles
circles_list = []
def circle_setup():
    n = 0
    circles_list.clear() # Rebuilds list each time (might not be efficient)
    for x in x_coords:
        for y in y_coords:
            circles_list.append(draw_trader(trader_money[n],x,y,trader_colour[n],trader_batch))
            n += 1

# Draw the last two traders that have interacted, with a line in between
interact_list=[]
def highlight_last_trade(trader_A,trader_B):
    interact_list.clear()
    # Draw a line between the last two shapes that have interacted
    interact_list.append(shapes.Line(trader_x_coords[trader_A],trader_y_coords[trader_A],trader_x_coords[trader_B],trader_y_coords[trader_B],1,color=(255,255,255),batch=interact_batch))
    # Also highlight the two traders who have last traded in white
    circle_trader_A = draw_trader(trader_money[trader_A],trader_x_coords[trader_A],trader_y_coords[trader_A],(255,255,255),interact_batch)
    circle_trader_A_glow = draw_trader(trader_money[trader_A]*2,trader_x_coords[trader_A],trader_y_coords[trader_A],(255,255,255),interact_batch)
    circle_trader_A_glow.opacity = 100
    circle_trader_B = draw_trader(trader_money[trader_B],trader_x_coords[trader_B],trader_y_coords[trader_B],(255,255,255),interact_batch)
    circle_trader_B_glow = draw_trader(trader_money[trader_B]*2,trader_x_coords[trader_B],trader_y_coords[trader_B],(255,255,255),interact_batch)
    circle_trader_B_glow.opacity = 100
    interact_list.extend([circle_trader_A,circle_trader_A_glow,circle_trader_B,circle_trader_B_glow])

#  DEFINE THE FUNCTION TO UPDATE STATE
# ------------------------------------
# Includes making a trade event, drawing those circles which have changed,
# and showing a straight line between the two traders between who a trade has
# las occured.
def update(dt): # Passing dt as pyglet.clock.schedule_interval requires that a parameter is passed, but not used at the moment

    # Make a trading event happen
    trader_A,trader_B = trading_event()

    # Update the last two trader circles that have changes
    circles_list[trader_A] = draw_trader(trader_money[trader_A],trader_x_coords[trader_A],trader_y_coords[trader_A],trader_colour[trader_A],trader_batch)
    circles_list[trader_B] = draw_trader(trader_money[trader_B],trader_x_coords[trader_B],trader_y_coords[trader_B],trader_colour[trader_B],trader_batch)

    # Highlight the last trade
    highlight_last_trade(trader_A,trader_B)


# SET UP WINDOW AND START GAME RUNNING
# ------------------------------------

# Define and create the window
window = pyglet.window.Window(window_width,window_height,"Yard sale",fullscreen = True)

# Define the circles, draw them, then wait for enter to be pressed
circle_setup()
fps_display = pyglet.window.FPSDisplay(window=window)


# Allow for pausing and unpausing with spacebar (starts in paused state)
paused = True
@window.event
def on_key_press(symbol,modifiers):
    global paused
    if symbol == pyglet.window.key.SPACE:
        paused = (not paused)
        if paused:
            pyglet.clock.unschedule(update)
        else:
            pyglet.clock.schedule_interval(update,1.0/60)


@window.event
def on_draw():
    window.clear()
    trader_batch.draw()
    interact_batch.draw()
    fps_display.draw()


# Start the app
pyglet.app.run()
