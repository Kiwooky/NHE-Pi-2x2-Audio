# NHE Pi 2x2 Audio: PCM1808 in, PCM5102A out

Stereo in and out on a Raspberry Pi's I2S pins, with a PCM1808 ADC board
(the clock master: its own 12.288 MHz crystal, 48 kHz) and a GY-PCM5102 DAC
board following the same clocks. Same wiring and files on a Pi 5 and a
Pi 3B+.

## Wiring

![Wiring map: one row per wire between the PCM1808 board, the Pi header and the PCM5102 board](docs/wiring.svg)

| Signal       | ADC (PCM1808) | Pi header          | DAC (GY-PCM5102)        |
|--------------|---------------|--------------------|-------------------------|
| Bit clock    | BCK (out)     | pin 12, GPIO 18    | BCK                     |
| Word clock   | LRCK (out)    | pin 35, GPIO 19    | LCK                     |
| Audio in     | DATA (out)    | pin 38, GPIO 20    |                         |
| Audio out    |               | pin 40, GPIO 21    | DIN                     |
| Master clock | MCK (out)     |                    | SCK (or SCK to GND)     |
| Ground       | GND           | pin 6 / 9 / 14     | GND                     |
| Power        | USB-C 5 V, same supply as the Pi (or VDD33 from pin 1, USB-C unplugged) | | VIN to pin 2 or 4 (5 V) |

