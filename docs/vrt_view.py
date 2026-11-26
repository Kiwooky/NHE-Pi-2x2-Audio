# Draws docs/layout.svg (component side + solder side) from a VeroRoute layout dumped
# by tools/vr_dump (docs/vr_layout.json), and checks it against docs/nhe-2x2-audio.net.
# Run from the repo root: python3 docs/vrt_view.py
import json, html, collections
d = json.load(open('docs/vr_layout.json'))
ROWS, COLS = d['rows'], d['cols']
comps = {c['name']: c for c in d['comps']}
# netlist
nets = {}; cur = None; inn = False
for l in open('docs/nhe-2x2-audio.net').read().split('\n'):
    if l == '(': inn = True; cur = None; continue
    if l == ')': inn = False; continue
    if inn:
        if cur is None: cur = l; nets[cur] = []
        else: nets[cur].append(l)
def pin(ref):
    name, n = ref.rsplit('-', 1); n = int(n)
    return comps[name]['pins'][n - 1] if name in comps else comps[f'{name}_{n}']['pins'][0]
netname = {}
for net, refs in nets.items():
    for r in refs: netname[pin(r)[2]] = net
cell = {(r, k): nid for l, r, k, nid, w in d['cells'] if nid >= 0}
# wire links still to add by hand: (net, from pin, to pin, why)
LINKS = [('LRCK', 'J4-4', 'JPIO-3', 'ADC LRCK to GPIO 35'), ('GND', 'J4-6', 'JPIO-1', 'ADC GND to GPIO 39')]
# connectivity (orthogonal; diagonals are off) + links + the Pi's own GND pins
par = {}
def f(a):
    par.setdefault(a, a)
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
for (r, k), nid in cell.items():
    for dr, dk in ((1, 0), (0, 1)):
        if cell.get((r + dr, k + dk)) == nid: par[f((r, k))] = f((r + dr, k + dk))
for net, a_, b_, why in LINKS:
    par[f(tuple(pin(a_)[:2]))] = f(tuple(pin(b_)[:2]))
gpio_gnd = [r for r in nets['GND'] if r.startswith('JP')]
for a_, b_ in zip(gpio_gnd, gpio_gnd[1:]):
    par[f(tuple(pin(a_)[:2]))] = f(tuple(pin(b_)[:2]))
bad = {n: len({f(tuple(pin(r)[:2])) for r in refs}) for n, refs in nets.items()}
bad = {n: p for n, p in bad.items() if p > 1}
print('with the two links:', 'every net connected' if not bad else f'still open: {bad}')

P = 22
NETC = {'GND': '#3a3a3a', 'P12V': '#c0392b', 'N12V': '#1e7bd6', 'P5V': '#d9822b',
        'BCK': '#883996', 'LRCK': '#883996', 'MCK': '#883996', 'DATA': '#5b8c2a', 'DOUT': '#5b8c2a'}
def ncol(n): return NETC.get(n, '#0f9d8a')
INK, MUTE, ACC = '#212121', '#7b7b7b', '#883996'
o = []; a = o.append
def t(x, y, s, size=11, anchor='middle', color=INK, weight='400'):
    a(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}">{html.escape(s)}</text>')
PADLAB = {'PIN': ['IN L tip', 'IN L sleeve', 'IN R tip', 'IN R sleeve'], 'PADC': ['to ADC L', 'GND', 'to ADC R', 'GND'],
          'POUT': ['OUT L tip', 'GND', 'OUT R tip', 'GND'], 'PDAC': ['DAC L', 'DAC G', 'DAC R'],
          'PS3': ['S3 L com', 'S3 L line', 'S3 L inst', 'S3 R com', 'S3 R line', 'S3 R inst'], 'PADCP': ['5V to ADC +']}
def board(ox, oy, title, sub, mirror):
    X = (lambda k: ox + ((COLS - 1 - k) if mirror else k) * P + P)
    Y = (lambda r: oy + r * P + P)
    t(ox, oy - 30, title, 18, 'start', weight='700'); t(ox, oy - 12, sub, 12, 'start', MUTE)
    a(f'<rect x="{ox}" y="{oy}" width="{(COLS+1)*P}" height="{(ROWS+1)*P}" rx="8" fill="#e9dcc0" stroke="#c9b48a"/>')
    for r in range(ROWS):
        for k in range(COLS):
            a(f'<circle cx="{X(k)}" cy="{Y(r)}" r="{P*0.3:.1f}" fill="#d8b36a"/><circle cx="{X(k)}" cy="{Y(r)}" r="{P*0.12:.1f}" fill="#fff8e6"/>')
    for k in range(0, COLS, 5): t(X(k), oy + (ROWS + 1) * P + 14, str(k), 9, color=MUTE)
    for r in range(0, ROWS, 5): t(ox - 6, Y(r) + 3, str(r), 9, 'end', MUTE)
    return X, Y
