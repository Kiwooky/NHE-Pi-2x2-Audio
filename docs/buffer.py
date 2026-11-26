# Draws docs/buffer.svg. Run from the repo root: python3 docs/buffer.py
# Buffer board for NHE Pi 2x2 Audio: one TL074, two instrument inputs, two outputs.
import html
o = []
a = o.append
W, H = 1280, 1290
INK, MUTE, ACC, BLUE, RED = '#212121', '#7b7b7b', '#883996', '#1e7bd6', '#c0392b'

def t(x, y, s, size=13, anchor='start', color=INK, weight='400', italic=False):
    st = ' font-style="italic"' if italic else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}"{st}>{html.escape(s)}</text>')

def wire(*pts, color=INK, w=2):
    d = ' '.join(f'{x},{y}' for x, y in pts)
    a(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="round"/>')

def dot(x, y):
    a(f'<circle cx="{x}" cy="{y}" r="4" fill="{INK}"/>')

def res_h(x, y, ref, val, L=64):
    # leads 12, zigzag 40
    z = [(x, y), (x + 12, y)]
    for i in range(6):
        z.append((x + 12 + (i + 0.5) * 40 / 6, y + (-7 if i % 2 == 0 else 7)))
    z += [(x + 52, y), (x + L, y)]
    wire(*z)
    t(x + L / 2, y - 14, f'{ref}  {val}', 12, 'middle')

def res_v(x, y, ref, val, L=64, side='right'):
    z = [(x, y), (x, y + 12)]
    for i in range(6):
        z.append((x + (-7 if i % 2 == 0 else 7), y + 12 + (i + 0.5) * 40 / 6))
    z += [(x, y + 52), (x, y + L)]
    wire(*z)
    if side == 'right':
        t(x + 14, y + L / 2 + 4, f'{ref}  {val}', 12)
    else:
        t(x - 14, y + L / 2 + 4, f'{ref}  {val}', 12, 'end')

def cap_h(x, y, ref, val, polar=False, L=44):
    wire((x, y), (x + 18, y)); wire((x + 26, y), (x + L, y))
    a(f'<line x1="{x+18}" y1="{y-12}" x2="{x+18}" y2="{y+12}" stroke="{INK}" stroke-width="2.5"/>')
    if polar:
        a(f'<path d="M{x+30},{y-12} Q{x+25},{y} {x+30},{y+12}" fill="none" stroke="{INK}" stroke-width="2.5"/>')
        t(x + 10, y - 9, '+', 12, 'middle', weight='700')
    else:
        a(f'<line x1="{x+26}" y1="{y-12}" x2="{x+26}" y2="{y+12}" stroke="{INK}" stroke-width="2.5"/>')
    t(x + L / 2, y - 18, f'{ref}  {val}', 12, 'middle')

def cap_v(x, y, ref, val, polar=False, L=44, side='right'):
    wire((x, y), (x, y + 18)); wire((x, y + 26), (x, y + L))
    a(f'<line x1="{x-12}" y1="{y+18}" x2="{x+12}" y2="{y+18}" stroke="{INK}" stroke-width="2.5"/>')
    if polar:
        a(f'<path d="M{x-12},{y+30} Q{x},{y+25} {x+12},{y+30}" fill="none" stroke="{INK}" stroke-width="2.5"/>')
        t(x - 16, y + 16, '+', 12, 'middle', weight='700')
    else:
        a(f'<line x1="{x-12}" y1="{y+26}" x2="{x+12}" y2="{y+26}" stroke="{INK}" stroke-width="2.5"/>')
    if side == 'right':
        t(x + 16, y + L / 2 + 4, f'{ref}  {val}', 12)
    else:
        t(x - 16, y + L / 2 + 4, f'{ref}  {val}', 12, 'end')

def gnd(x, y):
    wire((x, y), (x, y + 8))
    for i, w in enumerate((14, 9, 4)):
        a(f'<line x1="{x-w}" y1="{y+8+i*5}" x2="{x+w}" y2="{y+8+i*5}" stroke="{INK}" stroke-width="2"/>')

def opamp(x, y, name):
    # + input at (x, y), - input at (x, y+40), output at (x+100, y+20)
    a(f'<polygon points="{x},{y-30} {x},{y+70} {x+100},{y+20}" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
    t(x + 10, y + 5, '+', 16, weight='700'); t(x + 11, y + 45, '−', 16, weight='700')
    t(x + 32, y + 25, name, 11, color=MUTE)

def jack(x, y, label, right=False, above=False, below=False):
    a(f'<circle cx="{x}" cy="{y}" r="9" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
    a(f'<circle cx="{x}" cy="{y}" r="2.5" fill="{INK}"/>')
    if above:
        t(x, y - 18, label, 13, 'middle', weight='700')
    elif below:
        t(x, y + 28, label, 13, 'middle', weight='700')
    elif right:
        t(x + 16, y + 5, label, 13, weight='700')
    else:
        t(x - 16, y + 5, label, 13, 'end', weight='700')

def throw(x, y):
    a(f'<circle cx="{x}" cy="{y}" r="4" fill="#fff" stroke="{INK}" stroke-width="2"/>')

def section(y, title, sub):
    a(f'<rect x="20" y="{y}" width="{W-40}" height="2" fill="#e4e4e8"/>')
    t(40, y + 32, title, 19, weight='700')
    t(40, y + 54, sub, 13, color=MUTE)

a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Helvetica, Arial, sans-serif">')
a(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
t(40, 48, 'NHE Pi 2x2 Audio: buffer board (one TL074)', 26, weight='700')
t(40, 76, 'High-impedance instrument inputs in front of the PCM1808, and a pad + buffer after the PCM5102. Runs on ±12 V made from the Pi’s 5 V.', 15, color='#575757')

# ---------------- input channel ----------------
Y = 96
section(Y, 'Input  × 2', 'TL074 A: input L (pins 1–3)  ·  TL074 B: input R (pins 5–7)  ·  guitar → this → ADC board L / R')
y = Y + 140
jack(70, y, 'IN')
wire((79, y), (110, y))
res_h(110, y, 'R1', '1k')                     # 110..174
wire((174, y), (210, y)); dot(210, y)
res_v(210, y, 'R2', '10M', L=70, side='left'); gnd(210, y + 70)
wire((210, y), (240, y))
cap_h(240, y, 'C1', '100n film')              # 240..284
wire((284, y), (340, y)); dot(340, y)
# S1, input Z: SP3T from the + input to three resistors to VB
wire((340, y), (340, y + 40)); dot(340, y + 40)
a(f'<line x1="340" y1="{y+40}" x2="372" y2="{y+62}" stroke="{INK}" stroke-width="2.5"/>')
for i, (ref, val) in enumerate((('R3a', '1M'), ('R3b', '2.2M'), ('R3c', '4.7M'))):
    xx = 380 + i * 76
    throw(xx, y + 68)
    wire((xx, y + 72), (xx, y + 86))
    res_v(xx, y + 86, ref, val, L=64)
    gnd(xx, y + 150)
t(456, y + 50, 'S1  input Z (SP3T or rotary), to GND', 12, 'middle', ACC, '700')
# op-amp A
wire((340, y), (700, y))
opamp(700, y, '¼ TL074 A')                    # + (700,y), − (700,y+40), out (800,y+20)
yo = y + 20
wire((800, yo), (860, yo)); dot(860, yo)
# feedback: R4 with C9 across it, from the output back to the − input
fy = y + 110
wire((860, yo), (860, fy)); dot(860, fy)
res_h(730, fy, 'R4', '10k', L=130)            # 730..860
wire((730, fy), (670, fy), (670, y + 40), (700, y + 40)); dot(710, fy)
t(765, fy + 72, 'follower (unity gain)', 11, 'middle', MUTE)
cap_h(730, fy + 44, 'C9', '100p', L=130)
wire((730, fy + 44), (710, fy + 44), (710, fy)); wire((860, fy + 44), (860, fy))
# out to the ADC board
wire((860, yo), (900, yo))
cap_h(900, yo, 'C3', '10µ NP')      # 900..944
wire((944, yo), (970, yo))
res_h(970, yo, 'R6', '100R')                  # 970..1034
wire((1034, yo), (1070, yo)); dot(1070, yo)
res_v(1070, yo, 'R7', '100k', L=64); gnd(1070, yo + 64)
wire((1070, yo), (1140, yo)); jack(1149, yo, 'to ADC L / R', right=True)
t(1200, yo + 30, '(3.5 mm tip / ring)', 11, 'middle', MUTE)

# ---------------- output channel ----------------
Y2 = 586
section(Y2, 'Output  × 2', 'TL074 C: output L (pins 8–10)  ·  TL074 D: output R (pins 12–14)  ·  DAC board L / R → this → pedals, amp')
y = Y2 + 176
jack(70, y, 'from DAC L / R', below=True)
wire((79, y), (110, y)); dot(110, y)
res_h(110, y, 'R8', '10k')                    # 110..174
wire((174, y), (220, y)); dot(220, y)
res_v(220, y, 'R9', '2.2k', L=64, side='left'); gnd(220, y + 64)
# S3: INST (from the pad) or LINE (straight from the DAC)
wire((220, y), (300, y)); throw(304, y)
wire((110, y), (110, y - 52), (300, y - 52)); throw(304, y - 52)
t(304, y + 24, 'INST', 11, 'middle', ACC, '700'); t(304, y - 64, 'LINE', 11, 'middle', ACC, '700')
dot(350, y - 26)
a(f'<line x1="350" y1="{y-26}" x2="310" y2="{y-6}" stroke="{INK}" stroke-width="2.5"/>')
t(380, y - 64, 'S3  level (SPDT)', 12, 'start', ACC, '700')
wire((350, y - 26), (380, y - 26))
cap_h(380, y - 26, 'C4', '1µ film')          # 380..424
wire((424, y - 26), (470, y - 26)); dot(470, y - 26)
res_v(470, y - 26, 'R10', '1M', L=64); gnd(470, y + 38)
wire((470, y - 26), (700, y - 26))
opamp(700, y - 26, '¼ TL074 C')               # + (700, y-26), − (700, y+14), out (800, y-6)
yo = y - 6
wire((800, yo), (860, yo)); dot(860, yo)
wire((860, yo), (860, y + 60), (670, y + 60), (670, y + 14), (700, y + 14))
t(765, y + 80, 'follower (unity gain)', 11, 'middle', MUTE)
wire((860, yo), (900, yo))
cap_h(900, yo, 'C5', '10µ NP')
wire((944, yo), (970, yo))
res_h(970, yo, 'R11', '100R')
wire((1034, yo), (1070, yo)); dot(1070, yo)
res_v(1070, yo, 'R12', '100k', L=64); gnd(1070, yo + 64)
wire((1070, yo), (1140, yo)); jack(1149, yo, 'OUT L / R', right=True)
t(1185, yo + 30, '(¼" jacks)', 11, 'middle', MUTE)

# ---------------- power ----------------
Y3 = 920
section(Y3, 'Power: ±12 V from the Pi’s 5 V', 'One supply for the whole unit: the Pi’s USB-C charger. An isolated DC-DC module makes ±12 V; its 0 V joins audio GND.')
y = Y3 + 130
a(f'<rect x="40" y="{y-22}" width="96" height="44" rx="6" fill="#fff" stroke="{INK}" stroke-width="2"/>')
t(88, y - 3, 'Pi header', 12, 'middle', weight='700'); t(88, y + 13, '5 V pin 4', 11, 'middle', MUTE)
wire((136, y), (200, y)); dot(200, y)
cap_v(200, y, 'C10', '10µ', polar=True, L=44, side='left'); gnd(200, y + 44)
wire((200, y), (260, y))
# module box
mx, my = 260, y - 40
a(f'<rect x="{mx}" y="{my}" width="150" height="150" rx="8" fill="#f4eef6" stroke="{ACC}" stroke-width="2.5"/>')
t(mx + 75, my + 64, 'U2', 13, 'middle', ACC, '700')
t(mx + 75, my + 82, 'B0512S-1W', 12, 'middle', ACC, '700')
t(mx + 75, my + 98, '5 V → ±12 V, isolated', 10, 'middle', MUTE)
t(mx + 8, y + 4, 'Vin', 11); t(mx + 8, y + 104, 'GND', 11)
wire((mx, y + 100), (230, y + 100)); gnd(230, y + 100)
t(mx + 142, y + 4, '+Vo', 11, 'end'); t(mx + 142, y + 54, '0V', 11, 'end'); t(mx + 142, y + 104, '−Vo', 11, 'end')
ox = mx + 150
# +12 rail
wire((ox, y), (440, y)); res_h(440, y, 'R13', '10R'); wire((504, y), (560, y)); dot(560, y)
cap_v(560, y, 'C6', '100µ', polar=True, L=44); gnd(560, y + 44)
wire((560, y), (640, y)); t(650, y + 5, '+12 V → TL074 pin 4', 12, color=RED, weight='700')
# 0 V
wire((ox, y + 50), (440, y + 50)); gnd(440, y + 50)
t(600, y + 56, 'audio GND (one point)', 11, color=MUTE)
# -12 rail
yn = y + 100
wire((ox, yn), (440, yn)); res_h(440, yn, 'R14', '10R'); wire((504, yn), (560, yn)); dot(560, yn)
cap_v(560, yn, 'C8', '100µ, + side to GND', L=44); gnd(560, yn + 44)
wire((560, yn), (640, yn)); t(650, yn + 5, '−12 V → TL074 pin 11', 12, color=BLUE, weight='700')
t(40, y + 196, 'At the chip: C7 100n from pin 4 to GND and C11 100n from pin 11 to GND.  Module draws about 0.25 A from the Pi’s 5 V.', 12)

# TL074 pinout + notes
bx = 830
a(f'<rect x="{bx}" y="{Y3+76}" width="410" height="196" rx="10" fill="#f4f4f6"/>')
t(bx + 16, Y3 + 100, 'TL074 (DIP-14), top view', 13, weight='700')
left = ['1  out A → C3 (in L)', '2  − A', '3  + A', '4  +12 V', '5  + B', '6  − B', '7  out B → C3 (in R)']
right = ['14  out D → C5 (out R)', '13  − D', '12  + D', '11  −12 V', '10  + C', '9  − C', '8  out C → C5 (out L)']
for i, s in enumerate(left):
    t(bx + 16, Y3 + 124 + i * 20, s, 12)
for i, s in enumerate(right):
    t(bx + 220, Y3 + 124 + i * 20, s, 12)
a('</svg>')
open('docs/buffer.svg', 'w').write('\n'.join(o))
