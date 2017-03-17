#!/usr/bin/python3
import time, math, random
import sense_hat

"""
  Classic Snake!
    A snake game.  Eat the food! Don't crash with your body! 
  Modify the starting state in the `state` dict.

  Note: Requires sense_hat version 2.2.0 or later.
  Based on examples found at https://trinket.io/sense-hat
"""

state = { "snake_x" : [],
          "snake_y" : [],
          "snake_body_rgb" : (255,255,0),
          "snake_head_rgb" : (255,0,0),
          "food_x" : 2,
          "food_y" : 7,
          "food_rgb" : (0,255,50),
          "level" : 1,
          "last_mov" : sense_hat.DIRECTION_UP}

start_over_state = dict(state)

sense = sense_hat.SenseHat()

def restart():
  global state
  print("RIP",state["level"])
  sense.show_message(str(state["level"]))
  #Clean the state
  del state["snake_x"][:]
  del state["snake_y"][:]
  state = dict(start_over_state)
  add_new_position(4, 4)
  
  #New game starts after pressing the joystick
  while True:
    if len(sense.stick.get_events()) > 0:
      break
  
def setscreen():
  """Takes x and y vales and alters screen state. Does not 
  modify state."""
  snake_x = state["snake_x"]
  snake_y = state["snake_y"]

  sense.clear((50,100,150))
  sense.set_pixel(state["food_x"], state["food_y"], state["food_rgb"]) 
  
  for i in range(0,state["level"]-1):
    sense.set_pixel(snake_x[i], snake_y[i], state["snake_body_rgb"])
  sense.set_pixel(snake_x[state["level"]-1], snake_y[state["level"]-1], state["snake_head_rgb"])

def isInSnake(x,y):
  global state
  isIn = False
  for i in range(0, state["level"]): #
    if state["snake_x"][i] == x and state["snake_y"][i] == y :
      isIn = True
      break
  return isIn

def add_new_position(new_x, new_y):
  global state
  # Add the new state
  state["snake_x"].append(new_x)
  state["snake_y"].append(new_y)

  #The first element is dropped
  if len(state["snake_x"]) > state["level"] :
    del state["snake_x"][0]
  if len(state["snake_y"]) > state["level"] :
    del state["snake_y"][0]  

  print("X:",state["snake_x"])
  print("Y:",state["snake_y"])

def check_pos():
  """Checks for eating food and hitting enemies. Alters state but
  does not redraw screen.  Call setscreen() after this."""
  global state
  level = state["level"]
  snake_x = state["snake_x"][level-1]
  snake_y = state["snake_y"][level-1]
  food_x = state["food_x"]
  food_y = state["food_y"]

  if math.hypot(snake_x - food_x, snake_y - food_y) == 0.0:
    # Snake ate food
    state["level"] += 1
    add_new_position(snake_x, snake_y)
    # Set food to new location that's not under the snake
    while True:
      state["food_x"] = random.randint(0,7)
      state["food_y"] = random.randint(0,7)
      if not isInSnake(state["food_x"], state["food_y"]):
        break

"""Move the head of the snake with relation with its position"""
def move(x,y):
  global state
  pos = state["level"]-1
  new_x = (state["snake_x"][pos] + x) % 8
  new_y = (state["snake_y"][pos] + y) % 8
  collision = isInSnake(new_x, new_y)
  add_new_position(new_x, new_y)
  return collision;

"""The snake moves forward automatically. It only can turn.""" 
def move_direction(direction, auto):
  global state
  rip = False
  last_mov = state["last_mov"]
  if direction == sense_hat.DIRECTION_UP:
    if auto or (last_mov != sense_hat.DIRECTION_UP and last_mov != sense_hat.DIRECTION_DOWN) :
      state["last_mov"] = sense_hat.DIRECTION_UP
      rip = move(0,-1)
  elif direction == sense_hat.DIRECTION_DOWN:
    if auto or (last_mov != sense_hat.DIRECTION_UP and last_mov != sense_hat.DIRECTION_DOWN) :
      state["last_mov"] = sense_hat.DIRECTION_DOWN
      rip = move(0,1)
  elif direction == sense_hat.DIRECTION_RIGHT:
    if auto or (last_mov != sense_hat.DIRECTION_RIGHT and last_mov != sense_hat.DIRECTION_LEFT) : 
      state["last_mov"] = sense_hat.DIRECTION_RIGHT
      rip = move(1,0)
  elif direction == sense_hat.DIRECTION_LEFT:
    if auto or (last_mov != sense_hat.DIRECTION_RIGHT and last_mov != sense_hat.DIRECTION_LEFT) :
      state["last_mov"] = sense_hat.DIRECTION_LEFT
      rip = move(-1,0)
    
  if rip:
      restart()

def move_snake():
  global state
  move_direction(state["last_mov"], True)
  # Check to see if anything should happen
  setscreen()
  check_pos()
  setscreen()
       
def draw_snake(event):
  """Takes a keypress and redraws the screen"""
  global state
  if event.action == sense_hat.ACTION_RELEASED:
    # Ignore releases
    return
  else :
    move_direction(event.direction, False)
  # Check to see if anything should happen
  setscreen()
  check_pos()
  setscreen()

# Initial state
add_new_position(4, 4)#Initial snake placement
setscreen()

last_tick = round(time.time(),1) * 10

tick_move = 0
while True:
  # The snake moves faster in higher levels
  timer = 5 - (int)(state["level"] / 5)
  if timer < 1 :
    timer = 1
  tick = round(time.time(),1) * 10 
  
  if (tick % timer == tick_move) and (tick > last_tick):
    move_snake()
    last_tick = tick

  # Poll joystick for events. When they happen, redraw screen. 
  for event in sense.stick.get_events():
    #This avoids two movements in a very short period of time
    tick = round(time.time(),1) * 10 
    tick_move = (tick -1)  % timer
    draw_snake(event)
