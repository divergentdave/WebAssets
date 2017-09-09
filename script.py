#!/usr/bin/env python3
import math

import lxml.etree


SVG_NS = "http://www.w3.org/2000/svg"
WIDTH = 700
HEIGHT = 400
GREEN = "#43B063"
CHAIN_LINK_CIRCLE_RADIUS = 9
CLIP_CIRCLE_RADIUS = 9
CHAIN_LINK_SPACING = 21
CHAIN_LINK_ANGLE = math.radians(30)
CHAIN_LINK_GAP_RATIO = 1.1
FUDGE_FACTOR_RATIO = 0.9  # for making coincident arcs overlap
TOP_SPLINE_POINTS = [(271, 168), (223, 89), (107, 32), (22, 98)]
BOTTOM_SPLINE_POINTS = [(271, 168), (164, 322), (12, 214), (56, 90)]
EXTRA_CLIP_POINTS = [(20, 300), (300, 300), (300, 168)]
ITERATION_COUNT = 5000
CLIP_PATH_ID = "chain-clip"
CLIP_CIRCLE_ID = "circle-clip"
GRADIENT_ID = "gradient"
GEAR_CENTER = (158, 145)
GEAR_MAJOR_RADIUS = 70
GEAR_MINOR_RADIUS = 55


def draw_circles(parent, point):
    """
    Draws an annulus and a circle, centered at a given point.
    The path elements are appended to the given parent element.
    """
    x, y = point
    pathspec1 = (
            "M {cx:.6f} {cy:.6f} "
            "m -{r}, 0 "
            "a {r},{r} 0 1,1 {d},0 "
            "a {r},{r} 0 1,1 -{d},0 "
            "M {cx:.6f} {cy:.6f} "
            "m -{r2}, 0 "
            "a {r2},{r2} 0 1,0 {d2},0 "
            "a {r2},{r2} 0 1,0 -{d2},0"
            .format(cx=x, cy=y,
                    r=CHAIN_LINK_CIRCLE_RADIUS,
                    d=2 * CHAIN_LINK_CIRCLE_RADIUS,
                    r2=0.4 * CHAIN_LINK_CIRCLE_RADIUS,
                    d2=2 * 0.4 * CHAIN_LINK_CIRCLE_RADIUS)
    )
    lxml.etree.SubElement(parent, "path", d=pathspec1)
    pathspec2 = (
            "M {cx:.6f} {cy:.6f} "
            "m -{r}, 0 "
            "a {r},{r} 0 1,1 {d},0 "
            "a {r},{r} 0 1,1 -{d},0"
            .format(cx=x, cy=y,
                    r=0.25 * CHAIN_LINK_CIRCLE_RADIUS,
                    d=2 * 0.25 * CHAIN_LINK_CIRCLE_RADIUS)
    )
    lxml.etree.SubElement(parent, "path", d=pathspec2)


def evaluate_spline(spline_points, t):
    """
    Evaluates a cubic Bezier curve at a given parameter value.
    """
    return ((1 - t) ** 3 * spline_points[0][0] +
            3 * (1 - t) ** 2 * t * spline_points[1][0] +
            3 * (1 - t) * t ** 2 * spline_points[2][0] +
            t ** 3 * spline_points[3][0],
            (1 - t) ** 3 * spline_points[0][1] +
            3 * (1 - t) ** 2 * t * spline_points[1][1] +
            3 * (1 - t) * t ** 2 * spline_points[2][1] +
            t ** 3 * spline_points[3][1])


