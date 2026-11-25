# Draws docs/wiring.svg. Run from the repo root: python3 docs/wiring.py
# Wiring map: one row per net, three columns (ADC board, Pi header, DAC board).
import html
W, ROW, TOP = 1040, 64, 150
COLX = {'adc': 190, 'pi': 520, 'dac': 850}
C = {'clock': '#883996', 'data': '#1e7bd6', 'power': '#c0392b', 'ground': '#323232'}
rows = [
  # net label, kind, adc pin, pi pin, dac pin, direction note, footnote
  ('Master clock', 'clock', 'MCK', None, 'SCK', 'ADC → DAC', 'or tie DAC SCK to GND'),
  ('Bit clock',    'clock', 'BCK', 'pin 12 · GPIO 18', 'BCK', 'ADC → Pi + DAC', ''),
  ('Word clock',   'clock', 'LRCK', 'pin 35 · GPIO 19', 'LCK', 'ADC → Pi + DAC', ''),
  ('Audio in',     'data',  'DATA', 'pin 38 · GPIO 20', None, 'ADC → Pi', ''),
  ('Audio out',    'data',  None, 'pin 40 · GPIO 21', 'DIN', 'Pi → DAC', ''),
  ('5 V',          'power', None, 'pin 2 (or 4)', 'VIN', 'Pi → DAC', 'ADC: its USB-C, same supply'),
  ('Ground',       'ground','GND', 'pin 6 (or 9, 14)', 'GND', 'common', ''),
]
H = TOP + ROW * len(rows) + 150
o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Helvetica, Arial, sans-serif">')
a('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="13" markerHeight="13" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>')
a(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
a('<text x="40" y="48" font-size="26" font-weight="700" fill="#212121">NHE Pi 2x2 Audio: wiring</text>')
a('<text x="40" y="76" font-size="15" fill="#575757">PCM1808 ADC board (clock master) · Raspberry Pi 5 or 3B+ header · GY-PCM5102 DAC board. One row per wire; arrows point to the receivers.</text>')
heads = [('adc', 'PCM1808 ADC board', 'makes the clocks · 48 kHz'), ('pi', 'Raspberry Pi header', 'receives the clocks'), ('dac', 'GY-PCM5102 DAC board', 'jumpers 1 L · 2 L · 3 H · 4 L')]
for k, t, s in heads:
    x = COLX[k]
    a(f'<rect x="{x-130}" y="{TOP-58}" width="260" height="50" rx="10" fill="#212121"/>')
    a(f'<text x="{x}" y="{TOP-37}" font-size="16" font-weight="700" fill="#fff" text-anchor="middle">{t}</text>')
    a(f'<text x="{x}" y="{TOP-18}" font-size="12" fill="#c7c7cc" text-anchor="middle">{s}</text>')
for i, (lab, kind, ad, pi, da, dirn, note) in enumerate(rows):
    y = TOP + 30 + i * ROW
    col = C[kind]
    if i % 2 == 0:
        a(f'<rect x="20" y="{y-ROW/2+2}" width="{W-40}" height="{ROW-4}" rx="6" fill="#f4f4f6"/>')
    a(f'<text x="34" y="{y-4}" font-size="14" font-weight="700" fill="{col}">{lab}</text>')
    a(f'<text x="34" y="{y+14}" font-size="12" fill="#7b7b7b">{dirn}</text>')
    pins = [(k, v) for k, v in (('adc', ad), ('pi', pi), ('dac', da)) if v]
    xs = [COLX[k] for k, _ in pins]
    # the wire: pill to pill, an arrowhead at each receiver (ground has none)
    half = {'adc': 38, 'pi': 75, 'dac': 38}
    for (k0, _), (k1, _) in zip(pins, pins[1:]):
        x0, x1 = COLX[k0] + half[k0], COLX[k1] - half[k1]
        mk = '' if kind == 'ground' else ' marker-end="url(#arr)"'
        a(f'<line x1="{x0}" y1="{y}" x2="{x1 - (0 if kind == "ground" else 2)}" y2="{y}" stroke="{col}" stroke-width="4"{mk}/>')
    for k, v in pins:
        x = COLX[k]
        w = 150 if k == 'pi' else 76
        a(f'<rect x="{x-w/2}" y="{y-15}" width="{w}" height="30" rx="15" fill="#fff" stroke="{col}" stroke-width="2.5"/>')
        a(f'<text x="{x}" y="{y+5}" font-size="14" font-weight="700" fill="#212121" text-anchor="middle">{html.escape(v)}</text>')
    if note:
        a(f'<text x="{W-34}" y="{y+29 if len(pins)>2 else y+30}" font-size="11.5" fill="#7b7b7b" text-anchor="end" font-style="italic">{html.escape(note)}</text>')
yb = TOP + ROW * len(rows) + 20
notes = [
  'Keep BCK, LRCK and MCK short (under ~10 cm): BCK runs at 3.07 MHz.',
  'Power the ADC from the same 5 V supply as the Pi (one ground), or feed its VDD33 from Pi pin 1 with its USB-C unplugged.',
  'ADC in: line level, 3 Vp-p. DAC out: about 2 V RMS, a hot line out. For guitar and pedals use the buffer board (docs/buffer.svg).',
  'Software: dtoverlay=nhe-i2s-duplex and the nhe-i2s-codec module (README). Run JACK at 48000 Hz.',
]
for j, n in enumerate(notes):
    a(f'<text x="40" y="{yb + 22*j}" font-size="13.5" fill="#323232">• {html.escape(n)}</text>')
a('</svg>')
open('docs/wiring.svg', 'w').write('\n'.join(o))
