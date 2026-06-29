import argparse
from math import sqrt

import skrf as rf
from skrf.media import MLine

C0 = 299792458.0


def calculate_microstrip():
    parser = argparse.ArgumentParser(
        description=(
            "Calculate microstrip characteristic impedance and effective permittivity. "
            "This script computes both quasi-static and dispersive values using the "
            "Hammerstad & Jensen model, and calculates frequency limits for single-mode "
            "propagation and surface-wave excitation."
        ),
        add_help=False
    )
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    parser.add_argument("-f", "--freq", type=float, required=True, help="Frequency (GHz)")
    parser.add_argument("-w", "--width", type=float, required=True, help="Trace width (mm)")
    parser.add_argument("-h", "--height", type=float, required=True, help="Substrate height (mm)")
    parser.add_argument("-er", "--eps-r", type=float, required=True, help="Relative permittivity of substrate (-)")
    parser.add_argument("-t", "--thick", type=float, default=0.0, help="Conductor thickness (mm)")
    parser.add_argument("-p", "--precision", type=int, default=2, help="Decimal places for output (default: 2)")
    args = parser.parse_args()

    # Input validations
    if args.freq <= 0:
        parser.error("Frequency must be greater than 0 GHz.")
    if args.width <= 0:
        parser.error("Trace width must be greater than 0 mm.")
    if args.height <= 0:
        parser.error("Substrate height must be greater than 0 mm.")
    if args.eps_r < 1.0:
        parser.error("Relative permittivity (eps_r) must be greater than or equal to 1.0.")
    if args.thick < 0:
        parser.error("Conductor thickness (t) cannot be negative.")

    # Calculate limits (c0 is in m/s, convert dimensions to mm for calculation using c = 299.792458 mm/ns)
    c_mm_ns = 299.792458
    
    # 1. Transverse resonance cutoff frequency
    f_tr = c_mm_ns / (sqrt(args.eps_r) * (2.0 * args.width + 0.8 * args.height))
    
    # 2. First TE surface wave mode cutoff frequency
    if args.eps_r > 1.0:
        f_te1 = c_mm_ns / (4.0 * args.height * sqrt(args.eps_r - 1.0))
    else:
        f_te1 = float('inf')

    # Gather warnings
    warnings = []
    
    # Model range warnings
    w_h_ratio = args.width / args.height
    if w_h_ratio < 0.1 or w_h_ratio > 10.0:
        warnings.append(
            f"Width-to-Height ratio (W/H = {w_h_ratio:.3f}) is outside the standard "
            "Hammerstad & Jensen model optimal range (0.1 <= W/H <= 10.0)."
        )
    if args.thick > 0 and args.thick / args.height >= 0.25:
        warnings.append(
            f"Thickness-to-Height ratio (T/H = {args.thick/args.height:.3f}) is high. "
            "Thickness correction formulas are less accurate when T/H >= 0.25."
        )
    if args.thick >= args.height:
        warnings.append(
            f"Trace thickness (T = {args.thick} mm) is greater than or equal to "
            f"substrate height (H = {args.height} mm), which violates typical microstrip geometry."
        )
        
    # High frequency / mode propagation warnings
    if args.freq >= f_tr:
        warnings.append(
            f"LIMIT EXCEEDED: Operating frequency ({args.freq:.2f} GHz) is above the first higher-order "
            f"transverse resonance mode cutoff frequency (f_TR = {f_tr:.2f} GHz). "
            "Quasi-TEM single-mode propagation assumption is violated. Results are physically unreliable."
        )
    elif args.freq >= 0.9 * f_tr:
        warnings.append(
            f"WARNING: Operating frequency ({args.freq:.2f} GHz) is close to the first higher-order "
            f"transverse resonance mode cutoff (f_TR = {f_tr:.2f} GHz). "
            "Dispersion is significant and higher-order modes may be excited at discontinuities."
        )

    if args.freq >= f_te1:
        warnings.append(
            f"LIMIT EXCEEDED: Operating frequency ({args.freq:.2f} GHz) is above the first TE surface-wave "
            f"mode cutoff frequency (f_TE1 = {f_te1:.2f} GHz). "
            "Power will leak into surface waves, causing radiation loss and crosstalk. Results are physically unreliable."
        )
    elif args.freq >= 0.9 * f_te1:
        warnings.append(
            f"WARNING: Operating frequency ({args.freq:.2f} GHz) is close to the first TE surface-wave "
            f"mode cutoff (f_TE1 = {f_te1:.2f} GHz). "
            "Surface wave excitation risks are elevated."
        )

    # Calculate microstrip properties using scikit-rf
    line = MLine(
        frequency=rf.Frequency(args.freq, args.freq, 1, "GHz"),
        w=args.width * 1e-3,
        h=args.height * 1e-3,
        t=args.thick * 1e-3,
        ep_r=args.eps_r,
    )

    freq_hz = args.freq * 1e9
    guided_wl = (C0 / (freq_hz * sqrt(line.ep_reff_f[0].real))) * 1e3

    width = 3 + 1 + args.precision  # 3 for digits, 1 for decimal point, plus precision
    print('\nDisclaimer: Quasi-static calculations assume TEM mode propagation. Dispersive calculations include frequency-dependent effects.')
    print(f"\n=== Microstrip results at {args.freq} GHz ===")
    
    print("\n--- Electromagnetic properties ---")
    print("Quasi-static approximation:")
    print(f"  Line impedance:         {line.zl_eff[0].real:>{width}.{args.precision}f} Ω")
    print(f"  Effective permittivity: {line.ep_reff[0].real:>{width}.{args.precision}f}")
    print("Dispersive values:")
    print(f"  Line impedance:         {line._z_characteristic[0].real:>{width}.{args.precision}f} Ω")
    print(f"  Effective permittivity: {line.ep_reff_f[0].real:>{width}.{args.precision}f}")
    print(f"  Guided wavelength:      {guided_wl:>{width}.{args.precision}f} mm")
    print("---------------------------------")
    
    print("\n--- Dimensions ---")
    print(f"Trace width (W):        {args.width:>{width}.{args.precision}f} mm")
    print(f"Substrate height (H):   {args.height:>{width}.{args.precision}f} mm")
    print(f"Trace thickness (T):    {args.thick:>{width}.{args.precision}f} mm")
    print(f"Permittivity (eps_r):   {args.eps_r:>{width}.{args.precision}f}")
    print("---------------------------------")
    
    print("\n--- Frequency Limits ---")
    print(f"Transverse resonance (f_TR): {f_tr:>{width}.{args.precision}f} GHz")
    if f_te1 != float('inf'):
        print(f"First TE surface wave (f_TE1): {f_te1:>{width}.{args.precision}f} GHz")
    else:
        print("First TE surface wave (f_TE1):   N/A (eps_r = 1.0)")
    print("---------------------------------")

    if warnings:
        print("\n!!! WARNINGS / LIMIT VIOLATIONS !!!")
        for warning in warnings:
            print(f"- {warning}")
        print("-----------------------------------\n")
    else:
        print()


if __name__ == "__main__":
    calculate_microstrip()
