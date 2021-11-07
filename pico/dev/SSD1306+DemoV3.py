 # Display Image & text on I2C driven ssd1306 OLED display 
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
import math
import utime
WIDTH  = 128                                            # oled display width
HEIGHT = 64                                             # oled display height

# Explicit Method
sda=machine.Pin(2)
scl=machine.Pin(3)
i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)
#  print(i2c.scan())
from ssd1306 import SSD1306_I2C
oled = SSD1306_I2C(128, 64, i2c)

# Raspberry Pi logo as 32x32 bytearray
buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

# Load the raspberry pi logo into the framebuffer (the image is 32x32)
fb = framebuf.FrameBuffer(buffer, 32, 32, framebuf.MONO_HLSB)

def blk():
    oled.fill(0)
    oled.show()
    
def horiz(l,t,r,c):  # left, right , top
    n = r-l+1        # Horizontal line
    for i in range(n):
        oled.pixel(l + i, t, c)

def vert(l,t,b,c):   # left, top, bottom
    n = b-t+1        # Vertical line
    for i in range(n):
        oled.pixel(l, t+i,c)

def box(l,t,r,b,c):  # left, top, right, bottom
    horiz(l,t,r,c)   # Hollow rectangle
    horiz(l,b,r,c)
    vert(l,t,b,c)
    vert(r,t,b,c)
    
def ring2(cx,cy,r,c):   # Centre (x,y), radius, colour
    for angle in range(0, 90, 2):  # 0 to 90 degrees in 2s
        y3=int(r*math.sin(math.radians(angle)))
        x3=int(r*math.cos(math.radians(angle)))
        oled.pixel(cx-x3,cy+y3,c)  # 4 quadrants
        oled.pixel(cx-x3,cy-y3,c)
        oled.pixel(cx+x3,cy+y3,c)
        oled.pixel(cx+x3,cy-y3,c)
        
# Clear the oled display in case it has junk on it.
oled.fill(0) # Black

# Blit the image from the framebuffer to the oled display
oled.blit(fb, 96, 0)

# Basic stuff
oled.text("Raspberry Pi",5,5)
oled.text("Pico",5,15)
oled.pixel(10,60,1)
oled.rect(5,32,20,10,1)
oled.fill_rect(40,40,20,10,1)
oled.line(77,45,120,60,1)
oled.rect(75,32,40,10,1)

ring2(50,43,20,1)  # Empty circle             
# Finally update the oled display so the image & text is displayed
oled.show()
utime.sleep(3)

# Bouncing Raspberry
oled.fill(0) # Black
dx = 1
dy = 1
x = 13
y = 10
c = 1  # Colour White
for loop in range(250):
    oled.blit(fb, x, y)
    x = x + dx
    y = y + dy
    if (x == 95) or (x == 1):
        dx = dx * -1
    if (y == 31) or (y == 1):
        dy = dy * -1
    box(4,0,123,63,c)
    oled.show()
oled.fill(0) # Black
oled.show()

# Scrolling text on Sine curve
# Modified from a method by Tony DiCola
msg = 'Pico + SSD1306 is Magic!'
f_width  = 8   # Font width in pixels
f_height = 8   # Font Height in pixels
amp = 50   # Amplitude of sin wave
freq = 1    # Screen cycles (360 degrees)  
pos = WIDTH  # X position of the first character in the msg.
msg_len_px = len(msg) * f_width  # Pixel width of the msg.
# Extra wide lookup table - calculate once to speed things up
y_table = [0] * (WIDTH+f_width) # 1 character extra
for i in range(len(y_table)):
    p = i / (WIDTH-1)  # Compute current position
    # Create lookup table of  y co-ordinates 
    y_table[i] = int(((amp/2.0) * math.sin(2.0*math.pi*freq*p)) + (amp/2.0))
    
# Main loop:
finish = utime.ticks_ms() + 40000 # 40 seconds
while utime.ticks_ms() < finish:
    # Start again if msg finished
    pos -= 1
    if pos <= -msg_len_px:
        pos = WIDTH
    # Go through each character in the msg.
    blk()
    for i in range(len(msg)):
        char = msg[i]
        char_x = pos + (i * f_width)  # Character's X position on the screen.
        if -f_width <= char_x < WIDTH:
            # If character is visible, draw it.
            oled.text(char, char_x + 5, y_table[char_x + f_width], 1)
    oled.show()
    utime.sleep(0.08)
    
# Tidy up
blk() 

