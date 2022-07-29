#import board support libraries, including HID.
import board
import digitalio
import analogio
import usb_hid

#Libraries for the OLED Display
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import terminalio
import displayio
import busio

from time import sleep

#Libraries for communicating as a Keyboard device
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

#library for communicating as a gamepad
from hid_gamepad import Gamepad

from adafruit_hid.mouse import Mouse
mouse = Mouse(usb_hid.devices)

from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.consumer_control import ConsumerControl

mediacontrol = ConsumerControl(usb_hid.devices)

keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)
gp = Gamepad(usb_hid.devices)

#Create a collection of GPIO pins that represent the buttons
#This includes the digital pins for the Directional Pad.
#They can be used as regular buttons if using the analog inputs instead
button_pins = (board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7,board.GP10, board.GP11,
               board.GP12, board.GP13, board.GP14, board.GP15, board.GP16, board.GP17)



# Map the buttons to button numbers on the Gamepad.
# gamepad_buttons[i] will send that button number when buttons[i]
# is pushed.
gamepad_buttons = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)

#Keyboard Mode Button Definitions
keyboard_buttons = {0 : Keycode.UP_ARROW, 1 : Keycode.LEFT_ARROW, 2 : Keycode.DOWN_ARROW, 3 : Keycode.RIGHT_ARROW,
                  4 : Keycode.LEFT_CONTROL, 5 : Keycode.SPACE, 6 : Keycode.W, 7 : Keycode.ENTER, 8 : Keycode.LEFT_ALT
                    , 9 : Keycode.ENTER, 10 : Keycode.ENTER, 11 : Keycode.ENTER, 12 : Keycode.ENTER, 13 : Keycode.ENTER
                    , 14 : Keycode.ENTER, 15 : Keycode.ENTER}

#FPS Mode Button Definitions
fps_buttons = {0 : Keycode.W, 1 : Keycode.A, 2 : Keycode.S, 3 : Keycode.D,
                  4 : Keycode.LEFT_CONTROL, 5 : Keycode.SPACE, 6 : Keycode.LEFT_ALT, 7 : Keycode.ENTER,
               8 : Keycode.ENTER, 9 : Keycode.ENTER, 10 : Keycode.ENTER, 11 : Keycode.ENTER, 12 : Keycode.ENTER
               , 13 : Keycode.ENTER, 14 : Keycode.ENTER, 15 : Keycode.ENTER}

#List of defind mode names
mode_names = {1 : 'Gamepad', 2 : 'Keyboard', 3 : 'FPS', 4 : "Mouse", 5 : "Multimedia"}

#Set Default Mode To 1
mode = 1

#Define OLED Parameters
WIDTH = 128
HEIGHT = 64
BORDER = 5

buttons = [digitalio.DigitalInOut(pin) for pin in button_pins]

modeChangeButton = digitalio.DigitalInOut(board.GP22)
modeChangeButton.direction = digitalio.Direction.INPUT
modeChangeButton.pull = digitalio.Pull.UP

#Initialize The Buttons
for button in buttons:
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    
# Setup for Analog Joystick as X and Y
ax = analogio.AnalogIn(board.GP26)
ay = analogio.AnalogIn(board.GP27)

displayio.release_displays()


# Use for I2C for display
i2c = busio.I2C(board.GP9, board.GP8)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

# Equivalent of Arduino's map() function.
def range_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
  

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# Make the display context
splash = displayio.Group()
display.show(splash)

# Draw a label

text = "Mode : " + str(mode)
text_area = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=3, y=3
)
splash.append(text_area)
text = mode_names[mode]
text_area = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=3, y=23
)
splash.append(text_area)

def debounce():
    sleep(0.2)

while True:
    #Check to see if the mode change button is pressed
    if  modeChangeButton.value:
        mode = mode + 1
        if mode > 5:
            mode = 1
        sleep(1)
        splash = displayio.Group()
        display.show(splash)
        # Draw a smaller inner rectangle
        inner_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = 0x000000  # Black
        inner_sprite = displayio.TileGrid(
            inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER
        )
        splash.append(inner_sprite)
        display.show(splash)
        # Draw a label
        text = "Mode : " + str(mode)
        text_area = label.Label(
            terminalio.FONT, text=text, color=0xFFFFFF, x=3, y=3
        )
        splash.append(text_area)
        text = mode_names[mode]
        text_area = label.Label(
            terminalio.FONT, text=text, color=0xFFFFFF, x=3, y=23
        )
        splash.append(text_area)  
 
    if mode == 1:
        # Check value of up, down, left, and right buttons
        # and set the joystick values appropriately.
        # can be replaced with values from analog stick instead
        setx = 0
        sety = 0
        #Not keyboard presses for directional
        #So check them seperately first
        if not buttons[0].value:
            sety = -127
        if not buttons[2].value:
            sety = 127
        if not buttons[1].value:
            setx = -127
        if not buttons[3].value:
            setx = 127
        #Set Joystick movements
        gp.move_joysticks(
            x=setx,
            y=sety,
        )
        
        # Go through all the button definitions, and
        # press or release as appropriate
        for i, button in enumerate(buttons):
            if i > 3: #Skip the first 4, since they're the directionals
                gamepad_button_num = gamepad_buttons[i - 4] # Minus 4 to ignore directionals
                if button.value:
                    gp.release_buttons(gamepad_button_num)
                else:
                    gp.press_buttons(gamepad_button_num)
        
    if mode == 2: # Keyboard Mode
            
        for i, button in enumerate(buttons):
            if button.value:
                keyboard.release(keyboard_buttons[i])
            else:
                keyboard.press(keyboard_buttons[i]) 
    
    #FPS Mode
    if mode == 3:
        for i, button in enumerate(buttons):
            gamepad_button_num = gamepad_buttons[i]
            if button.value:
                keyboard.release(fps_buttons[i])
            else:
                keyboard.press(fps_buttons[i])
                
    if mode == 4:
        if not buttons[0].value:
            mouse.move(y=-4)
        if not buttons[2].value:
            mouse.move(y=4)
        if not buttons[1].value:
            mouse.move(x=-4)
        if not buttons[3].value:
            mouse.move(x=4)
        if not buttons[4].value:
            mouse.click(Mouse.LEFT_BUTTON)
            sleep(0.2)
        if not buttons[5].value:
            mouse.click(Mouse.RIGHT_BUTTON)
            sleep(0.2)

    if mode == 5:
        if not buttons[0].value:
            mediacontrol.send(ConsumerControlCode.VOLUME_INCREMENT)
            debounce()
        if not buttons[2].value:
            mediacontrol.send(ConsumerControlCode.VOLUME_DECREMENT)
            debounce()
        if not buttons[1].value:
            mediacontrol.send(ConsumerControlCode.SCAN_PREVIOUS_TRACK)
            debounce()
        if not buttons[3].value:
            mediacontrol.send(ConsumerControlCode.SCAN_NEXT_TRACK)
            debounce()
        if not buttons[4].value:
            mediacontrol.send(ConsumerControlCode.PLAY_PAUSE)
            debounce()
        if not buttons[5].value:
            mediacontrol.send(ConsumerControlCode.STOP)
            debounce()
        if not buttons[9].value:
            mediacontrol.send(ConsumerControlCode.MUTE)
            debounce()
