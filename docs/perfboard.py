# Draws docs/perfboard.svg: the whole 2x2 board on pad-per-hole perfboard
# (40 x 35 holes, about 10 x 9 cm), top view and solder-side view.
# It also checks the layout: no two nets share a hole, and every net is connected.
# Run from the repo root: python3 docs/perfboard.py
import html, sys

COLS, ROWS = 40, 35
P = 24                      # px per hole
GND, VP, VN, V5, V5B = 'GND', '+12V', '-12V', '5V', '5V-B'

# ---------- parts: (ref, kind, value, [(x, y, net), ...]) ----------
parts = []
DX, DY = -11, -16          # the buffer and power block moved up-left from the first layout
def part(ref, kind, val, *pins, shift=True):
    if shift:
        pins = [(x + DX, y + DY, n) for x, y, n in pins]
    parts.append((ref, kind, val, list(pins)))

# Digital: converter-board sockets (columns) and the Pi header
part('J4', 'sock', 'ADC board', (21, 23, 'MCK'), (21, 24, 'DATA'), (21, 25, 'BCK'), (21, 26, 'LRCK'), (21, 27, 'NC_VDD33'), (21, 28, GND), shift=False)
part('J2', 'sock', 'DAC board', (25, 23, 'MCK'), (25, 24, 'BCK'), (25, 25, 'DOUT'), (25, 26, 'LRCK'), (25, 27, GND), (25, 28, V5), shift=False)
part('J1', 'hdr', 'to Pi', (17, 33, 'DATA'), (18, 33, 'BCK'), (19, 33, 'LRCK'), (20, 33, GND), (21, 33, V5), (22, 33, 'DOUT'), shift=False)
# TL074, pins 1-7 down the left (x 28), 14-8 down the right (x 31)
L, R = 28, 31     # first-layout coordinates (shifted by part())
part('U1', 'dip', 'TL074',
     (L, 18, 'OUTA'), (L, 19, 'OUTA'), (L, 20, 'INPA'), (L, 21, VP), (L, 22, 'INPB'), (L, 23, 'OUTB'), (L, 24, 'OUTB'),
     (R, 24, 'OUTC'), (R, 23, 'OUTC'), (R, 22, 'INPC'), (R, 21, VN), (R, 20, 'INPD'), (R, 19, 'OUTD'), (R, 18, 'OUTD'))
# Input L (TL074 A)
part('R1a', 'r', '1k', (15, 20, 'IN_L'), (16, 20, 'X1A'))
part('C1a', 'film', '100n', (17, 20, 'X1A'), (19, 20, 'INPA'))
part('R2a', 'r', '1M', (22, 20, 'INPA'), (22, 21, GND))
part('C3a', 'np', '10µ NP', (27, 18, 'OUTA'), (26, 18, 'X3A'))
part('R6a', 'r', '100R', (24, 18, 'X3A'), (23, 18, 'ADC_L'))
part('R7a', 'r', '100k', (22, 18, 'ADC_L'), (22, 17, GND))
# Input R (TL074 B)
part('R1b', 'r', '1k', (15, 22, 'IN_R'), (16, 22, 'X1B'))
part('C1b', 'film', '100n', (17, 22, 'X1B'), (19, 22, 'INPB'))
part('R2b', 'r', '1M', (24, 22, 'INPB'), (24, 21, GND))
part('C3b', 'np', '10µ NP', (27, 24, 'OUTB'), (26, 24, 'X3B'))
part('R6b', 'r', '100R', (24, 24, 'X3B'), (23, 24, 'ADC_R'))
part('R7b', 'r', '100k', (22, 24, 'ADC_R'), (22, 25, GND))
# Output R (TL074 D)
part('C5d', 'np', '10µ NP', (32, 18, 'OUTD'), (33, 18, 'X6D'))
part('R11d', 'r', '100R', (34, 18, 'X6D'), (35, 18, 'OUT_R'))
part('R12d', 'r', '100k', (37, 18, 'OUT_R'), (37, 17, GND))
part('R10d', 'r', '1M', (33, 20, 'INPD'), (33, 21, GND))
part('C4d', 'film', '1µ', (36, 20, 'INPD'), (39, 20, 'COM_R'))
part('R8d', 'r', '10k', (45, 20, 'D1R'), (46, 20, 'D2R'))
part('R9d', 'r', '2.2k', (48, 20, 'D2R'), (48, 21, GND))
# Output L (TL074 C)
part('C5c', 'np', '10µ NP', (32, 24, 'OUTC'), (33, 24, 'X6C'))
part('R11c', 'r', '100R', (34, 24, 'X6C'), (35, 24, 'OUT_L'))
part('R12c', 'r', '100k', (37, 24, 'OUT_L'), (37, 25, GND))
part('R10c', 'r', '1M', (34, 22, 'INPC'), (34, 21, GND))
part('C4c', 'film', '1µ', (36, 22, 'INPC'), (39, 22, 'COM_L'))
part('R8c', 'r', '10k', (45, 22, 'D1L'), (46, 22, 'D2L'))
part('R9c', 'r', '2.2k', (49, 22, 'D2L'), (49, 21, GND))
# Power
part('C7', 'cer', '100n', (28, 25, GND), (29, 25, VP))
part('C11', 'cer', '100n', (30, 25, VN), (31, 25, GND))
part('C6', 'el', '47µ', (29, 27, VP), (28, 27, GND))      # + first
part('C8', 'el', '47µ', (32, 26, GND), (32, 27, VN))      # + to GND
part('R13', 'r', '10R', (34, 30, VP), (34, 31, 'RAWP'))
part('R14', 'r', '10R', (36, 28, VN), (36, 29, 'RAWN'))
part('U2', 'sip', 'A0512S / IA0512S', (34, 33, 'RAWP'), (35, 33, GND), (36, 33, 'RAWN'), (38, 33, GND), (39, 33, V5))
part('C10', 'el', '10µ', (42, 32, V5), (42, 31, GND))

