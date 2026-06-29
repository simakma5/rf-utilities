# RF Utilities

A collection of lightweight command-line utilities for PCB RF transmission line calculations and antenna design.

## Features

- **Symmetric Stripline Calculator (`stripline_impedance.py`)**:
  - Calculates line impedance, effective permittivity, and guided wavelength using the IPC-2141 approximation.
  - Aligned with standard RF/PCB community conventions: $H$ represents the dielectric height of a single layer (trace-to-ground spacing), and total ground-to-ground spacing is $2H + T$.
- **Microstrip Line Calculator (`mline_impedance.py`)**:
  - Calculates characteristic impedance and effective permittivity for both quasi-static and frequency-dispersive models (utilizing the Hammerstad & Jensen model via `scikit-rf`).
  - Automatically checks and warns/errors if operating frequency exceeds single-mode limits:
    - **Transverse resonance limit ($f_{TR}$)**: $f_{TR} = c_0 / (\sqrt{\epsilon_r} (2W + 0.8H))$
    - **First TE surface wave limit ($f_{TE1}$)**: $f_{TE1} = c_0 / (4H\sqrt{\epsilon_r - 1})$
- **Patch Antenna Designer (`patch_design.py`)**:
  - Computes rectangular microstrip patch antenna dimensions (Width and Length) using the transmission line model.
  - Warns about substrate thickness bounds:
    - **Electrically thin ($H < 0.01\lambda_0$)**: Leads to poor radiation efficiency and narrow bandwidth.
    - **Electrically thick ($H > 0.1\lambda_0$)**: Leads to severe surface-wave excitation and pattern distortion.

## Requirements & Installation

This project requires Python 3.12+ and `scikit-rf`.

You can install dependencies using `pip`:
```bash
pip install -r pyproject.toml
```
Or, if you are using `uv`:
```bash
uv sync
```

## Usage Examples

### Stripline Impedance
Calculate symmetric stripline properties at 1 GHz for a 0.5 mm wide trace, 0.8 mm dielectric height (H), on FR-4 ($\epsilon_r = 4.4$) with 1 oz copper ($T = 0.035$ mm):
```bash
python3 stripline_impedance.py -f 1.0 -w 0.5 -h 0.8 -er 4.4 -t 0.035
```

### Microstrip Impedance & Frequency Limits
Calculate microstrip impedance at 10 GHz for a 1.5 mm wide trace, 0.8 mm substrate height, on FR-4:
```bash
python3 mline_impedance.py -f 10.0 -w 1.5 -h 0.8 -er 4.4 -t 0.035
```

### Patch Antenna Design
Calculate microstrip patch antenna dimensions for 10 GHz on a 1.6 mm substrate:
```bash
python3 patch_design.py -f 10.0 -h 1.6 -er 4.4
```
