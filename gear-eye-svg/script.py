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
GRADIENT_LEFT_ID = "gradient-left"
GRADIENT_RIGHT_ID = "gradient-right"
GEAR_CENTER = (158, 145)
GEAR_MAJOR_RADIUS = 70
GEAR_MINOR_RADIUS = 55

TEXT_PATHS = [
    [(14, 305), (49, 305), (43, 311), (32, 311), (32, 356), (26, 356),
     (26, 311), (8, 311)],
    [(55, 305), (61, 308), (61, 328), (84, 328), (84, 305), (90, 308),
     (90, 356), (84, 356), (84, 334), (61, 334), (61, 356), (55, 356)],
    [(98, 305), (132, 305), (126, 311), (104, 311), (104, 328), (129, 328),
     (123, 334), (104, 334), (104, 350), (132, 350), (126, 356), (98, 356)],
    [(162, 305), (193, 305), (187, 311), (161, 311), (161, 350), (187, 350),
     (187, 334), (170, 334), (176, 328), (193, 328), (193, 350), (187, 356),
     (162, 356), (155, 349), (155, 312)],
    [(201, 305), (233, 305), (239, 311), (239, 326), (234, 330), (239, 334),
     (239, 356), (233, 356), (233, 334), (207, 334), (207, 328), (233, 328),
     (233, 311), (207, 311), (207, 356), (201, 356)],
    [(246, 305), (280, 305), (274, 311), (252, 311), (252, 328), (277, 328),
     (271, 334), (252, 334), (252, 350), (280, 350), (274, 356), (246, 356)],
    [(283, 305), (317, 305), (311, 311), (289, 311), (289, 328), (314, 328),
     (308, 334), (289, 334), (289, 350), (317, 350), (311, 356), (283, 356)],
    [(324, 308), (331, 305), (356, 344), (356, 308), (362, 305), (362, 356),
     (357, 356), (332, 317), (330, 317), (330, 356), (324, 356)],
    [(391, 310), (397, 306), (415, 341), (416, 341), (434, 305), (441, 309),
     (441, 356), (435, 356), (435, 317), (419, 349), (413, 349), (397, 316),
     (397, 356), (391, 356)],
    [(452, 312), (459, 305), (484, 305), (490, 311), (490, 356), (484, 356),
     (490, 311), (490, 356), (484, 356), (484, 337), (458, 337), (458, 331),
     (484, 331), (484, 311), (458, 311), (458, 356), (452, 356)],
    [(496, 311), (502, 305), (527, 305), (533, 311), (502, 311), (502, 350),
     (534, 350), (528, 356), (502, 356), (496, 350)],
    [(540, 305), (546, 308), (546, 328), (569, 328), (569, 305), (575, 308),
     (575, 356), (569, 356), (569, 334), (546, 334), (546, 356), (540, 356)],
    [(588, 305), (594, 305), (594, 356), (588, 356)],
    [(606, 308), (613, 305), (638, 344), (638, 308), (644, 305), (644, 356),
     (639, 356), (614, 317), (612, 317), (612, 356), (606, 356)],
    [(651, 305), (685, 305), (679, 311), (657, 311), (657, 328), (682, 328),
     (676, 334), (657, 334), (657, 350), (685, 350), (679, 356), (651, 356)],
]


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
                    sintheta = math.sin(theta)
                    costheta = math.cos(theta)

                    r1 = CHAIN_LINK_CIRCLE_RADIUS * FUDGE_FACTOR_RATIO
                    r2 = CHAIN_LINK_CIRCLE_RADIUS
                    pathspec = (
                        "M {x1:.6f} {y1:.6f} "
                        "A {r1} {r1} 0 0 1 {x2:.6f} {y2:.6f} "
                        "L {x3:.6f} {y3:.6f} "
                        "A {r2} {r2} 0 0 1 {x4:.6f} {y4:.6f} "
                        "L {x5:.6f} {y5:.6f} "
                        "A {r1} {r1} 0 0 1 {x6:.6f} {y6:.6f} "
                        "L {x7:.6f} {y7:.6f} "
                        "A {r2} {r2} 0 0 1 {x8:.6f} {y8:.6f} "
                        .format(
                            r1=r1,
                            r2=r2,
                            x1=costheta * r1,
                            y1=-sintheta * r1,
                            x2=costheta * r1,
                            y2=sintheta * r1,
                            x3=(CHAIN_LINK_CIRCLE_RADIUS + d / 2
                                - costheta * r2),
                            y3=h - sintheta * r2,
                            x4=(CHAIN_LINK_CIRCLE_RADIUS + d / 2
                                + costheta * r2),
                            y4=h - sintheta * r2,
                            x5=(2 * CHAIN_LINK_CIRCLE_RADIUS + d
                                - costheta * r1),
                            y5=sintheta * r1,
                            x6=(2 * CHAIN_LINK_CIRCLE_RADIUS + d
                                - costheta * r1),
                            y6=-sintheta * r1,
                            x7=(CHAIN_LINK_CIRCLE_RADIUS + d / 2
                                + costheta * r2),
                            y7=-h + sintheta * r2,
                            x8=(CHAIN_LINK_CIRCLE_RADIUS + d / 2
                                - costheta * r2),
                            y8=-h + sintheta * r2
                        )
                    )
                    lxml.etree.SubElement(translated_group, "path",
                                          d=pathspec)
                    parity = True
                else:
                    r1 = CHAIN_LINK_CIRCLE_RADIUS * CHAIN_LINK_GAP_RATIO
                    sinangle = math.sin(CHAIN_LINK_ANGLE)
                    cosangle = math.cos(CHAIN_LINK_ANGLE)
                    pathspec = (
                        "M {x1:.6f} {y1:.6f} "
                        "A {r1} {r1} 0 0 1 {x2:.6f} {y2:.6f} "
                        "L {x3:.6f} {y3:.6f} "
                        "A {r1} {r1} 0 0 1 {x4:.6f} {y4:.6f} "
                        .format(
                            r1=r1,
                            x1=cosangle * r1,
                            y1=-sinangle * r1,
                            x2=cosangle * r1,
                            y2=sinangle * r1,
                            x3=(2 * CHAIN_LINK_CIRCLE_RADIUS + d
                                - cosangle * r1),
                            y3=sinangle * r1,
                            x4=(2 * CHAIN_LINK_CIRCLE_RADIUS + d
                                - cosangle * r1),
                            y4=-sinangle * r1
                        )
                    )
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
                sintheta = math.sin(theta)
                costheta = math.cos(theta)

                # the first and last arcs cause a small amount of overlap
                # TODO: fix by caching last transform angle
                p1 = (0, -11)
                p2 = (costheta * 11, -sintheta * 11)
                p3 = (CLIP_CIRCLE_RADIUS + d / 2 - costheta * 7,
                      -h + sintheta * 7)
                p4 = (CLIP_CIRCLE_RADIUS + d / 2 + costheta * 7,
                      -h + sintheta * 7)
                p5 = (2 * CLIP_CIRCLE_RADIUS + d - costheta * 11,
                      -sintheta * 11)
                p6 = (2 * CLIP_CIRCLE_RADIUS + d, -11)
                p1t = apply_affine_transform(xform, p1)
                p2t = apply_affine_transform(xform, p2)
                p3t = apply_affine_transform(xform, p3)
                p4t = apply_affine_transform(xform, p4)
                p5t = apply_affine_transform(xform, p5)
                p6t = apply_affine_transform(xform, p6)
                pathspec += (
                    "{cmd} {x1:.6f} {y1:.6f} "
                    "A {r1} {r1} 0 0 1 {x2:.6f} {y2:.6f} "
                    "L {x3:.6f} {y3:.6f} "
                    "A {r2} {r2} 0 0 0 {x4:.6f} {y4:.6f} "
                    "L {x5:.6f} {y5:.6f} "
                    "A {r1} {r1} 0 0 1 {x6:.6f} {y6:.6f} "
                    .format(
                        cmd=cmd,
                        r1=11,
                        r2=7,
                        x1=p1t[0], y1=p1t[1],
                        x2=p2t[0], y2=p2t[1],
                        x3=p3t[0], y3=p3t[1],
                        x4=p4t[0], y4=p4t[1],
                        x5=p5t[0], y5=p5t[1],
                        x6=p6t[0], y6=p6t[1]
                    )
                )
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
        pathspec += (
            "{cmd} {x1:.6f} {y1:.6f} A {r} {r} 0 0 1 {x2:.6f} {y2:.6f} "
            "L {x3:.6f} {y3:.6f} A {R} {R} 0 0 1 {x4:.6f} {y4:.6f} "
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


def draw_eye(parent, gradient_id):
    eye_top = lxml.etree.SubElement(parent, "g", fill=GREEN)
    draw_chain(eye_top, TOP_SPLINE_POINTS, False)
    eye_bottom = lxml.etree.SubElement(parent, "g", fill=GREEN)
    eye_bottom.set("clip-path", "url(#{})".format(CLIP_PATH_ID))
    draw_chain(eye_bottom, BOTTOM_SPLINE_POINTS, True)

    draw_gear(parent)
    draw_circle(parent, GEAR_CENTER, 40, fill="url(#{})".format(gradient_id))
    draw_circle(parent, GEAR_CENTER, 10, fill=GREEN)


def draw_text(parent, paths):
    for path in paths:
        pathspec = ("M {} {} L ".format(*path[0]) +
                    " L ".join("{} {}".format(*point)
                               for point in path[1:]))
        lxml.etree.SubElement(parent, "path", d=pathspec)


def main():
    svg = lxml.etree.Element("svg",
                             xmlns=SVG_NS,
                             width=str(WIDTH),
                             height=str(HEIGHT))
    tree = lxml.etree.ElementTree(svg)

    defs = lxml.etree.SubElement(svg, "defs")
    cos30 = math.cos(math.radians(30))
    sin30 = math.sin(math.radians(30))
    gradient_left = lxml.etree.SubElement(
        defs, "linearGradient", id=GRADIENT_LEFT_ID,
        x1="{:.6f}".format((1 - sin30) / 2),
        y1="{:.6f}".format((1 - cos30) / 2),
        x2="{:.6f}".format((1 + sin30) / 2),
        y2="{:.6f}".format((1 + cos30) / 2)
    )
    lxml.etree.SubElement(gradient_left, "stop", offset="0%") \
        .set("stop-color", GREEN)
    lxml.etree.SubElement(gradient_left, "stop", offset="100%") \
        .set("stop-color", "white")
    gradient_right = lxml.etree.SubElement(
        defs, "linearGradient", id=GRADIENT_RIGHT_ID,
        x1="{:.6f}".format((1 + sin30) / 2),
        y1="{:.6f}".format((1 - cos30) / 2),
        x2="{:.6f}".format((1 - sin30) / 2),
        y2="{:.6f}".format((1 + cos30) / 2)
    )
    lxml.etree.SubElement(gradient_right, "stop", offset="0%") \
        .set("stop-color", GREEN)
    lxml.etree.SubElement(gradient_right, "stop", offset="100%") \
        .set("stop-color", "white")

    chain_clipping_path(defs, TOP_SPLINE_POINTS)

    left_eye = lxml.etree.SubElement(svg, "g")
    right_eye = lxml.etree.SubElement(svg, "g",
                                      transform="translate(700 0) scale(-1 1)")
    draw_eye(left_eye, GRADIENT_LEFT_ID)
    draw_eye(right_eye, GRADIENT_RIGHT_ID)

    text = lxml.etree.SubElement(svg, "g", fill=GREEN)
    draw_text(text, TEXT_PATHS)

    with open("logo_gear_eyes_text.svg", "wb") as f:
        tree.write(f, xml_declaration=True, encoding="utf-8")


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