# ---------- wire pads (off-board leads): (x, y, net, label, side) ----------
_pads = [
    (14, 20, 'IN_L', 'IN L tip', 'nv'), (12, 20, GND, 'IN L sleeve', 'nv'),
    (14, 22, 'IN_R', 'IN R tip', 'sv'), (12, 22, GND, 'IN R sleeve', 'sv'),
    (20, 18, 'ADC_L', 'to ADC L in', 'nv'), (21, 17, GND, '', 'n'),
    (20, 24, 'ADC_R', 'to ADC R in', 'sv'), (21, 25, GND, '', 's'),
    (39, 18, 'OUT_R', 'OUT R tip', 'nv'), (38, 17, GND, '', 'n'),
    (39, 24, 'OUT_L', 'OUT L tip', 'sv'), (38, 25, GND, '', 's'),
    (40, 20, 'COM_R', 'S3 R com', 'nv'), (43, 20, 'D1R', 'DAC R', 'nv'), (44, 20, 'D1R', 'S3 R line', 'nv'), (47, 20, 'D2R', 'S3 R inst', 'nv'),
    (40, 22, 'COM_L', 'S3 L com', 'sv'), (43, 22, 'D1L', 'DAC L', 'sv'), (44, 22, 'D1L', 'S3 L line', 'sv'), (47, 22, 'D2L', 'S3 L inst', 'sv'),
    (43, 21, GND, 'DAC GND', 'ev'),
]
pads = [(x + DX, y + DY, n, l, sd) for x, y, n, l, sd in _pads] + [
    (4, 18, V5, '5V to ADC + pin', 'nv'),
]

