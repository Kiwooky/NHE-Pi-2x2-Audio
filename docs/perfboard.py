# Draws docs/perfboard.svg: the whole 2x2 board on pad-per-hole perfboard
# (9 x 15 cm, 59 x 35 holes), top view and solder-side view.
# It also checks the layout: no two nets share a hole, and every net is connected.
# Run from the repo root: python3 docs/perfboard.py
import html, sys

COLS, ROWS = 59, 35
P = 24                      # px per hole
GND, VP, VN, V5, V5B = 'GND', '+12V', '-12V', '5V', '5V-B'

# ---------- parts: (ref, kind, value, [(x, y, net), ...]) ----------
parts = []
def part(ref, kind, val, *pins):
    parts.append((ref, kind, val, list(pins)))

# Digital: Pi wires, DAC socket, ADC socket
part('J1', 'hdr', 'to Pi', (4, 11, 'BCK'), (5, 11, 'DOUT'), (6, 11, 'LRCK'), (7, 11, GND), (8, 11, V5), (9, 11, 'DIN'))
part('J2', 'sock', 'DAC board', (3, 8, 'MCK'), (4, 8, 'BCK'), (5, 8, 'DOUT'), (6, 8, 'LRCK'), (7, 8, GND), (8, 8, V5))
part('J4', 'sock', 'ADC board', (14, 8, 'DIN'), (15, 8, V5), (16, 8, GND), (17, 8, 'LRCK'), (18, 8, 'BCK'), (19, 8, 'MCK'))
# TL074, pins 1-7 down the left (x 28), 14-8 down the right (x 31)
L, R = 28, 31
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
part('U2', 'sip', 'A0512S-1WR3', (34, 33, 'RAWP'), (35, 33, GND), (36, 33, 'RAWN'), (38, 33, GND), (39, 33, V5B))
part('C10', 'el', '10µ', (42, 32, V5B), (42, 31, GND))
part('J6', 'hdr', '5V', (42, 33, V5B))