def tracks(X, Y, op):
    for (r, k), nid in cell.items():
        c = ncol(netname.get(nid, ''))
        for dr, dk in ((1, 0), (0, 1)):
            if cell.get((r + dr, k + dk)) == nid:
                a(f'<line x1="{X(k)}" y1="{Y(r)}" x2="{X(k+dk)}" y2="{Y(r+dr)}" stroke="{c}" stroke-opacity="{op}" stroke-width="{P*0.42:.1f}" stroke-linecap="round"/>')
        a(f'<circle cx="{X(k)}" cy="{Y(r)}" r="{P*0.21:.1f}" fill="{c}" fill-opacity="{op}"/>')
W = (COLS + 1) * P + 120; H1 = (ROWS + 1) * P
H = 120 + H1 + 120 + H1 + 260
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Helvetica, Arial, sans-serif">')
a(f'<rect width="{W}" height="{H}" fill="#fff"/>')
t(40, 40, 'NHE Pi 2x2 Audio: build layout (from NHE-2x2-Pi-Audio.vrt)', 24, 'start', weight='700')
t(40, 64, f'{COLS} x {ROWS} holes. Drawn from the VeroRoute layout; checked against the netlist: ' + ('every net connected once the two green links are in.' if not bad else 'OPEN NETS: ' + str(bad)), 13, 'start', '#575757')
# top
X, Y = board(60, 130, 'Component side', 'Parts as placed. Faint lines: traces underneath. Dashed: where the converter boards and the Pi sit.', False)
tracks(X, Y, 0.22)
def rect(r0, r1, c0, c1, col, lab):
    a(f'<rect x="{X(c0)}" y="{Y(r0)}" width="{X(c1)-X(c0)}" height="{Y(r1)-Y(r0)}" rx="6" fill="{col}" fill-opacity="0.08" stroke="{col}" stroke-width="1.6" stroke-dasharray="6 4"/>')
    t((X(c0) + X(c1)) / 2, Y((r0 + r1) / 2), lab, 12, color=col, weight='700')
rect(10.2, 29.9, 7.65, 19.35, '#2a7a8c', 'ADC board (body up from J4)')
rect(16.2, 29.4, 21.2, 27.5, '#6d4aa8', 'DAC (body up)')
a(f'<rect x="{X(21.6)}" y="{Y(14.6)}" width="{X(27.1)-X(21.6)}" height="{P*1.6}" rx="3" fill="#6d4aa8" fill-opacity="0.3"/>')
t(X(24.35), Y(15.4) + 4, 'jack', 9, color='#fff', weight='700')
gx = [p[1] for p in comps['JPIE']['pins']]; gr = comps['JPIE']['pins'][0][0]
a(f'<rect x="{X(min(gx)-11.5)}" y="{Y(gr-0.88)}" width="{P*33.5}" height="{P*4}" fill="#c0392b" fill-opacity="0.07" stroke="#c0392b" stroke-width="1.6" stroke-dasharray="6 4"/>')
t(X((min(gx) + max(gx)) / 2), Y(gr + 3.6), 'Raspberry Pi edge (upright, under here)', 10, color='#c0392b', weight='700')
for name, c in comps.items():
    pins = c['pins']; typ = c['type']
    xs = [X(p[1]) for p in pins]; ys = [Y(p[0]) for p in pins]
    if typ == 'PAD':
        g, n = name.rsplit('_', 1); lab = PADLAB.get(g, [name])[int(n) - 1] if g in PADLAB else name
        a(f'<circle cx="{xs[0]}" cy="{ys[0]}" r="{P*0.36:.1f}" fill="none" stroke="{ACC}" stroke-width="2.2"/>')
        a(f'<text x="{xs[0]}" y="{ys[0]-P*0.5}" font-size="9" fill="{ACC}" font-weight="700" text-anchor="start" transform="rotate(-50 {xs[0]} {ys[0]-P*0.5})">{html.escape(lab)}</text>')
        continue
    if typ in ('STRIP_100MIL', 'DIP', 'SIP'):
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        fill = {'STRIP_100MIL': '#444', 'DIP': '#2b2b2b', 'SIP': '#1f1f1f'}[typ]
        pad = P * 0.45 if typ != 'SIP' else P * 1.1
        a(f'<rect x="{x0-pad}" y="{y0-P*0.45}" width="{x1-x0+2*pad}" height="{y1-y0+P*0.9}" rx="3" fill="{fill}"/>')
        for i, (xx, yy) in enumerate(zip(xs, ys)):
            col = '#ccc' if pins[i][2] >= 0 else '#777'
            a(f'<rect x="{xx-3}" y="{yy-3}" width="6" height="6" fill="{col}"/>')
        a(f'<rect x="{xs[0]-6}" y="{ys[0]-6}" width="12" height="12" fill="none" stroke="#e33" stroke-width="2"/>')
        lab = {'JPIO': 'GPIO edge row (odd pins)', 'JPIE': 'GPIO inner row (even pins)', 'U1': 'TL074', 'U2': c['value']}.get(name, f"{name} {c['value']}")
        if name in ('U1',):
            t((x0 + x1) / 2, (y0 + y1) / 2 + 4, lab, 10, color='#fff', weight='700')
        elif name == 'JPIO':
            t(x1 + P, y0 + 4, lab + ' · red box = GPIO pin 39', 9, 'start', '#c0392b', '700')
        elif name == 'JPIE':
            t(x1 + P, y0 + 4, lab + ' · red box = pin 40', 9, 'start', MUTE, '700')
        else:
            t((x0 + x1) / 2, y0 - P * 0.7, lab, 10, weight='700')
        continue
    (r0, k0, _), (r1, k1, _) = pins[0], pins[1]
    cx0, cy0, cx1, cy1 = X(k0), Y(r0), X(k1), Y(r1)
    a(f'<line x1="{cx0}" y1="{cy0}" x2="{cx1}" y2="{cy1}" stroke="#9a9a9a" stroke-width="2"/>')
    mx, my = (cx0 + cx1) / 2, (cy0 + cy1) / 2
    if typ == 'RESISTOR':
        a(f'<circle cx="{cx0}" cy="{cy0}" r="{P*0.42:.1f}" fill="#e8d1a6" stroke="#8a6d3b" stroke-width="1.5"/>')
    elif typ == 'CAP_FILM':
        a(f'<rect x="{min(cx0,cx1)-P*0.35}" y="{min(cy0,cy1)-P*0.4}" width="{abs(cx1-cx0)+P*0.7}" height="{abs(cy1-cy0)+P*0.8}" rx="3" fill="#e0b13a" stroke="#9c7a1f"/>')
    elif typ == 'CAP_CERAMIC':
        a(f'<circle cx="{mx}" cy="{my}" r="{P*0.45:.1f}" fill="#e6a23c" stroke="#a66b17"/>')
    else:
        col = '#2f4f8f' if typ == 'CAP_ELECTRO_200' else '#3c3c3c'
        a(f'<circle cx="{mx}" cy="{my}" r="{P*0.72:.1f}" fill="{col}" stroke="#111"/>')
        if typ == 'CAP_ELECTRO_200':
            t(cx0, cy0 + 4, '+', 12, color='#fff', weight='700')
    warn = name == 'R14'
    horiz = r0 == r1
    lx, ly_, an = (mx, my - P * 0.62, 'middle') if horiz else (mx + P * 0.6, my + 3.5, 'start')
    t(lx, ly_, name + ('  ← lay flat' if warn else ''), 8.5, an, '#c0392b' if warn else INK, '700')
