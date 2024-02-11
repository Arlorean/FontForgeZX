import os
import fontforge

filename = 'Spectrum.ch8'

file = open(filename, 'br')
bytes = file.read()

CH8_NUM_BYTES = 768

if len(bytes) != CH8_NUM_BYTES:
    print("File '"+filename+"' is not "+CH8_NUM_BYTES+" bytes in length")
    exit(-1)

NUM_CHARS = CH8_NUM_BYTES//8

CHAR_SIZE = 2048         # Character width and height in Font Units
PIXEL_SIZE = CHAR_SIZE//8 # Pixel width and height in Font Units

# Create a new font
font = fontforge.font()
font.em = CHAR_SIZE
font.ascent = 7*PIXEL_SIZE;
font.descent = 1*PIXEL_SIZE;

def create_pixel(pen, x, y):
    pen.moveTo((x+0)*PIXEL_SIZE,(y+0)*PIXEL_SIZE)
    pen.lineTo((x+0)*PIXEL_SIZE,(y+1)*PIXEL_SIZE)
    pen.lineTo((x+1)*PIXEL_SIZE,(y+1)*PIXEL_SIZE)
    pen.lineTo((x+1)*PIXEL_SIZE,(y+0)*PIXEL_SIZE)
    pen.closePath()

# Define a simple square glyph
def create_glyph(font, char, bytes):
    glyph = font.createChar(char)
    glyph.width = CHAR_SIZE

    pen = glyph.glyphPen()

    for y in range(0,8):
        byte = bytes[y]
        x = 0
        while byte != 0:
            if (byte & 1) == 1:
                create_pixel(pen, 7-x, 7-y-1)
            byte >>= 1
            x += 1


SPACE_CHAR = 32

for i in range(0, NUM_CHARS):
    charBytes = bytes[i*8:(i+1)*8]
    create_glyph(font, i+SPACE_CHAR, charBytes)

# Generate the TrueType font file
ttfFileName = os.path.splitext(filename)[0]+'.ttf'
font.generate(ttfFileName)