def draw_chain(parent, spline_points, parity):
    # Coordinates for arclength calculation
    last_point = spline_points[0]
    arclength = 0
    arclength_goal = 0

    # Coordinates for chain link endpoints
    point_a = (0, 0)
    point_b = (0, 0)

    for iterations in range(1, ITERATION_COUNT + 1):
        t = iterations / ITERATION_COUNT
        point = evaluate_spline(spline_points, t)
        delta_x = point[0] - last_point[0]
        delta_y = point[1] - last_point[1]
        arclength += math.sqrt(delta_x ** 2 + delta_y ** 2)
        if arclength >= arclength_goal:
            arclength_goal += CHAIN_LINK_SPACING
            if point_a == point_b:
                # Special case for the first circle
                point_a = point
            else:
                point_b = point_a
                point_a = point
                angle = math.degrees(math.atan2(point_b[1] - point_a[1],
                                                point_b[0] - point_a[0]))
                xform = ("translate({:.6f}, {:.6f}) rotate({:.6f})"
                         .format(point_b[0], point_b[1],
                                 angle + 180))
                translated_group = lxml.etree.SubElement(parent,
                                                         "g",
                                                         transform=xform)
                draw_circles(translated_group, (0, 0))
                
                # Distance between the outside of the two circles
                d = (math.sqrt((point_a[0] - point_b[0]) ** 2 +
                               (point_a[1] - point_b[1]) ** 2) -
                     2 * CHAIN_LINK_CIRCLE_RADIUS)

                # How much further up the cutaway circle is
                h = math.sqrt(4 * CHAIN_LINK_CIRCLE_RADIUS ** 2 -
                              (CHAIN_LINK_CIRCLE_RADIUS + d / 2) ** 2)

                if not parity:
                    # Angle that marks the location of tangency between circles
                    theta = math.atan2(h, CHAIN_LINK_CIRCLE_RADIUS + d / 2)
                    sintheta=math.sin(theta)
                    costheta=math.cos(theta)

                    r1 = CHAIN_LINK_CIRCLE_RADIUS * FUDGE_FACTOR_RATIO
                    r2 = CHAIN_LINK_CIRCLE_RADIUS
                    pathspec = ("M {x1:.6f} {y1:.6f} A {r1} {r1} 0 0 1 {x2:.6f} {y2:.6f} "
                                "L {x3:.6f} {y3:.6f} A {r2} {r2} 0 0 1 {x4:.6f} {y4:.6f} "
                                "L {x5:.6f} {y5:.6f} A {r1} {r1} 0 0 1 {x6:.6f} {y6:.6f} "
                                "L {x7:.6f} {y7:.6f} A {r2} {r2} 0 0 1 {x8:.6f} {y8:.6f} "
                                .format(r1=r1, r2=r2,
                                        x1=costheta * r1, y1=-sintheta * r1,
                                        x2=costheta * r1, y2=sintheta * r1,
                                        x3=CHAIN_LINK_CIRCLE_RADIUS + d / 2 - costheta * r2, y3=h - sintheta * r2,
                                        x4=CHAIN_LINK_CIRCLE_RADIUS + d / 2 + costheta * r2, y4=h - sintheta * r2,
                                        x5=2 * CHAIN_LINK_CIRCLE_RADIUS + d - costheta * r1, y5=sintheta * r1,
                                        x6=2 * CHAIN_LINK_CIRCLE_RADIUS + d - costheta * r1, y6=-sintheta * r1,
                                        x7=CHAIN_LINK_CIRCLE_RADIUS + d / 2 + costheta * r2, y7=-h + sintheta * r2,
                                        x8=CHAIN_LINK_CIRCLE_RADIUS + d / 2 - costheta * r2, y8=-h + sintheta * r2))
                    lxml.etree.SubElement(translated_group , "path", d=pathspec)
                    parity = True
                else:
                    r1 = CHAIN_LINK_CIRCLE_RADIUS * CHAIN_LINK_GAP_RATIO
                    sinangle = math.sin(CHAIN_LINK_ANGLE)
                    cosangle = math.cos(CHAIN_LINK_ANGLE)
                    pathspec = ("M {x1:.6f} {y1:.6f} A {r1} {r1} 0 0 1 {x2:.6f} {y2:.6f} "
                                "L {x3:.6f} {y3:.6f} A {r1} {r1} 0 0 1 {x4:.6f} {y4:.6f} "
                                .format(r1=r1,
                                        x1=cosangle * r1, y1=-sinangle * r1,
                                        x2=cosangle * r1, y2=sinangle * r1,
                                        x3=2 * CHAIN_LINK_CIRCLE_RADIUS + d - cosangle * r1, y3=sinangle * r1,
                                        x4=2 * CHAIN_LINK_CIRCLE_RADIUS + d - cosangle * r1, y4=-sinangle * r1))
                    lxml.etree.SubElement(translated_group, "path", d=pathspec)
                    parity = False

        last_point = point
    draw_circles(parent, point_a)


def matrix_multiply(m1, m2):
    return (
        (
            m1[0][0] * m2[0][0] + m1[0][1] * m2[1][0] + m1[0][2] * m2[2][0],
            m1[0][0] * m2[0][1] + m1[0][1] * m2[1][1] + m1[0][2] * m2[2][1],
            m1[0][0] * m2[0][2] + m1[0][1] * m2[1][2] + m1[0][2] * m2[2][2]
        ),
        (
            m1[1][0] * m2[0][0] + m1[1][1] * m2[1][0] + m1[1][2] * m2[2][0],
            m1[1][0] * m2[0][1] + m1[1][1] * m2[1][1] + m1[1][2] * m2[2][1],
            m1[1][0] * m2[0][2] + m1[1][1] * m2[1][2] + m1[1][2] * m2[2][2]
        ),
        (
            m1[2][0] * m2[0][0] + m1[2][1] * m2[1][0] + m1[2][2] * m2[2][0],
            m1[2][0] * m2[0][1] + m1[2][1] * m2[1][1] + m1[2][2] * m2[2][1],
            m1[2][0] * m2[0][2] + m1[2][1] * m2[1][2] + m1[2][2] * m2[2][2]
        )
    )


