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
    
_jconst(SCREEN_WIDTH=80)
_jconst(SCREEN_HEIGHT=25)
_jconst(VRAM_BASE=0xb8000)

def print_okay():
    _jput64(0xb8000, 0x2f592f412f4b2f4f)
    
def print_char(c, x, y, fg_col, bg_col):
    addr = VRAM_BASE+2*(x+y*SCREEN_WIDTH)
    color_byte = fg_col+16*bg_col
    _jput64(addr, c+256*color_byte)

def sebel_main():
    print_okay()
    print_char('W', 26, 12, Colors.WHITE, Colors.BLACK)
    print_char('e', 27, 12, Colors.WHITE, Colors.BLACK)
    print_char('l', 28, 12, Colors.WHITE, Colors.BLACK)
    print_char('c', 29, 12, Colors.WHITE, Colors.BLACK)
    print_char('o', 30, 12, Colors.WHITE, Colors.BLACK)
    print_char('m', 31, 12, Colors.WHITE, Colors.BLACK)
    print_char('e', 32, 12, Colors.WHITE, Colors.BLACK)
    print_char(' ', 33, 12, Colors.WHITE, Colors.BLACK)
    print_char('t', 34, 12, Colors.WHITE, Colors.BLACK)
    print_char('o', 35, 12, Colors.WHITE, Colors.BLACK)
    print_char(' ', 36, 12, Colors.WHITE, Colors.BLACK)
    print_char('B', 37, 12, Colors.WHITE, Colors.BLACK)
    print_char('a', 38, 12, Colors.WHITE, Colors.BLACK)
    print_char('r', 39, 12, Colors.WHITE, Colors.BLACK)
    print_char('e', 40, 12, Colors.WHITE, Colors.BLACK)
    print_char(' ', 41, 12, Colors.WHITE, Colors.BLACK)
    print_char('M', 42, 12, Colors.WHITE, Colors.BLACK)
    print_char('e', 43, 12, Colors.WHITE, Colors.BLACK)
    print_char('t', 44, 12, Colors.WHITE, Colors.BLACK)
    print_char('a', 45, 12, Colors.WHITE, Colors.BLACK)
    print_char('l', 46, 12, Colors.WHITE, Colors.BLACK)
    print_char(' ', 47, 12, Colors.WHITE, Colors.BLACK)
    print_char('P', 48, 12, Colors.BLUE, Colors.GREEN)
    print_char('y', 49, 12, Colors.YELLOW, Colors.GREEN)
    print_char('t', 50, 12, Colors.BLUE, Colors.GREEN)
    print_char('h', 51, 12, Colors.YELLOW, Colors.GREEN)
    print_char('o', 52, 12, Colors.BLUE, Colors.GREEN)
    print_char('n', 53, 12, Colors.YELLOW, Colors.GREEN)
