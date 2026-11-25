# NHE Pi 2x2 Audio: PCM1808 in, PCM5102A out

Stereo in and out on a Raspberry Pi's I2S pins, with a PCM1808 ADC board
(the clock master: its own 12.288 MHz crystal, 48 kHz) and a GY-PCM5102 DAC
board following the same clocks. Same wiring and files on a Pi 5 and a
Pi 3B+.

## Wiring

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
