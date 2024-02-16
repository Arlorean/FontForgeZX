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

# Create mark and mkmk lookup tables
scriptLanguages = (('DFLT',('dflt')),('latn',('dflt')))

# NOTE: Must add 'mkmk' feature first, before 'mark' so it ends up at the bottom of the list(!)
font.addLookup("mkmk-table", "gpos_mark2mark", None, (('mkmk',scriptLanguages),))
font.addLookupSubtable("mkmk-table", "mkmk-subtable")
font.addAnchorClass("mkmk-subtable", "mkmk")

font.addLookup("mark-table", "gpos_mark2base", None, (('mark',scriptLanguages),))
font.addLookupSubtable("mark-table", "mark-subtable")
font.addAnchorClass("mark-subtable", "mark")


def create_pixel(pen, x, y, xscale):
    pen.moveTo((x+0)*PIXEL_SIZE*xscale,(y+0)*PIXEL_SIZE)
    pen.lineTo((x+0)*PIXEL_SIZE*xscale,(y+1)*PIXEL_SIZE)
    pen.lineTo((x+1)*PIXEL_SIZE*xscale,(y+1)*PIXEL_SIZE)
    pen.lineTo((x+1)*PIXEL_SIZE*xscale,(y+0)*PIXEL_SIZE)
    pen.closePath()

def create_byte(pen, x, y, byte, xscale):
    while byte != 0:
        if (byte & 1) == 1:
            create_pixel(pen, x, y, xscale)
        byte >>= 1
        x -= 1

# Define a simple square glyph
def create_glyph(font, char, bytes, width, xscale):
    glyph = font.createChar(char)

    pen = glyph.glyphPen()

    y = len(bytes)-2
    for byte in bytes:
        create_byte(pen, width-1, y, byte, xscale)
        y -= 1

    return glyph


HALF_WIDTH = 32 # Half width forms of ASCII 
FULL_WIDTH = 0xFF00 # Full width forms of ASCII 

for i in range(0, NUM_CHARS):
    charBytes = bytes[i*8:(i+1)*8]

    glyph = create_glyph(font, i+HALF_WIDTH, charBytes, 8, 0.5)
    glyph.width = CHAR_SIZE//2

    glyph = create_glyph(font, i+FULL_WIDTH, charBytes, 8, 1)
    glyph.width = CHAR_SIZE


DIACRITIC_MARKS = 0x0300 # Combining Diacritical Marks

for i in range(0, 16):
    charBytes = [i]
    glyph = create_glyph(font, i+DIACRITIC_MARKS, charBytes, 4, 1)
    glyph.glyphname = "mark"+str(i)
    glyph.width = 0 #CHAR_SIZE//2
    
    glyph.addAnchorPoint("mark", "mark", 0, -256)

    glyph.addAnchorPoint("mkmk", "basemark", 0, 0)
    glyph.addAnchorPoint("mkmk", "mark", 0, -256)


PUA = 0xE000 # Private Use Area

for i in range(0, 16):
    charBytes = [i]
    glyph = create_glyph(font, i+PUA, charBytes, 4, 1)
    glyph.glyphname = "base"+str(i)
    glyph.width = CHAR_SIZE//2

    glyph.addAnchorPoint("mark", "base", 0, 0)


# Save font file
sfdFileName = os.path.splitext(filename)[0]+'.sfd'
font.save(sfdFileName)

# Generate the TrueType font file
ttfFileName = os.path.splitext(filename)[0]+'.ttf'
font.generate(ttfFileName)