# ---------- traces on the solder side: net -> polylines ----------
_tr = {
    GND: [[(12, 17), (41, 17)], [(12, 17), (12, 25)], [(12, 21), (26, 21)], [(12, 25), (28, 25), (28, 27)],
          [(41, 17), (41, 31)], [(33, 21), (49, 21)], [(31, 25), (41, 25)], [(31, 25), (31, 26), (32, 26)],
          [(38, 31), (42, 31)], [(38, 31), (38, 34), (35, 34), (35, 33)]],
    'IN_L': [[(14, 20), (15, 20)]], 'X1A': [[(16, 20), (17, 20)]], 'INPA': [[(19, 20), (28, 20)]],
    'OUTA': [[(27, 18), (28, 18), (28, 19)]], 'X3A': [[(24, 18), (26, 18)]], 'ADC_L': [[(20, 18), (23, 18)]],
    'IN_R': [[(14, 22), (15, 22)]], 'X1B': [[(16, 22), (17, 22)]], 'INPB': [[(19, 22), (28, 22)]],
    'OUTB': [[(27, 24), (28, 24), (28, 23)]], 'X3B': [[(24, 24), (26, 24)]], 'ADC_R': [[(20, 24), (23, 24)]],
    'OUTD': [[(32, 18), (31, 18), (31, 19)]], 'X6D': [[(33, 18), (34, 18)]], 'OUT_R': [[(35, 18), (39, 18)]],
    'INPD': [[(31, 20), (36, 20)]], 'COM_R': [[(39, 20), (40, 20)]], 'D1R': [[(43, 20), (45, 20)]], 'D2R': [[(46, 20), (48, 20)]],
    'OUTC': [[(32, 24), (31, 24), (31, 23)]], 'X6C': [[(33, 24), (34, 24)]], 'OUT_L': [[(35, 24), (39, 24)]],
    'INPC': [[(31, 22), (36, 22)]], 'COM_L': [[(39, 22), (40, 22)]], 'D1L': [[(43, 22), (45, 22)]], 'D2L': [[(46, 22), (49, 22)]],
    VP: [[(28, 21), (29, 21), (29, 29), (34, 29), (34, 30)]],
    VN: [[(31, 21), (30, 21), (30, 27), (36, 27), (36, 28)]],
    'RAWP': [[(34, 31), (34, 33)]], 'RAWN': [[(36, 29), (36, 33)]],
    V5: [[(39, 33), (42, 33), (42, 32)]],
}
traces = {n: [[(x + DX, y + DY) for x, y in poly] for poly in polys] for n, polys in _tr.items()}
# new: the converter boards, the Pi header and power along the bottom (unshifted coordinates)
for n, polys in {
    'MCK': [[(21, 23), (25, 23)]],
    'BCK': [[(21, 25), (22, 25), (22, 24), (25, 24)], [(21, 25), (18, 25), (18, 33)]],
    'LRCK': [[(21, 26), (25, 26)], [(21, 26), (19, 26), (19, 33)]],
    'DATA': [[(21, 24), (17, 24), (17, 33)]],
    'DOUT': [[(25, 25), (26, 25), (26, 32), (22, 32), (22, 33)]],
    GND: [[(21, 28), (22, 28), (22, 27), (25, 27)], [(21, 28), (20, 28), (20, 34)], [(1, 9), (1, 34), (20, 34)]],
    V5: [[(25, 28), (25, 31), (21, 31), (21, 33)], [(21, 33), (21, 34), (31, 34), (31, 17)], [(28, 17), (28, 19), (4, 19), (4, 18)]],
}.items():
    traces.setdefault(n, []).extend(polys)
# insulated wire links on the component side: (net, a, b)
links = []

# ---------- check ----------
def cells(poly):
    out = []
    for (x0, y0), (x1, y1) in zip(poly, poly[1:]):
        assert x0 == x1 or y0 == y1, f'diagonal trace {poly}'
        n = max(abs(x1 - x0), abs(y1 - y0))
        dx, dy = (x1 > x0) - (x1 < x0), (y1 > y0) - (y1 < y0)
        out += [(x0 + i * dx, y0 + i * dy) for i in range(n + 1)]
    return out

err = []
own = {}                     # hole -> net
legs = {}                    # hole -> ref (one lead per hole)
def claim(c, net, who):
    if not (0 <= c[0] < COLS and 0 <= c[1] < ROWS):
        err.append(f'{who} off the board at {c}')
    if own.setdefault(c, net) != net:
        err.append(f'short: {who} puts {net} on {c}, already {own[c]}')
for ref, kind, val, pins in parts:
    for x, y, net in pins:
        claim((x, y), net, ref)
        if (x, y) in legs:
            err.append(f'two leads in hole {(x, y)}: {legs[(x, y)]} and {ref}')
        legs[(x, y)] = ref
for x, y, net, lab, side in pads:
    claim((x, y), net, 'pad ' + lab)
    if (x, y) in legs:
        err.append(f'pad {lab} shares hole {(x, y)} with {legs[(x, y)]}')
for net, polys in traces.items():
    for poly in polys:
        for c in cells(poly):
            claim(c, net, 'trace')
# connectivity: union-find over holes
par = {}
def f(a):
    par.setdefault(a, a)
    while par[a] != a:
        par[a] = par[par[a]]; a = par[a]
    return a
def u(a, b): par[f(a)] = f(b)
for net, polys in traces.items():
    for poly in polys:
        cs = cells(poly)
        for a, b in zip(cs, cs[1:]):
            u(a, b)
for net, a, b in links:
    if own.get(a) != net or own.get(b) != net:
        err.append(f'link ends not on {net}: {a} {b}')
    u(a, b)
for ref, kind, val, pins in parts:
    if kind == 'dip':
        continue
terms = {}
for ref, kind, val, pins in parts:
    for x, y, net in pins:
        terms.setdefault(net, []).append((x, y))
