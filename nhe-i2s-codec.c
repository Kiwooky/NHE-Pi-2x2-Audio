// SPDX-License-Identifier: GPL-2.0
/*
 * nhe-i2s-codec: a stand-in codec for two control-less I2S chips on one bus
 * that make their own clocks, e.g. a PCM1808 ADC (the clock master, with its
 * own 12.288 MHz crystal) and a PCM5102A DAC following the same BCK / LRCK.
 *
 * Neither chip has a control bus, so the kernel has nothing to talk to: this
 * only tells ALSA what the bus can carry. Stereo in and out, 16/24/32-bit,
 * at 48 kHz only, because that is what the PCM1808's crystal gives (256 fs,
 * BCK 64 fs): offering other rates would let JACK pick one the hardware
 * isn't running at, and the audio would play at the wrong speed.
 *
 * The kernel's own stand-ins don't fit: linux,spdif-dit is playback only,
 * linux,spdif-dir capture only, and asahi-kasei,ak4554 is both but 16-bit.
 *
 * Device tree: compatible = "nhe,i2s-codec" (overlay nhe-i2s-duplex).
 *
 * Copyright (C) 2026 New Horizon Electronics
 */

#include <linux/module.h>
#include <linux/of.h>
#include <linux/platform_device.h>
#include <sound/soc.h>

#define NHE_RATES	SNDRV_PCM_RATE_48000
#define NHE_FORMATS	(SNDRV_PCM_FMTBIT_S16_LE | SNDRV_PCM_FMTBIT_S24_LE | \
			 SNDRV_PCM_FMTBIT_S32_LE)

static const struct snd_soc_dapm_widget nhe_widgets[] = {
	SND_SOC_DAPM_INPUT("AINL"),
	SND_SOC_DAPM_INPUT("AINR"),
	SND_SOC_DAPM_OUTPUT("AOUTL"),
	SND_SOC_DAPM_OUTPUT("AOUTR"),
};

static const struct snd_soc_dapm_route nhe_routes[] = {
	{ "Capture", NULL, "AINL" },
	{ "Capture", NULL, "AINR" },
	{ "AOUTL", NULL, "Playback" },
	{ "AOUTR", NULL, "Playback" },
};

static struct snd_soc_dai_driver nhe_dai = {
	.name = "nhe-i2s-hifi",
	.playback = {
		.stream_name	= "Playback",
		.channels_min	= 2,
		.channels_max	= 2,
		.rates		= NHE_RATES,
		.formats	= NHE_FORMATS,
	},
	.capture = {
		.stream_name	= "Capture",
		.channels_min	= 2,
		.channels_max	= 2,
		.rates		= NHE_RATES,
		.formats	= NHE_FORMATS,
	},
	/* one bus, one clock: both directions at the same rate */
	.symmetric_rate = 1,
};

static const struct snd_soc_component_driver nhe_component = {
	.dapm_widgets		= nhe_widgets,
	.num_dapm_widgets	= ARRAY_SIZE(nhe_widgets),
	.dapm_routes		= nhe_routes,
	.num_dapm_routes	= ARRAY_SIZE(nhe_routes),
	.idle_bias_on		= 1,
	.use_pmdown_time	= 1,
	.endianness		= 1,
};

static int nhe_codec_probe(struct platform_device *pdev)
{
	return devm_snd_soc_register_component(&pdev->dev, &nhe_component,
					       &nhe_dai, 1);
}

static const struct of_device_id nhe_codec_of_match[] = {
	{ .compatible = "nhe,i2s-codec" },
	{ }
};
MODULE_DEVICE_TABLE(of, nhe_codec_of_match);

static struct platform_driver nhe_codec_driver = {
	.driver = {
		.name		= "nhe-i2s-codec",
		.of_match_table	= nhe_codec_of_match,
	},
	.probe = nhe_codec_probe,
};
module_platform_driver(nhe_codec_driver);

MODULE_DESCRIPTION("Stand-in codec for a control-less I2S ADC + DAC pair (PCM1808 + PCM5102A)");
MODULE_AUTHOR("New Horizon Electronics");
MODULE_LICENSE("GPL");
