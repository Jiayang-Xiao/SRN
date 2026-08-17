# SRN Autonomous Environment

**Created:** 2026-08-17  
**Path:** `/home/xjy/ARIS/.envs/srn-autonomous`  
**Construction:** Python `venv` with `--system-site-packages`, inheriting the
project-recommended `/home/xjy/.conda/envs/aris-torch` environment.

## Creation commands

```bash
/home/xjy/.conda/envs/aris-torch/bin/python -m venv \
  --system-site-packages /home/xjy/ARIS/.envs/srn-autonomous

XDG_CACHE_HOME=/home/xjy/ARIS/.cache \
PIP_CACHE_DIR=/home/xjy/ARIS/.cache/pip \
/home/xjy/ARIS/.envs/srn-autonomous/bin/python -m pip install \
  scipy==1.15.3 opencv-python-headless==4.12.0.88 \
  matplotlib==3.10.5 pytest==8.4.1 tqdm==4.67.1
```

## Runtime versions

| Component | Version/status |
|---|---|
| Python | 3.10.20 |
| PyTorch | 2.4.1 |
| torchvision | 0.19.1 |
| PyTorch CUDA build | 12.1 |
| CUDA available | false (NVML/device-node blocker) |
| NumPy | 2.2.6 |
| PyYAML | 6.0.3 |
| SciPy | 1.15.3 |
| OpenCV headless | 4.12.0 |
| Pillow | 12.2.0 |
| Matplotlib | 3.10.5 |
| pytest | 8.4.1 |
| tqdm | 4.67.1 |
| CairoSVG | 2.8.2 |
| XeTeX / TinyTeX | 0.999998 / TeX Live 2026, project-local |

Set project-local caches for all runs:

```bash
export HF_HOME=/home/xjy/ARIS/.cache/huggingface
export TORCH_HOME=/home/xjy/ARIS/.cache/torch
export XDG_CACHE_HOME=/home/xjy/ARIS/.cache
export MPLCONFIGDIR=/home/xjy/ARIS/.cache/matplotlib
```

`requirements-srn-autonomous.txt` records the packages added by this sprint. The
base deep-learning packages remain inherited from `aris-torch` to avoid copying
or destructively mutating the shared recommended environment.

## Paper toolchain

- Functional TeX root: `/home/xjy/ARIS/.envs/.TinyTeX` (project-local, about 186 MB).
- Engine: XeTeX/XeLaTeX from TeX Live 2026; build driver: `latexmk`.
- Added TinyTeX packages: `eso-pic`, `fancyhdr`, `natbib`, `multirow`, `cleveref`,
  `microtype`, and `collection-fontsrecommended`.
- A first Conda `texlive-core` attempt under `.envs/srn-tex` was incomplete because its
  format builder omitted `mktexlsr.pl`; the failure is preserved in
  `logs/tex_env_install.log`. TinyTeX resolved the blocker without root access.
- Figure raster/vector conversion additionally uses CairoSVG 2.8.2 installed into
  `.envs/srn-autonomous`.