for x, y, net, lab, side in pads:
    terms.setdefault(net, []).append((x, y))
for net, ts in terms.items():
    roots = {f(t) for t in ts}
    if len(roots) > 1:
        err.append(f'open: {net} is in {len(roots)} pieces')
if err:
    print('\n'.join(err)); sys.exit(1)
print(f'ok: {len(terms)} nets, {sum(len(p[3]) for p in parts)} leads, {len(pads)} wire pads, no shorts or opens')

# ---------- draw ----------
NETC = {GND: '#3a3a3a', VP: '#c0392b', VN: '#1e7bd6', V5: '#d9822b', V5B: '#d9822b',
        'BCK': '#883996', 'LRCK': '#883996', 'MCK': '#883996', 'DIN': '#5b8c2a', 'DOUT': '#5b8c2a'}
def ncol(n): return NETC.get(n, '#0f9d8a')
INK, MUTE, ACC = '#212121', '#7b7b7b', '#883996'
o = []; a = o.append
def t(x, y, s, size=11, anchor='middle', color=INK, weight='400'):
    a(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}">{html.escape(s)}</text>')

def board(ox, oy, title, sub, mirror):
    def X(x): return ox + ((COLS - 1 - x) if mirror else x) * P + P
    def Y(y): return oy + y * P + P
    t(ox, oy - 30, title, 18, 'start', weight='700'); t(ox, oy - 12, sub, 12, 'start', MUTE)
    a(f'<rect x="{ox}" y="{oy}" width="{(COLS+1)*P}" height="{(ROWS+1)*P}" rx="8" fill="#e9dcc0" stroke="#c9b48a"/>')
    for y in range(ROWS):
        for x in range(COLS):
            a(f'<circle cx="{X(x)}" cy="{Y(y)}" r="{P*0.30:.1f}" fill="#d8b36a"/><circle cx="{X(x)}" cy="{Y(y)}" r="{P*0.12:.1f}" fill="#fff8e6"/>')
    # column / row rulers every 5
    for x in range(0, COLS, 5):
        t(X(x), oy - 2 + (ROWS + 1) * P + 14, str(x), 9, color=MUTE)
    for y in range(0, ROWS, 5):
        t(ox - 6, Y(y) + 3, str(y), 9, 'end', MUTE)
    return X, Y

W = (COLS + 1) * P + 120
H1 = (ROWS + 1) * P
H = 110 + H1 + 90 + H1 + 230
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Helvetica, Arial, sans-serif">')
a(f'<rect width="{W}" height="{H}" fill="#fff"/>')
t(40, 40, 'NHE Pi 2x2 Audio: perfboard layout (pad per hole, 40 × 35 holes, about 10 × 9 cm)', 24, 'start', weight='700')
t(40, 64, 'Converter boards plug into female header sockets. Standing resistors. Check against docs/buffer.svg; the script checks for shorts and opens.', 13, 'start', '#575757')