def apply_affine_transform(m, p):
    return (
        m[0][0] * p[0] + m[0][1] * p[1] + m[0][2],
        m[1][0] * p[0] + m[1][1] * p[1] + m[1][2],
    )


def chain_clipping_path(parent, spline_points):
    clip_path = lxml.etree.SubElement(parent, "clipPath", id=CLIP_PATH_ID)

    # Coordinates for arclength calculation
    last_point = spline_points[0]
    arclength = 0
    arclength_goal = 0

    # Coordinates for chain link endpoints
    point_a = (0, 0)
    point_b = (0, 0)

    cmd = "M"
    pathspec = ""

    i = 0
    for iterations in range(1, ITERATION_COUNT + 1):
        t = iterations / ITERATION_COUNT
        point = evaluate_spline(spline_points, t)
        delta_x = point[0] - last_point[0]
        delta_y = point[1] - last_point[1]
        arclength += math.sqrt(delta_x ** 2 + delta_y ** 2)
        if arclength >= arclength_goal:
            arclength_goal += CHAIN_LINK_SPACING
            if point_a == point_b:
                # Special case for the first circle
                point_a = point
            else:
                point_b = point_a
                point_a = point
                if i < 2:
                    i += 1
                    continue
                i += 1
                angle = math.pi + math.atan2(point_b[1] - point_a[1],
                                             point_b[0] - point_a[0])
                translate_mat = ((1, 0, point_b[0]),
                                 (0, 1, point_b[1]),
                                 (0, 0, 1))
                rotate_mat = ((math.cos(angle), -math.sin(angle), 0),
                              (math.sin(angle), math.cos(angle), 0),
                              (0, 0, 1))
                xform = matrix_multiply(translate_mat, rotate_mat)

                # Distance between the outside of the two circles
                d = (math.sqrt((point_a[0] - point_b[0]) ** 2 +
                               (point_a[1] - point_b[1]) ** 2) -
                     2 * CHAIN_LINK_CIRCLE_RADIUS)

                # How much further up the cutaway circle is
                h = math.sqrt(4 * CHAIN_LINK_CIRCLE_RADIUS ** 2 -
                              (CHAIN_LINK_CIRCLE_RADIUS + d / 2) ** 2)

                # Angle that marks the location of tangency between circles
                theta = math.atan2(h, CHAIN_LINK_CIRCLE_RADIUS + d / 2)
                sintheta=math.sin(theta)
                costheta=math.cos(theta)

                # the first and last arcs cause a small amount of overlap
                # TODO: fix by caching last transform angle
                p1 = (0, -11)
                p2 = (costheta * 11, -sintheta * 11)
                p3 = (CLIP_CIRCLE_RADIUS + d / 2 - costheta * 7, -h + sintheta * 7)
                p4 = (CLIP_CIRCLE_RADIUS + d / 2 + costheta * 7, -h + sintheta * 7)
                p5 = (2 * CLIP_CIRCLE_RADIUS + d - costheta * 11, -sintheta * 11)
                p6 = (2 * CLIP_CIRCLE_RADIUS + d, -11)
                p1t = apply_affine_transform(xform, p1)
                p2t = apply_affine_transform(xform, p2)
                p3t = apply_affine_transform(xform, p3)
                p4t = apply_affine_transform(xform, p4)
                p5t = apply_affine_transform(xform, p5)
                p6t = apply_affine_transform(xform, p6)
                pathspec += ("{cmd} {x1:.6f} {y1:.6f} A {r1} {r1} 0 0 1 {x2:.6f} {y2:.6f} "
                             "L {x3:.6f} {y3:.6f} A {r2} {r2} 0 0 0 {x4:.6f} {y4:.6f} "
                             "L {x5:.6f} {y5:.6f} A {r1} {r1} 0 0 1 {x6:.6f} {y6:.6f} "
                             .format(
                                 cmd=cmd,
                                 r1=11,
                                 r2=7,
                                 x1=p1t[0], y1=p1t[1],
                                 x2=p2t[0], y2=p2t[1],
                                 x3=p3t[0], y3=p3t[1],
                                 x4=p4t[0], y4=p4t[1],
                                 x5=p5t[0], y5=p5t[1],
                                 x6=p6t[0], y6=p6t[1],
                ))
                if cmd == "M":
                    cmd = "L"
        last_point = point
    for p in EXTRA_CLIP_POINTS:
        pathspec += "L {} {} ".format(*p)
    lxml.etree.SubElement(clip_path, "path", d=pathspec)