# ---------- wire pads (off-board leads): (x, y, net, label, side) ----------
pads = [
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

# ---------- traces on the solder side: net -> polylines ----------
traces = {
    GND: [[(12, 17), (41, 17)], [(12, 17), (12, 25)], [(12, 21), (26, 21)], [(12, 25), (28, 25), (28, 27)],
          [(41, 17), (41, 31)], [(33, 21), (49, 21)], [(31, 25), (41, 25)], [(31, 25), (31, 26), (32, 26)],
          [(38, 31), (42, 31)], [(38, 31), (38, 34), (35, 34), (35, 33)],
          [(7, 8), (7, 11)], [(7, 11), (7, 14), (16, 14), (16, 8)]],
    V5: [[(8, 8), (8, 11)], [(8, 11), (8, 13), (15, 13), (15, 8)]],
    V5B: [[(39, 33), (42, 33), (42, 32)]],
    'BCK': [[(4, 8), (4, 11)], [(4, 11), (4, 16), (18, 16), (18, 8)]],
    'DOUT': [[(5, 8), (5, 11)]],
    'LRCK': [[(6, 8), (6, 11)], [(6, 11), (6, 15), (17, 15), (17, 8)]],
    'DIN': [[(9, 11), (9, 12), (14, 12), (14, 8)]],
    'MCK': [[(3, 8), (3, 7), (19, 7), (19, 8)]],
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
}
# insulated wire links on the component side: (net, a, b)
links = [(GND, (16, 14), (16, 17))]

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
t(40, 40, 'NHE Pi 2x2 Audio: perfboard layout (pad per hole, 9 × 15 cm)', 24, 'start', weight='700')
t(40, 64, 'Converter boards plug into female header sockets. Standing resistors. Check against docs/buffer.svg; the script checks for shorts and opens.', 13, 'start', '#575757')

# ----- top view -----
ox, oy = 60, 120
X, Y = board(ox, oy, 'Component side (top view)', 'Parts and the one wire link. Faint lines show the traces underneath.', False)
for net, polys in traces.items():
    for poly in polys:
        pts = ' '.join(f'{X(x)},{Y(y)}' for x, y in poly)
        a(f'<polyline points="{pts}" fill="none" stroke="{ncol(net)}" stroke-opacity="0.22" stroke-width="{P*0.42:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
# module footprints over the sockets
a(f'<rect x="{X(2)-P*0.5}" y="{Y(1)}" width="{P*8}" height="{P*6.4}" rx="5" fill="#6d4aa8" fill-opacity="0.12" stroke="#6d4aa8" stroke-dasharray="5 4"/>')
t((X(2) + X(9)) / 2, Y(4), 'GY-PCM5102 DAC board', 11, color='#6d4aa8', weight='700'); t((X(2) + X(9)) / 2, Y(5), 'lies over this area', 10, color='#6d4aa8')
a(f'<rect x="{X(12)-P*0.5}" y="{Y(0)}" width="{P*10}" height="{P*7.4}" rx="5" fill="#2a7a8c" fill-opacity="0.12" stroke="#2a7a8c" stroke-dasharray="5 4"/>')
t((X(12) + X(21)) / 2, Y(3), 'PCM1808 ADC board', 11, color='#2a7a8c', weight='700'); t((X(12) + X(21)) / 2, Y(4), 'lies over this area', 10, color='#2a7a8c')
for ref, kind, val, pins in parts:
    xs = [X(x) for x, y, n in pins]; ys = [Y(y) for x, y, n in pins]
    if kind in ('hdr', 'sock'):
        fill = '#222' if kind == 'hdr' else '#444'
        a(f'<rect x="{min(xs)-P*0.45}" y="{min(ys)-P*0.45}" width="{max(xs)-min(xs)+P*0.9}" height="{P*0.9}" fill="{fill}" rx="2"/>')
        for (x, y, n), cx in zip(pins, xs):
            a(f'<rect x="{cx-3}" y="{Y(y)-3}" width="6" height="6" fill="#d8b36a"/>')
        names = {'J2': ['SCK', 'BCK', 'DIN', 'LCK', 'GND', 'VIN'], 'J4': ['DATA', '5V', 'GND', 'LRCK', 'BCK', 'MCK'],
                 'J1': ['BCK', 'DOUT', 'LRCK', 'GND', '5V', 'DIN']}.get(ref)
        if names:
            for nm, cx in zip(names, xs):
                a(f'<text x="{cx}" y="{min(ys)+P*1.25}" font-size="8.5" text-anchor="end" fill="{INK}" transform="rotate(-90 {cx} {min(ys)+P*1.25})" dy="3">{nm}</text>' if ref == 'J1' else
                  f'<text x="{cx}" y="{min(ys)+P*0.95}" font-size="8" text-anchor="start" fill="{INK}" transform="rotate(90 {cx} {min(ys)+P*0.95})" dy="3">{nm}</text>')
        lab = {'J1': 'J1 to Pi header (Dupont wires)', 'J2': 'J2', 'J4': 'J4', 'J6': 'J6 ← Pi pin 4 (5 V)'}[ref]
        if ref == 'J1':
            t(max(xs) + P * 0.8, min(ys) + 4, lab, 10, 'start', weight='700')
        elif ref == 'J6':
            t(max(xs) + P * 0.8, min(ys) + 4, lab, 10, 'start', weight='700')
        else:
            t(min(xs) - P * 0.8, min(ys) + 4, lab, 10, 'end', weight='700')
    elif kind == 'dip':
        a(f'<rect x="{X(L)-P*0.4}" y="{Y(18)-P*0.6}" width="{X(R)-X(L)+P*0.8}" height="{Y(24)-Y(18)+P*1.2}" rx="3" fill="#2b2b2b"/>')
        a(f'<path d="M{X(L)+P*1.0},{Y(18)-P*0.6} a{P*0.5},{P*0.5} 0 0 0 {P*1.0},0" fill="#555"/>')
        a(f'<circle cx="{X(L)+P*0.35}" cy="{Y(18)-P*0.1}" r="2.5" fill="#bbb"/>')
        for x, y, n in pins:
            a(f'<rect x="{X(x)-3}" y="{Y(y)-3}" width="6" height="6" fill="#ccc"/>')
        t((X(L) + X(R)) / 2, Y(21) + 4, 'TL074', 10, color='#fff', weight='700')
        t((X(L) + X(R)) / 2, Y(25) + 6, 'U1 (socket)', 9, color=MUTE)
    elif kind == 'sip':
        a(f'<rect x="{X(33)-P*0.2}" y="{Y(33)-P*1.2}" width="{X(40)-X(33)+P*0.4}" height="{P*2.4}" rx="3" fill="#1f1f1f"/>')
        t((X(33) + X(40)) / 2, Y(33) + 4, 'A0512S-1WR3', 9.5, color='#fff', weight='700')
        t((X(33) + X(40)) / 2, Y(33) + P * 1.9, 'U2: dot (pin 1, Vin) on the right', 9, color=MUTE)
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
            place = (0, -1) if y0 in (18, 20) else (0, 1)
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
    'J4 pin order (DATA 5V GND LRCK BCK MCK) is a guess until checked against the ADC board. J2 matches the GY-PCM5102 (SCK BCK DIN LCK GND VIN).',
    'Audio to and from the converter boards: short 3-wire leads (L, GND, R) from each board’s audio pads or jack to the DAC/ADC pads here.',
    'S3: one DPDT toggle switches both channels. Per channel, wire its common to "S3 com", one throw to "line", the other to "inst".',
    'Standing resistors: body on the ring end. 47µ: + as marked. C8’s + goes to GND (it sits on −12 V). U2: dot side (pin 1, Vin) to the right.',
    'Before plugging anything in: check for shorts between 5V, ±12V and GND with a meter, then power up with only U2 and U1 fitted and measure the rails.',
]
for j, n in enumerate(notes):
    t(60, ly + 40 + j * 22, '• ' + n, 12.5, 'start', '#323232')
a('</svg>')
open('docs/perfboard.svg', 'w').write('\n'.join(o))