# ----- top view -----
ox, oy = 60, 120
X, Y = board(ox, oy, 'Component side (top view)', 'Parts, sockets and where the converter boards sit. Faint lines show the traces underneath.', False)
for net, polys in traces.items():
    for poly in polys:
        pts = ' '.join(f'{X(x)},{Y(y)}' for x, y in poly)
        a(f'<polyline points="{pts}" fill="none" stroke="{ncol(net)}" stroke-opacity="0.22" stroke-width="{P*0.42:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
# converter boards: where they sit (component side up, on their sockets)
def outline(x0, y0, x1, y1, col, title, sub):
    a(f'<rect x="{X(x0)}" y="{Y(y0)}" width="{X(x1)-X(x0)}" height="{Y(y1)-Y(y0)}" rx="6" fill="{col}" fill-opacity="0.10" stroke="{col}" stroke-width="1.6" stroke-dasharray="6 4"/>')
    t((X(x0) + X(x1)) / 2, Y((y0 + y1) / 2) - 4, title, 12, color=col, weight='700')
    t((X(x0) + X(x1)) / 2, Y((y0 + y1) / 2) + 12, sub, 10, color=col)
ADCC, DACC = '#2a7a8c', '#6d4aa8'
outline(2.2, 19.6, 21.9, 31.4, ADCC, 'PCM1808 ADC board (DM-AMAD01)', 'traces only underneath')
a(f'<rect x="{X(1.4)}" y="{Y(28.2)}" width="{P*2.2}" height="{P*2.6}" rx="3" fill="{ADCC}" fill-opacity="0.35"/>')
t(X(3.9), Y(29.4) + 4, '3.5 mm in: pigtail to the ADC L / R pads', 10, 'start', ADCC, '700')
for xx in (5.8, 6.7):
    a(f'<circle cx="{X(xx)}" cy="{Y(20.3)}" r="4" fill="none" stroke="{ADCC}" stroke-width="2"/>')
t(X(7.3), Y(20.3) + 4, '+ and − (wire + to the 5V pad)', 10, 'start', ADCC, '700')
outline(24.6, 22.2, 38.2, 28.5, DACC, 'GY-PCM5102 DAC', 'no header on its top row')
a(f'<rect x="{X(38.2)}" y="{Y(23.0)}" width="{P*1.2}" height="{P*4.4}" rx="3" fill="{DACC}" fill-opacity="0.35"/>')
for xx, nm in ((32.5, 'G'), (33.5, 'R'), (34.5, 'G'), (35.5, 'L')):
    a(f'<circle cx="{X(xx)}" cy="{Y(22.7)}" r="4" fill="#fff" stroke="{DACC}" stroke-width="2"/>')
    t(X(xx), Y(22.7) + 17, nm, 10, color=DACC, weight='700')
# DAC audio wires: L, G, R from the DAC's top pins to the pads
for (xx, yy), (px, py), c in (((35.5, 22.7), (32, 6), '#0f9d8a'), ((33.5, 22.7), (32, 4), '#0f9d8a'), ((34.5, 22.7), (32, 5), '#3a3a3a')):
    a(f'<path d="M{X(xx)},{Y(yy)} C{X(xx)},{Y(14)} {X(px)+P*2},{Y(py)+P*3} {X(px)},{Y(py)}" fill="none" stroke="{c}" stroke-width="2.4" stroke-dasharray="1 0"/>')
t(X(35.8), Y(15), 'three short wires:', 10, 'start', DACC, '700'); t(X(35.8), Y(15) + 13, 'DAC L, G, R', 10, 'start', DACC, '700')
for ref, kind, val, pins in parts:
    xs = [X(x) for x, y, n in pins]; ys = [Y(y) for x, y, n in pins]
    if kind in ('hdr', 'sock'):
        fill = '#222' if kind == 'hdr' else '#444'
        vert = len(set(xs)) == 1
        if vert:
            a(f'<rect x="{xs[0]-P*0.45}" y="{min(ys)-P*0.45}" width="{P*0.9}" height="{max(ys)-min(ys)+P*0.9}" fill="{fill}" rx="2"/>')
        else:
            a(f'<rect x="{min(xs)-P*0.45}" y="{ys[0]-P*0.45}" width="{max(xs)-min(xs)+P*0.9}" height="{P*0.9}" fill="{fill}" rx="2"/>')
        for x, y, n in pins:
            a(f'<rect x="{X(x)-3}" y="{Y(y)-3}" width="6" height="6" fill="#d8b36a"/>')
        names = {'J4': ['MCK', 'DATA', 'BCK', 'LRCK', 'VDD33 (nc)', 'GND'], 'J2': ['SCK', 'BCK', 'DIN', 'LCK', 'GND', 'VIN'],
                 'J1': ['DATA → pin 38', 'BCK → pin 12', 'LRCK → pin 35', 'GND → pin 6', '5V → pin 2', 'DOUT → pin 40']}[ref]
        for (x, y, n), nm in zip(pins, names):
            if ref == 'J4':
                t(X(x) - P * 0.6, Y(y) + 3.5, nm, 8.5, 'end', ADCC, '700')
            elif ref == 'J2':
                t(X(x) + P * 0.6, Y(y) + 3.5, nm, 8.5, 'start', DACC, '700')
            else:
                a(f'<text x="{X(x)}" y="{Y(y)+P*0.6}" font-size="9" text-anchor="end" fill="{INK}" font-weight="700" transform="rotate(-90 {X(x)} {Y(y)+P*0.6})" dy="3.5">{html.escape(nm)}</text>')
        if ref == 'J1':
            t(X(23), Y(33) + 4, 'J1 to the Pi (Dupont wires)', 10, 'start', weight='700')
        else:
            t(xs[0], min(ys) - P * 0.7, ref, 10, weight='700')
    elif kind == 'dip':
        L2, R2, T2, B2 = min(p[0] for p in pins), max(p[0] for p in pins), min(p[1] for p in pins), max(p[1] for p in pins)
        a(f'<rect x="{X(L2)-P*0.4}" y="{Y(T2)-P*0.6}" width="{X(R2)-X(L2)+P*0.8}" height="{Y(B2)-Y(T2)+P*1.2}" rx="3" fill="#2b2b2b"/>')
        a(f'<path d="M{X(L2)+P*1.0},{Y(T2)-P*0.6} a{P*0.5},{P*0.5} 0 0 0 {P*1.0},0" fill="#555"/>')
        a(f'<circle cx="{X(L2)+P*0.35}" cy="{Y(T2)-P*0.1}" r="2.5" fill="#bbb"/>')
        for x, y, n in pins:
            a(f'<rect x="{X(x)-3}" y="{Y(y)-3}" width="6" height="6" fill="#ccc"/>')
        t((X(L2) + X(R2)) / 2, Y((T2 + B2) / 2) + 4, 'TL074', 10, color='#fff', weight='700')
    elif kind == 'sip':
        x0s, x1s, ys0 = pins[0][0] - 1.2, pins[-1][0] + 1.2, pins[0][1]
        a(f'<rect x="{X(x0s)}" y="{Y(ys0)-P*1.2}" width="{X(x1s)-X(x0s)}" height="{P*2.4}" rx="3" fill="#1f1f1f"/>')
        t((X(x0s) + X(x1s)) / 2, Y(ys0) + 4, 'A0512S or IA0512S', 9.5, color='#fff', weight='700')
        t(X(x1s) + 6, Y(ys0) - 6, 'U2: pin 1 (Vin) on this end', 9, 'start', MUTE)
    else:
        (x0, y0, _), (x1, y1, _) = pins[0], pins[1]
        cx0, cy0, cx1, cy1 = X(x0), Y(y0), X(x1), Y(y1)
        a(f'<line x1="{cx0}" y1="{cy0}" x2="{cx1}" y2="{cy1}" stroke="#9a9a9a" stroke-width="2"/>')
        if kind == 'r':
            a(f'<circle cx="{cx0}" cy="{cy0}" r="{P*0.42:.1f}" fill="#e8d1a6" stroke="#8a6d3b" stroke-width="1.5"/>')
        elif kind == 'film':
            a(f'<rect x="{min(cx0,cx1)-P*0.35}" y="{min(cy0,cy1)-P*0.4}" width="{abs(cx1-cx0)+P*0.7}" height="{abs(cy1-cy0)+P*0.8}" rx="3" fill="#e0b13a" stroke="#9c7a1f"/>')
        elif kind == 'cer':
            a(f'<ellipse cx="{(cx0+cx1)/2}" cy="{(cy0+cy1)/2}" rx="{P*0.75 if cy0==cy1 else P*0.4:.1f}" ry="{P*0.4 if cy0==cy1 else P*0.75:.1f}" fill="#e6a23c" stroke="#a66b17"/>')
        elif kind in ('el', 'np'):
            col = '#2f4f8f' if kind == 'el' else '#3c3c3c'
            a(f'<circle cx="{(cx0+cx1)/2}" cy="{(cy0+cy1)/2}" r="{P*0.72:.1f}" fill="{col}" stroke="#111"/>')
            if kind == 'el':
                a(f'<text x="{cx0}" y="{cy0+4}" font-size="11" text-anchor="middle" fill="#fff" font-weight="700">+</text>')
        # label
        mx, my = (cx0 + cx1) / 2, (cy0 + cy1) / 2
        lab = val.replace(' NP', '')
        place = {'R2a': (0, -1), 'R2b': (0, 1), 'R7a': (0, -1), 'R7b': (0, 1), 'R12d': (0, -1), 'R12c': (0, 1),
                 'R10d': (0, -1), 'R10c': (0, 1), 'R9d': (0, -1), 'R9c': (1, 0), 'C7': (0, 1), 'C11': (0, 1),
                 'C6': (-1, 0), 'C8': (1, 0), 'R13': (-1, 0), 'R14': (1, 0), 'C10': (1, 0)}.get(ref)
        if place is None:
            place = (0, -1) if y0 in (2, 4) else (0, 1)
        dx, dy = place
        if dx:
            t(mx + dx * P * 0.95, my + 4, lab, 10, 'start' if dx > 0 else 'end')
        else:
            t(mx, my + dy * P * 1.05 + (4 if dy > 0 else 0), lab, 10)
for net, (x0, y0), (x1, y1) in links:
    a(f'<line x1="{X(x0)}" y1="{Y(y0)}" x2="{X(x1)}" y2="{Y(y1)}" stroke="#2a7a2a" stroke-width="3"/>')
    t(X(x0) + 7, (Y(y0) + Y(y1)) / 2 + 4, 'link (GND)', 9, 'start', '#2a7a2a', '700')
def padlabels(X, Y, mirror):
    for x, y, net, lab, side in pads:
        a(f'<circle cx="{X(x)}" cy="{Y(y)}" r="{P*0.36:.1f}" fill="none" stroke="{ACC}" stroke-width="2.2"/>')
        if not lab:
            continue
        cx, cy = X(x), Y(y)
        if side == 'nv':
            a(f'<text x="{cx}" y="{cy-P*0.55}" font-size="10" fill="{ACC}" font-weight="700" text-anchor="start" transform="rotate(-90 {cx} {cy-P*0.55})" dy="3.5">{html.escape(lab)}</text>')
        elif side == 'sv':
            a(f'<text x="{cx}" y="{cy+P*0.55}" font-size="10" fill="{ACC}" font-weight="700" text-anchor="end" transform="rotate(-90 {cx} {cy+P*0.55})" dy="3.5">{html.escape(lab)}</text>')
        elif side == 'ev':
            east = not mirror
            t(cx + (P*0.55 if east else -P*0.55), cy + 4, lab, 9.5, 'start' if east else 'end', ACC, '700')
        elif side == 'w':
            west = not mirror
            t(cx + (-P*0.55 if west else P*0.55), cy + 4, lab, 10, 'end' if west else 'start', ACC, '700')
        elif side == 'n':
            t(cx, cy - P*0.6, lab, 10, 'middle', ACC, '700')
        else:
            t(cx, cy + P*0.95, lab, 10, 'middle', ACC, '700')
padlabels(X, Y, False)

# ----- solder side -----
oy2 = oy + H1 + 90
X2, Y2 = board(ox, oy2, 'Solder side (board flipped left to right)', 'Make each line a trace: solder bridges between pads, or tinned wire for long runs. Purple rings: wire pads.', True)
for net, polys in traces.items():
    for poly in polys:
        pts = ' '.join(f'{X2(x)},{Y2(y)}' for x, y in poly)
        a(f'<polyline points="{pts}" fill="none" stroke="{ncol(net)}" stroke-width="{P*0.42:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
for ref, kind, val, pins in parts:
    for x, y, net in pins:
        a(f'<circle cx="{X2(x)}" cy="{Y2(y)}" r="{P*0.2:.1f}" fill="#fff" stroke="{INK}" stroke-width="1.2"/>')
padlabels(X2, Y2, True)
for net, (x0, y0), (x1, y1) in links:
    for xx, yy in ((x0, y0), (x1, y1)):
        a(f'<circle cx="{X2(xx)}" cy="{Y2(yy)}" r="{P*0.34:.1f}" fill="none" stroke="#2a7a2a" stroke-width="2"/>')
# legend
ly = oy2 + H1 + 40
for i, (lab, c) in enumerate([('Ground', NETC[GND]), ('+12 V', NETC[VP]), ('−12 V', NETC[VN]), ('5 V', NETC[V5]),
                               ('I2S clocks', NETC['BCK']), ('I2S data', NETC['DIN']), ('Audio', '#0f9d8a')]):
    x = 60 + i * 140
    a(f'<rect x="{x}" y="{ly}" width="26" height="8" rx="4" fill="{c}"/>'); t(x + 34, ly + 8, lab, 12, 'start')
notes = [
    'J4 and J2 match the boards in the photos: plug each board in component side up, its body over the dashed outline.',
    'DAC: solder headers on its six-pin side only. Its L / G / R pins are half a hole off the grid: three short wires to the DAC pads.',
    'ADC: audio goes in through its own 3.5 mm jack: a short stereo plug pigtail from the ADC L / R pads (sleeve to GND). One wire from its + pin to the 5V pad.',
    'S3: one DPDT toggle for both channels. Per channel: common to "S3 com", one throw to "line", the other to "inst".',
    'U2: A0512S-1WR3 or XP IA0512S (same pins). Build the power first and measure about ±12 V on the TL074 socket pins 4 and 11 before fitting the chip.',
]
for j, n in enumerate(notes):
    t(60, ly + 40 + j * 22, '• ' + n, 12.5, 'start', '#323232')
a('</svg>')
open('docs/perfboard.svg', 'w').write('\n'.join(o))

# ---------- netlist for VeroRoute (Protel V1 / Tango: File > Import > Tango) ----------
def vr_type(ref, kind, pins):
    if kind == 'r':
        return 'RESISTOR1'                       # standing, legs 100 mil apart (stretch it in VeroRoute to lie flat)
    if kind == 'film':
        (x0, y0, _), (x1, y1, _) = pins
        return 'CAP_FILM%d' % (abs(x1 - x0) + abs(y1 - y0))
    if kind == 'cer':
        return 'CAP_CERAMIC1'
    if kind == 'el':
        return 'CAP_ELECTRO_200'                 # pin 1 is +
    if kind == 'np':
        return 'CAP_ELECTRO_200_NP'
    if kind == 'dip':
        return 'DIP%d' % len(pins)
    if kind in ('sock', 'hdr'):
        return 'STRIP_100MIL%d' % len(pins)
    raise ValueError(kind)

NETNAME = {VP: 'P12V', VN: 'N12V', V5: 'P5V'}
vparts, vnets = [], {}
def vadd(name, typ, value, nets):               # nets: list of net per pin (pin 1 first)
    vparts.append((name, typ, value))
    for i, n in enumerate(nets):
        if n and not n.startswith('NC_'):
            vnets.setdefault(NETNAME.get(n, n), []).append(f'{name}-{i+1}')
for ref, kind, val, pins in parts:
    if kind == 'sip':                           # U2: 1 Vin, 2 GND, 3 no pin, 4 -Vo, 5 0V, 6 +Vo
        by = {x: n for x, y, n in pins}
        xs = sorted(by)                         # +Vo, 0V, -Vo, GND, Vin (left to right)
        vadd(ref, 'SIP6', val, [by[xs[4]], by[xs[3]], None, by[xs[2]], by[xs[1]], by[xs[0]]])
    else:
        vadd(ref, vr_type(ref, kind, pins), val, [n for x, y, n in pins])
# off-board wires as pad groups (each pin becomes a pad named GROUP_n); entries are pad labels or (x, y)
groups = [('PIN', 'jacks IN', ['IN L tip', 'IN L sleeve', 'IN R tip', 'IN R sleeve']),
          ('PADC', 'to ADC board', ['to ADC L in', (10, 1), 'to ADC R in', (10, 9)]),
          ('POUT', 'jacks OUT', ['OUT L tip', (27, 9), 'OUT R tip', (27, 1)]),
          ('PDAC', 'from DAC board', ['DAC L', 'DAC GND', 'DAC R']),
          ('PS3', 'switch S3', ['S3 L com', 'S3 L line', 'S3 L inst', 'S3 R com', 'S3 R line', 'S3 R inst']),
          ('PADCP', 'ADC + pin', ['5V to ADC + pin'])]
bylab = {lab: (x, y, n) for x, y, n, lab, sd in pads if lab}
byxy = {(x, y): (x, y, n) for x, y, n, lab, sd in pads}
vpos = {}                                        # name -> [(row, col) per pin]
for ref, kind, val, pins in parts:
    if kind == 'sip':
        xs = sorted(x for x, y, n in pins); y0 = pins[0][1]
        vpos[ref] = [(y0, xs[-1] - i) for i in range(6)]   # pin 1 (Vin) at the right end, pin 3 is the gap
    else:
        vpos[ref] = [(y, x) for x, y, n in pins]
used = set()
for name, val, ents in groups:
    pp = [bylab[e] if isinstance(e, str) else byxy[e] for e in ents]
    used.update((x, y) for x, y, n in pp)
    vadd(name, 'PADS%d' % len(pp), val, [n for x, y, n in pp])
    for k, (x, y, n) in enumerate(pp):
        vpos[f'{name}_{k+1}'] = [(y, x)]
assert used == set(byxy), set(byxy) - used
import json
json.dump({'rows': ROWS, 'cols': COLS, 'pos': vpos,
           'tracks': [[NETNAME.get(n, n), [(y, x) for poly in polys for (x, y) in cells(poly)]] for n, polys in traces.items()]},
          open('docs/vr_place.json', 'w'))
with open('docs/nhe-2x2-audio.net', 'w') as f:
    for name, typ, value in vparts:
        f.write(f'[\n{name}\n{typ}\n{value}\n\n\n\n]\n')
    for net, pins_ in vnets.items():
        f.write('(\n' + net + '\n' + '\n'.join(pins_) + '\n)\n')
print(f'netlist: {len(vparts)} parts, {len(vnets)} nets -> docs/nhe-2x2-audio.net')
