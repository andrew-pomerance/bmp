_jenum('Colors',
    BLACK       = 0,
    BLUE        = 1,
    GREEN       = 2,
    CYAN        = 3,
    RED         = 4,
    MAGENTA     = 5,
    BROWN       = 6,
    LIGHT_GRAY  = 7,
    DARK_GRAY   = 8,
    LIGHT_BLUE  = 9,
    LIGHT_GREEN = 10,
    LIGHT_CYAN  = 11,
    LIGHT_RED   = 12,
    PINK        = 13,
    YELLOW      = 14,
    WHITE       = 15)
    
def print_okay():
    _jput64(0xb8000, 0x2f592f412f42f4f)
    
_jconst(SCREEN_WIDTH=80)
_jconst(SCREEN_HEIGHT=25)
_jconst(VRAM_BASE=0xb8000)
    
def print_char(c, x, y, fg_col, bg_col):
    addr = VRAM_BASE+2*(x+y*SCREEN_WIDTH)
    color_byte = fg_col+16*bg_col
    _jput64(addr, c+256*color_byte)

def sebel_main():
    print_char('W', 30, 12, Colors.WHITE, Colors.BLACK)
#     print_char('e', 31, 12, Colors.WHITE, Colors.BLACK)
#     print_char('l', 32, 12, Colors.WHITE, Colors.BLACK)
#     print_char('c', 33, 12, Colors.WHITE, Colors.BLACK)
#     print_char('o', 34, 12, Colors.WHITE, Colors.BLACK)
#     print_char('m', 35, 12, Colors.WHITE, Colors.BLACK)
#     print_char('e', 36, 12, Colors.WHITE, Colors.BLACK)
#     print_char(' ', 37, 12, Colors.WHITE, Colors.BLACK)
#     print_char('t', 38, 12, Colors.WHITE, Colors.BLACK)
#     print_char('o', 39, 12, Colors.WHITE, Colors.BLACK)
#     print_char(' ', 40, 12, Colors.WHITE, Colors.BLACK)
#     print_char('B', 41, 12, Colors.WHITE, Colors.BLACK)
#     print_char('a', 42, 12, Colors.WHITE, Colors.BLACK)
#     print_char('r', 43, 12, Colors.WHITE, Colors.BLACK)
#     print_char('e', 44, 12, Colors.WHITE, Colors.BLACK)
#     print_char(' ', 45, 12, Colors.WHITE, Colors.BLACK)
#     print_char('M', 46, 12, Colors.WHITE, Colors.BLACK)
#     print_char('e', 47, 12, Colors.WHITE, Colors.BLACK)
#     print_char('t', 48, 12, Colors.WHITE, Colors.BLACK)
#     print_char('a', 49, 12, Colors.WHITE, Colors.BLACK)
#     print_char('l', 50, 12, Colors.WHITE, Colors.BLACK)
#     print_char(' ', 51, 12, Colors.WHITE, Colors.BLACK)
#     print_char('P', 52, 12, Colors.BLUE, Colors.BLACK)
#     print_char('y', 53, 12, Colors.YELLOW, Colors.BLACK)
#     print_char('t', 54, 12, Colors.BLUE, Colors.BLACK)
#     print_char('h', 55, 12, Colors.YELLOW, Colors.BLACK)
#     print_char('o', 56, 12, Colors.BLUE, Colors.BLACK)
#     print_char('n', 57, 12, Colors.YELLOW, Colors.BLACK)
