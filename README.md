# HF Gem Radar: Local LLM & MMLLM Scout

A modular intelligence tool engineered to scout, score, and surface standout open-source models within your hardware's operational range — finding the hidden gems buried under the waves of mainstream fame.

---

## Quickstart

Run with one command (defaults to your operational range `3B–12B`, LLMs & MMLLMs, post-2024 cutoff):
```bash
python radar.py
```

### Common Commands

```bash
# Focus strictly on GGUF quantized models for local offload
python radar.py --gguf-only

# Expand operational envelope up to 14B or 32B
python radar.py --params "min:0,max:14B"
python radar.py --params "min:6B,max:32B"

# Quick scan (e.g. limit to first 5 pages per tag)
python radar.py --max-pages 5

# Deep multi-angle keyword search (abliterated, uncensored, RP, SillyTavern)
python radar.py --mode keywords

# Custom output destination
python radar.py --output my_scouted_gems.csv
```

---

## How It Finds Hidden Gems

Mainstream Hugging Face sorting only shows models with hundreds of thousands of accumulated downloads ("the fame wave"). The Gem Radar calculates:

1. **Log-Space Euclidean Magnitude (`magnitude`)**:
   $$\text{magnitude} = \sqrt{(\log_{10}(\text{likes}))^2 + (\log_{10}(\text{downloads}))^2}$$
   *Direct parity with your Excel formula `=SQRT(G2^2 + I2^2)`.* Normalizes power-law engagement into a 2D vector space.

2. **Quality Angle ($\theta$)**:
   $$\theta = \arctan\left(\frac{\log_{10}(\text{likes})}{\log_{10}(\text{downloads})}\right)$$
   Models with high angles possess disproportionately high acclaim relative to their raw download count.

3. **Gem Residual**:
   $$\text{Residual} = \log_{10}(\text{likes}) - 0.75 \cdot \log_{10}(\text{downloads})$$
   Isolates models that sit high above the baseline fame curve.

4. **Appreciation Rate (%)**:
   $$(\text{Likes} / \text{Downloads}) \times 100$$
   Community satisfaction density.

5. **Linear Popularity Magnitude (`DL_Mag`)**:
   $$\sqrt{\text{Downloads}^2 + \text{Likes}^2}$$

---

## Leaderboards Surfaced by Default

Every scan automatically analyzes and renders four curated leaderboards:
1. 💎 **Top Hidden Gems**: Outlier models with high appreciation and high quality angles, fame-capped to filter out the multi-million download corporate giants.
2. 👁️ **Standout Local MMLLMs**: Multimodal vision/video models (`image-text-to-text`, `video-text-to-text`) in your local VRAM range.
3. 🔓 **Top Uncensored & Abliterated Crafts**: Specialized de-aligned, abliterated, and creative roleplay fine-tunes.
4. ⚡ **Top GGUF Models**: Quantized models ranked by 2D engagement magnitude.

---

## Directory Structure

```
huggingface_scrubber/
├── radar.py                  # CLI runner & interactive scout
├── README.md                 # Documentation
├── hf_radar/                 # Modular Python package
│   ├── __init__.py           # Package exports
│   ├── client.py             # Resilient HF API client & pagination
│   ├── metrics.py            # Log10, Euclidean magnitudes & Gem scores
│   ├── normalizer.py         # Metadata, Excel serial dates & archetype flags
│   ├── scout.py              # Orchestrator across pipeline tags & parameters
│   └── leaderboards.py       # Filtering, ranking & console table displays
├── archive/                  # Historical backup of original scripts (hfdata, hfscrape, hfsnapshot*)
├── huggingface_snapshot.csv  # Output dataset
├── huggingface_snapshot.xlsx # Historical spreadsheet v1
└── huggingface_snapshot_v2.xlsx # Historical spreadsheet v2
```
