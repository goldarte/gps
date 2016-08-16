# coding=UTF-8
# transform coordinates from GPS (WGS-84)
# to cartesian coordinates (ГОСТ 32453-2013).
# usage: convert_GPS_to_GKS(B, L, H) -> (x, y)

import math
from math import sin, cos, sqrt, fabs, pi


def geodetic_to_cartesian3D(B, L, H, a, alpha):
    """ Transfer geodetic coordinates (BLH)
    to absolute cartesian ones (XYZ)
    for ellipsoid with parameters (a, alpha).
    BLH - (radians, radians, metres);
    XYZ - metres, a - metres"""
    exc = (2 - alpha) * alpha
    N = a / sqrt(1 - pow(exc * sin(B), 2))
    X = (N + H) * cos(B) * cos(L)
    Y = (N + H) * cos(B) * sin(L)
    Z = ((1 - exc * exc) * N + H) * sin(B)
    return (X, Y, Z)


def cartesian3D_to_geodetic(X, Y, Z, a, alpha):
    """ Transfer absolute cartesian coordinates (XYZ)
    to geodetic ones (BLH)
    for ellipsoid with parameters (a, alpha).
    BLH - (radians, radians, metres);
    XYZ - metres, a - metres"""
    D = sqrt(X * X + Y * Y)
    exc = (2 - alpha) * alpha
    # calculate L
    L = 0
    if D == 0:
        B = math.copysign(math.pi / 2, Z)
        return (B, 0, Z * sin(B) - a * sqrt(1 - pow(exc * sin(B), 2)))
    else:
        La = fabs(math.asin(Y / D))
        if Y == 0 and X > 0:
            L = 0
        elif Y == 0:
            L = pi
        elif Y < 0 and X > 0:
            L = 2 * pi - La
        elif Y < 0:
            L = pi + La
        elif Y > 0 and X < 0:
            L = pi - La
        else:
            L = La
    # calculate B and H iteratively
    r = sqrt(X * X + Y * Y + Z * Z)
    c = math.asin(Z / r)
    p = exc * exc * a / (2 * r)
    max_diff = 1e-4
    s = 0
    diff = 2 * max_diff
    while diff > max_diff:
        b = c + s
        s2 = math.asin(p * sin(2 * b) / sqrt(1 - pow(exc * sin(b), 2)))
        diff = fabs(s2 - s)
        s = s2
    B = b
    H = D * cos(B) + Z * sin(B) - a * sqrt(1 - pow(exc * sin(B), 2))
    return (B, L, H)


def WGS84_to_PZ90(X, Y, Z):
    """ Transfer coordinates in WGS-84 system
    to ПЗ-90 system.
    XYZ and results - metres"""
    Xr = (1 + 0.12e-6) * (X - 0.9696e-6 * Y) + 1.1
    Yr = (1 + 0.12e-6) * (Y - 0.9696e-6 * X) + 0.3
    Zr = (1 + 0.12e-6) * Z + 0.9
    return (Xr, Yr, Zr)


def PZ90_to_SK95(X, Y, Z):
    """ Transfer from ПЗ-90 system to
    referential system - 1995
    XYZ and results - metres"""
    return (X - 25.9, Y + 130.94, Z + 81.76)


def SK95_to_GKS(B, L):
    """Transfer from referential system - 1995
    to Gauss-Kruger system.
    XY and results - metres"""
    Ldeg = L * 180.0 / pi  # longitude in radians
    n = math.floor((6 + Ldeg) / 6)  # position of 6 degree zone
    l = (Ldeg - (3 + 6 * (n - 1))) * pi / 180.0
    sinB2 = pow(sin(B), 2)
    sinB4 = pow(sinB2, 2)
    sinB6 = sinB2 * sinB4
    l2 = l * l
    x = (6367558.4968 * B - sin(2 * B) * (16002.89 + 66.9607 * sinB2 + 0.3515 * sinB4
         - l2 * (1594561.25 + 5336.535 * sinB2 + 26.79 * sinB4 + 0.149 * sinB6
                 + l2 * (672483.4 - 811219.9 * sinB2 + 5420 * sinB4 - 10.6 * sinB6
                         + l2 * (278194 - 830174 * sinB2 + 572434 * sinB4 - 16010 * sinB6
                                 + l2 * (109500 - 574700 * sinB2 + 863700 * sinB4 - 398600 * sinB6))))))
    y = ((5 + 10 * n) * 1e5 + l * cos(B) * (6378245 + 21346.1415 * sinB2 + 107.1590 * sinB4
         + 0.5977 * sinB6 + l2 * (1070204.16 - 2136826.66 * sinB2 + 17.98 * sinB4 - 11.99 * sinB6
                                  + l2 * (270806 - 1523417 * sinB2 + 1327645 * sinB4 - 21701 * sinB6
                                          + l2 * (79690 - 866190 * sinB2 + 1730360 * sinB4 - 945460 * sinB6)))))
    return (x, y)


