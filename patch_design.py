import argparse
import math

C0 = 299792458.0


def calculate_patch():
    parser = argparse.ArgumentParser(
        description=(
            "Calculate rectangular microstrip patch antenna dimensions (width and length) "
            "using standard transmission line model equations, and evaluate substrate height limits."
        ),
        add_help=False
    )
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    parser.add_argument("-f", "--freq", type=float, required=True, help="Operating frequency (GHz)")
    parser.add_argument("-h", "--height", type=float, required=True, help="Substrate height (mm)")
    parser.add_argument("-er", "--eps-r", type=float, required=True, help="Relative permittivity (-)")
    parser.add_argument("-p", "--precision", type=int, default=2, help="Decimal places for output (default: 2)")
    args = parser.parse_args()

    # Input validations
    if args.freq <= 0:
        parser.error("Frequency must be greater than 0 GHz.")
    if args.height <= 0:
        parser.error("Substrate height must be greater than 0 mm.")
    if args.eps_r < 1.0:
        parser.error("Relative permittivity (eps_r) must be greater than or equal to 1.0.")

    f_hz = args.freq * 1e9
    h_m = args.height * 1e-3
    eps_r = args.eps_r

    # Standard rectangular patch formulas
    w_m = (C0 / (2.0 * f_hz)) * math.sqrt(2.0 / (eps_r + 1.0))
    eps_reff = ((eps_r + 1.0) / 2.0) + ((eps_r - 1.0) / 2.0) * math.pow(1.0 + 12.0 * (h_m / w_m), -0.5)
    delta_l = 0.412 * h_m * (eps_reff + 0.3) * (w_m / h_m + 0.264) / ((eps_reff - 0.258) * (w_m / h_m + 0.8))
    l_eff = C0 / (2.0 * f_hz * math.sqrt(eps_reff))
    l_m = l_eff - 2.0 * delta_l

    # Substrate thickness relative to wavelength
    lambda_0_mm = (C0 / f_hz) * 1e3
    h_lambda = args.height / lambda_0_mm

    # Gather warnings
    warnings = []
    if h_lambda < 0.01:
        warnings.append(
            f"Substrate is electrically very thin (H = {h_lambda:.4f} * lambda_0). "
            "Antenna efficiency will be low and bandwidth extremely narrow."
        )
    elif h_lambda < 0.025:
        warnings.append(
            f"Substrate is electrically thin (H = {h_lambda:.4f} * lambda_0). "
            "Bandwidth will be relatively narrow (typically < 1-2%)."
        )
    elif h_lambda > 0.1:
        warnings.append(
            f"Substrate is electrically very thick (H = {h_lambda:.4f} * lambda_0). "
            "Surface-wave excitation will be severe, causing degraded efficiency and radiation pattern distortion."
        )

    if eps_r > 12.0:
        warnings.append(
            f"Relative permittivity is very high (eps_r = {eps_r:.2f}). "
            "This will result in narrow bandwidth and small patch dimensions, making fabrication difficult."
        )

    width = 3 + 1 + args.precision  # 3 for digits, 1 for decimal point, plus precision
    print('\nDisclaimer: Microstrip patch antenna dimensions are calculated using transmission line model approximations.')
    print(f"\n=== Patch antenna dimensions at {args.freq} GHz ===")
    
    print("\n--- Physical dimensions ---")
    print(f"Width (W):                  {w_m * 1e3:>{width}.{args.precision}f} mm")
    print(f"Length (L):                 {l_m * 1e3:>{width}.{args.precision}f} mm")
    print("--------------------------")
    
    print("\n--- Substrate properties ---")
    print(f"Substrate height (H):       {args.height:>{width}.{args.precision}f} mm")
    print(f"Permittivity (eps_r):       {args.eps_r:>{width}.{args.precision}f}")
    print(f"Effective permittivity:     {eps_reff:>{width}.{args.precision}f}")
    print(f"Fringing extension (dL):    {delta_l * 1e3:>{width}.{args.precision}f} mm")
    print("--------------------------")

    if warnings:
        print("\n!!! WARNINGS / LIMIT VIOLATIONS !!!")
        for warning in warnings:
            print(f"- {warning}")
        print("-----------------------------------\n")
    else:
        print()


if __name__ == "__main__":
    calculate_patch()