for i, (net, a_, b_, why) in enumerate(LINKS):
    p0, p1 = pin(a_), pin(b_)
    a(f'<line x1="{X(p0[1])+5}" y1="{Y(p0[0])}" x2="{X(p1[1])+5}" y2="{Y(p1[0])}" stroke="#2a9a2a" stroke-width="3.5"/>')
    t(X(p0[1]) + 5, Y(p1[0]) + P * 0.95, f'L{i+1}', 10, 'middle', '#2a9a2a', '700')
# solder side
oy2 = 130 + H1 + 120
X, Y = board(60, oy2, 'Solder side (flipped left to right)', 'Every line is a trace: solder bridges between pads, or tinned wire. Green: the two wire links.', True)
tracks(X, Y, 1)
for name, c in comps.items():
    for p in c['pins']:
        a(f'<circle cx="{X(p[1])}" cy="{Y(p[0])}" r="{P*0.18:.1f}" fill="#fff" stroke="{INK}" stroke-width="1.1"/>')
for net, a_, b_, why in LINKS:
    p0, p1 = pin(a_), pin(b_)
    a(f'<line x1="{X(p0[1])+5}" y1="{Y(p0[0])}" x2="{X(p1[1])+5}" y2="{Y(p1[0])}" stroke="#2a9a2a" stroke-width="3.5"/>')
ly = oy2 + H1 + 50
for i, (lab, c) in enumerate([('Ground', NETC['GND']), ('+12 V', NETC['P12V']), ('−12 V', NETC['N12V']), ('5 V', NETC['P5V']),
                               ('I2S clocks', NETC['BCK']), ('I2S data', NETC['DATA']), ('Audio', '#0f9d8a')]):
    x = 60 + i * 140
    a(f'<rect x="{x}" y="{ly}" width="26" height="8" rx="4" fill="{c}"/>'); t(x + 34, ly + 8, lab, 12, 'start')
notes = ['Two wire links to add (green), on the trace side, each hopping one GPIO pin: L1 J4 pin 4 to GPIO 35 (LRCK), L2 J4 pin 6 to GPIO 39 (the ADC’s ground).',
         'R14 stands under the top of the ADC board: lay it flat (about 3 mm tall) or move it out of the dashed area.',
         'Row 33 has traces below the GPIO edge row: the board edge goes past them, so the carrier overlaps the Pi by about 9 mm. Check it clears the Active Cooler.',
         'Pin 1 boxes are red. The GPIO edge-row box is pin 39; check the mirror: the Pi’s pin 1 (square pad on its underside) meets the right-hand end of the edge row.']
for j, n in enumerate(notes):
    t(60, ly + 40 + j * 22, '• ' + n, 12.5, 'start', '#323232')
a('</svg>')
open('docs/layout.svg', 'w').write('\n'.join(o))