- **DAC jumpers** on the back: 1 = L, 2 = L, 3 = H, 4 = L (3 is XSMT: on L the DAC stays silent). Leave the SCK jumper open if MCK feeds SCK.
- **Short clock wires** (BCK is ~3 MHz): under ~10 cm.
- **Levels:** the ADC takes line level (3 Vp-p, ~1 V RMS); a guitar needs a buffer in front. The DAC puts out ~2 V RMS: a line output.
- **48 kHz only** (the ADC's crystal): run JACK at 48000.

## Buffer board (guitar in, pedal-level out)

![Buffer board schematic: two high-impedance inputs, two padded and buffered outputs, power and bias, TL074 pinout](docs/buffer.svg)

One TL074 on veroboard, between the jacks and the two audio boards:

- **Inputs (TL074 A and B):** a buffer for a guitar, in front of the ADC board's
  3.5 mm jack. **S1** picks the input impedance: about 0.9 / 1.8 / 3.2 MΩ (R3a/b/c in
  parallel with R2's 10 MΩ; higher keeps more of a single coil's top end, and picks
  up more hum: keep the input wiring short and shielded). Unity gain: the ADC
  clips at 3 Vp-p, which leaves a single coil 4-10 dB of headroom. Add gain in
  software (a gain plugin) if you want it; the PCM1808's ~99 dB of range has room.
- **Outputs (TL074 C and D):** after the DAC board's jack. **S3 INST** pads its ~2 V RMS
  line level down by 15 dB to about 0.38 V RMS, a hot-guitar level for pedals and amps;
  **LINE** passes it straight through, buffered.
- **Power: one supply for the whole unit, the Pi's USB-C charger.** A small isolated
  DC-DC module (U2, B0512S-1W) turns the Pi's 5 V (header pin 4) into ±12 V for the
  TL074. A split supply puts the signal at 0 V with about ±10 V of swing, so there's
  no bias divider, and LINE mode takes the DAC's full ~6 Vp-p. The module draws about
  0.25 A from the 5 V. Its 0 V joins the audio ground at one point (the ADC board's GND).
  R13/R14 with C6/C8 filter the module's switching noise; it's unregulated, so with
  the TL074's light load the rails may sit nearer ±13-14 V (fine: the TL074 takes ±18 V).

| Part | Each | For |
|---|---|---|
| TL074 (DIP-14) + socket | 1 | |
| B0512S-1W (5 V in, ±12 V out, 1 W, isolated) | 1 | U2 |
| 1k / 10M / 1M / 2.2M / 4.7M | 2 each | R1, R2, R3a, R3b, R3c |
| 10k | 2 + 2 | R4 (inputs); R8 (outputs) |
| 2.2k / 100R / 100k | 2 / 4 / 4 | R9; R6, R11; R7, R12 |
| 1M | 2 | R10 |
| 10R | 2 | R13, R14 (rail filters) |
| 100n film / 1µ film | 2 / 2 | C1; C4 |
| 100p ceramic | 2 | C9 |
| 10µ non-polar electrolytic | 4 | C3, C5 |
| 100µ electrolytic, 25 V | 2 | C6 (+12 V), C8 (−12 V, + side to GND) |
| 10µ electrolytic, 16 V | 1 | C10, at the module's input |
| 100n ceramic | 2 | C7 (pin 4 to GND), C11 (pin 11 to GND), at the chip |
| SP3T (or rotary) / SPDT | 2 / 2 | S1; S3 |
| 3.5 mm plugs (to the boards), ¼" jacks | | |

Values are a starting point for the breadboard, not yet measured on hardware.

## Build and install (on the Pi)

```sh
sudo apt install device-tree-compiler
sudo apt install linux-headers-$(uname -r)      # if not found: raspberrypi-kernel-headers
make
sudo make install
```

Then in `/boot/firmware/config.txt` (older images: `/boot/config.txt`), add:

```
dtoverlay=nhe-i2s-duplex
```

(remove `dtoverlay=hifiberry-dac` if you tried the DAC on its own first), and `sudo reboot`.

After a kernel update: `make` and `sudo make install` again (a module is built for one kernel).

## Check it

```sh
aplay -l          # a card "nhe-duplex"
arecord -l        # the same card
speaker-test -D plughw:CARD=nheduplex -c 2 -r 48000 -t sine -f 440
arecord -D plughw:CARD=nheduplex -f S32_LE -r 48000 -c 2 -d 5 test.wav && aplay -D plughw:CARD=nheduplex test.wav
```

(`aplay -l` shows the card's id if it differs from `nheduplex`.) Then pick it
in `sudo patchbox` → JACK: 48000 Hz.

If nothing shows: `dmesg | grep -i -E "nhe|asoc|i2s"`.

## What the files are

- `nhe-i2s-duplex-overlay.dts`: the overlay. The Pi's I2S receives the
  clocks (`i2s_clk_consumer`: the RP1's second I2S block on a Pi 5, the
  BCM2835's I2S on a Pi 3), 2 x 32-bit slots (BCK = 64 fs). Based on the
  kernel's `i2s-master-dac` overlay, which is playback only.
- `nhe-i2s-codec.c`: a stand-in codec. Neither chip has a control bus, so
  there's nothing to drive: it tells ALSA the bus carries stereo in and out,
  16/24/32-bit, 48 kHz. The kernel's own stand-ins are one-way
  (`linux,spdif-dit`, `linux,spdif-dir`) or 16-bit (`asahi-kasei,ak4554`).

## Checked so far (not yet on hardware)

- The overlay compiles and applies to the Pi 5 (`bcm2712-rpi-5-b`) and Pi 3B+
  (`bcm2710-rpi-3-b-plus`) device trees from the Raspberry Pi kernel
  (6.18, Nov 2026): the sound card takes its clocks from the codec, the
  Pi 5's consumer I2S (`i2s@a4000`) is switched on, on GPIO 18-21.
  (Checked with `fdtoverlay`, which can't read the `card-name` option or a
  label on an `__overlay__`; the Pi firmware can.)
- The module compiles for the Pi 5 kernel config (`bcm2712_defconfig`), no
  warnings at `W=1`.
- An old Pi 3 kernel (Patchbox's 2022 image) may not know `i2s_clk_consumer`:
  if `dtoverlay=nhe-i2s-duplex` fails there, replace it with `i2s` in the
  overlay (three places) and rebuild.

## Licence

GPL-2.0 (the kernel module and overlay are built against the Linux kernel). © 2026 New Horizon Electronics.