def convert_GPS_to_GKS(B, L, H):
    """ Convert GPS coordinates to flat cartesian (Gauss-Kruger system)
    according to ГОСТ 32453-2013.
    BLH - (radians, radians, metres);
    x,y - metres."""
    # convert geodetic GPS data to absolute cartesian system WGS-84
    (Xwgs, Ywgs, Zwgs) = geodetic_to_cartesian3D(
        B, L, H, 6378137, 1 / 298.257223563)
    # convert to ПЗ-90 system
    (Xpz, Ypz, Zpz) = WGS84_to_PZ90(Xwgs, Ywgs, Zwgs)
    # convert to referential system-1995
    (Xrs, Yrs, Zrs) = PZ90_to_SK95(Xpz, Ypz, Zpz)
    # convert to geodetic coordinates on the Krasovsky ellipsoid
    (Bkr, Lkr, Hkr) = cartesian3D_to_geodetic(
        Xrs, Yrs, Zrs, 6378245, 1 / 298.3)
    # convert to Gauss-Kruger coordinates
    (x, y) = SK95_to_GKS(Bkr, Lkr)
    return (x, y)


def test_geodetic_to_cartesian3D():
    """unit test for geodetic_to_cartesian3D
    and cartesian3D_to_geodetic."""
    B = 4 * pi / 180.0
    L = 29 * pi / 180.0
    H = 199
    (X, Y, Z) = geodetic_to_cartesian3D(B, L, H, 6378245, 1 / 298.3)
    (nB, nL, nH) = cartesian3D_to_geodetic(X, Y, Z, 6378245, 1 / 298.3)
    assert(fabs(nB - B) < 1e-2 and fabs(nL - L) < 1e-2 and fabs(nH - H) < 1e-2)
    B = -87 * pi / 180.0
    L = 295 * pi / 180.0
    H = -14
    (X, Y, Z) = geodetic_to_cartesian3D(B, L, H, 6378245, 1 / 298.3)
    (nB, nL, nH) = cartesian3D_to_geodetic(X, Y, Z, 6378245, 1 / 298.3)
    assert(fabs(nB - B) < 1e-2 and fabs(nL - L) < 1e-2 and fabs(nH - H) < 1e-2)


def test_convert_GPS_to_GKS():
    """unit test for convert_GPS_to_GKS"""
    B = 56 * pi / 180.0
    L = 37 * pi / 180.0
    H = 0
    (x1, y1) = convert_GPS_to_GKS(B, L, H)
    H = -100
    (x2, y2) = convert_GPS_to_GKS(B, L, H)
    assert fabs(x1 - x2) < 1e-2 and fabs(y1 - y2) < 1e-2
    H = 0
    # 1 second of longitude is approximately 17 metres on 56N
    L += pi / 3600.0 / 180.0
    (x3, y3) = convert_GPS_to_GKS(B, L, H)
    assert fabs(y3 - y1 - 17) < 1 and fabs(x3 - x1) < 1
    # 1 second of latitude is approximately 31 metres on 56N
    B += pi / 3600.0 / 180.0
    (x4, y4) = convert_GPS_to_GKS(B, L, H)
    assert fabs(y4 - y3) < 1 and fabs(x4 - x3 - 31) < 1

if __name__ == "__main__":
    # run tests; debug if assertion failed.
    test_geodetic_to_cartesian3D()
    test_convert_GPS_to_GKS()
