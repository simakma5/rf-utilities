import argparse
from math import log, sqrt

import skrf as rf
from skrf.media import DefinedGammaZ0

C0 = 299792458.0


def calculate_stripline():
    parser = argparse.ArgumentParser(
        description=(
            'Calculate symmetric stripline impedance and permittivity using the IPC-2141 approximation. '
            'In the RF community, the dielectric height parameter H conventionally refers to the thickness '
            'of a single layer (the distance from the conductor/trace to either ground plane), making the '
            'total ground-to-ground spacing 2H + T (where T is trace thickness).'
        ),
        add_help=False
    )
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    parser.add_argument('-f', '--freq', type=float, required=True, help='Frequency (GHz)')
    parser.add_argument('-w', '--width', type=float, required=True, help='Trace width (mm)')
    parser.add_argument(
        '-h', '--height', type=float, required=True,
        help='Dielectric height H (distance from trace to either ground plane, i.e., half the total height) (mm)'
    )
    parser.add_argument('-er', '--eps-r', type=float, required=True, help='Relative permittivity of substrate (-)')
    parser.add_argument('-t', '--thick', type=float, default=0.0, help='Conductor/trace thickness (mm)')
    parser.add_argument('-p', '--precision', type=int, default=2, help='Decimal places for output (default: 2)')
    args = parser.parse_args()

    # Input validations
    if args.freq <= 0:
        parser.error("Frequency must be greater than 0 GHz.")
    if args.width <= 0:
        parser.error("Trace width must be greater than 0 mm.")
    if args.height <= 0:
        parser.error("Dielectric height (H) must be greater than 0 mm.")
    if args.eps_r < 1.0:
        parser.error("Relative permittivity (eps_r) must be greater than or equal to 1.0.")
    if args.thick < 0:
        parser.error("Conductor thickness (t) cannot be negative.")

    # Calculate total height b = 2*H + T
    total_height = 2.0 * args.height + args.thick
    denominator = 0.8 * args.width + args.thick

    # Check validity for IPC-2141 logarithm argument
    if denominator <= 0 or (1.9 * total_height) / denominator <= 1.0:
        parser.error(
            f"Invalid dimensions: width={args.width} mm, thickness={args.thick} mm, height={args.height} mm. "
            f"The logarithmic term argument (1.9 * (2H + T) / (0.8W + T)) must be greater than 1.0 (got "
            f"{(1.9 * total_height) / denominator:.3f} if calculated) to yield a positive impedance."
        )

    # IPC-2141 Symmetric Stripline characteristic impedance approximation:
    # Z0 = (60 / sqrt(er)) * ln(1.9 * b / (0.8 * w + t))
    # where b is the total distance between ground planes (2H + T)
    z0_calc = (60.0 / sqrt(args.eps_r)) * log(
        (1.9 * total_height) / denominator
    )

    # Define the propagation constant gamma = alpha + j*beta
    # For a lossless TEM medium: alpha = 0, beta = 2*pi*f*sqrt(er)/c
    freq_hz = args.freq * 1e9
    omega = 2.0 * 3.141592653589793 * freq_hz
    beta = (omega * sqrt(args.eps_r)) / C0
    gamma = 0.0 + 1j * beta

    # Generate the transmission line medium using scikit-rf
    line = DefinedGammaZ0(
        frequency=rf.Frequency(args.freq, args.freq, 1, 'GHz'),
        z0=z0_calc,
        gamma=gamma
    )

    width = 3 + 1 + args.precision  # 3 for digits, 1 for decimal point, plus precision
    print(f'\nDisclaimer: H = single-layer dielectric height (trace-to-ground spacing). Total ground-to-ground spacing is 2H + T.')
    print(f'\n=== Stripline results at {args.freq} GHz ===')
    print('\n--- Electromagnetic properties ---')
    print(f'Line impedance:         {line.z0[0].real:>{width}.{args.precision}f} Ω')
    print(f'Effective permittivity: {args.eps_r:>{width}.{args.precision}f}')
    print(f'Guided wavelength:      {(C0 / (freq_hz * sqrt(args.eps_r)) * 1e3):>{width}.{args.precision}f} mm')
    print('---------------------------------')
    print('\n--- Dimensions ---')
    print(f'Dielectric height (H):  {args.height:>{width}.{args.precision}f} mm')
    print(f'Trace thickness (T):    {args.thick:>{width}.{args.precision}f} mm')
    print(f'Ground plane spacing:   {total_height:>{width}.{args.precision}f} mm')
    print('---------------------------------\n')


if __name__ == '__main__':
    calculate_stripline()