def draw_gear(parent):
    pathspec = ""
    cmd = "M"
    for degrees in range(0, 360, 30):
        alpha = math.radians(degrees + 10)
        beta = math.radians(degrees + 25)
        gamma = math.radians(degrees + 40)
        pathspec += ("{cmd} {x1} {y1} A {r} {r} 0 0 1 {x2} {y2} "
                     "L {x3} {y3} A {R} {R} 0 0 1 {x4} {y4} "
                     .format(cmd=cmd,
                             r=GEAR_MINOR_RADIUS,
                             R=GEAR_MAJOR_RADIUS,
                             x1=GEAR_CENTER[0] + GEAR_MINOR_RADIUS * math.cos(alpha),
                             y1=GEAR_CENTER[1] + GEAR_MINOR_RADIUS * math.sin(alpha),
                             x2=GEAR_CENTER[0] + GEAR_MINOR_RADIUS * math.cos(beta),
                             y2=GEAR_CENTER[1] + GEAR_MINOR_RADIUS * math.sin(beta),
                             x3=GEAR_CENTER[0] + GEAR_MAJOR_RADIUS * math.cos(beta),
                             y3=GEAR_CENTER[1] + GEAR_MAJOR_RADIUS * math.sin(beta),
                             x4=GEAR_CENTER[0] + GEAR_MAJOR_RADIUS * math.cos(gamma),
                             y4=GEAR_CENTER[1] + GEAR_MAJOR_RADIUS * math.sin(gamma)
                             ))
        cmd = "L"
    pathspec += "Z"
    gear = lxml.etree.SubElement(parent, "path", d=pathspec, fill=GREEN)
    gear.set("clip-path", "url(#{})".format(CLIP_PATH_ID))

def draw_circle(parent, center, radius, **kwargs):
    pathspec = (
            "M {cx:.6f} {cy:.6f} "
            "m -{r}, 0 "
            "a {r},{r} 0 1,1 {d},0 "
            "a {r},{r} 0 1,1 -{d},0"
            .format(cx=center[0], cy=center[1],
                    r=radius,
                    d=2 * radius)
    )
    lxml.etree.SubElement(parent, "path", d=pathspec, **kwargs)


def main():
    svg = lxml.etree.Element("svg",
                             xmlns=SVG_NS,
                             width=str(WIDTH),
                             height=str(HEIGHT))
    tree = lxml.etree.ElementTree(svg)

    defs = lxml.etree.SubElement(svg, "defs")
    tan30 = math.tan(math.radians(30))
    gradient = lxml.etree.SubElement(defs, "linearGradient", id=GRADIENT_ID,
            x1=str((1 - tan30) / 2),
            y1="0",
            x2=str((1 + tan30) / 2),
            y2="1")
    lxml.etree.SubElement(gradient, "stop", offset="0%").set("stop-color", GREEN)
    lxml.etree.SubElement(gradient, "stop", offset="100%").set("stop-color", "white")

    chain_clipping_path(defs, TOP_SPLINE_POINTS)

    eye_top = lxml.etree.SubElement(svg, "g", fill=GREEN)
    draw_chain(eye_top, TOP_SPLINE_POINTS, False)
    eye_bottom = lxml.etree.SubElement(svg, "g", fill=GREEN)
    eye_bottom.set("clip-path", "url(#{})".format(CLIP_PATH_ID))
    draw_chain(eye_bottom, BOTTOM_SPLINE_POINTS, True)

    draw_gear(svg)
    draw_circle(svg, GEAR_CENTER, 40, fill="url(#{})".format(GRADIENT_ID))
    draw_circle(svg, GEAR_CENTER, 10, fill=GREEN)

    with open("logo_gear_eyes_text.svg", "wb") as f:
        tree.write(f)

def test():
    a = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
    b = ((8, 4, 2), (5, 7, 3), (1, 9, 6))
    ab = ((21, 45, 26), (63, 105, 59), (105, 165, 92))
    assert matrix_multiply(a, b) == ab
    v = (7, 11)
    av = (32, 89)
    assert apply_affine_transform(a, v) == av

if __name__ == "__main__":
    test()
    main()
