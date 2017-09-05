#!/usr/bin/env python3
import math

import lxml.etree


SVG_NS = "http://www.w3.org/2000/svg"
WIDTH = 700
HEIGHT = 400
GREEN = "#43B063"
CHAIN_LINK_CIRCLE_RADIUS = 5
CHAIN_LINK_SPACING = 21
CHAIN_LINK_ANGLE = 30
CHAIN_LINK_GAP_RATIO = 1.1
FUDGE_FACTOR_RATIO = 0.9  # for making coincident arcs overlap
TOP_SPLINE_POINTS = [(271, 168), (223, 89), (107, 32), (22, 98)]
BOTTOM_SPLINE_POINTS = [(271, 168), (164, 322), (12, 214), (56, 90)]
ITERATION_COUNT = 5000


def draw_circles(parent, point):
    """
    Draws an annulus and a circle, centered at a given point.
    The path elements are appended to the given parent element.
    """
    x, y = point
    pathspec1 = (
            "M {cx} {cy} "
            "m -{r}, 0 "
            "a {r},{r} 0 1,1 {d},0 "
            "a {r},{r} 0 1,1 -{d},0 "
            "M {cx} {cy} "
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
            "M {cx} {cy} "
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

    for i in range(1, ITERATION_COUNT + 1):
        t = i / ITERATION_COUNT
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
                xform = ("translate({}, {}) rotate({})"
                         .format(point_b[0], point_b[1],
                                 angle))
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

                # Angle that marks the location of tangency between circles
                theta = math.atan2(h, r + d / 2)

                if not parity:
                    # 0 0 r fudgefactor mul theta -1 mul theta arc
                    # x-coord y-coord r ang1 ang2 arc
                    pathspec = (""
                                .format())
                    parity = True
                else:
                    parity = False

        last_point = point
    draw_circles(parent, point_a)


def chain_clipping_path(parent, spline_points):
    pass


def eye(parent):
    draw_chain(parent, TOP_SPLINE_POINTS, False)
    draw_chain(parent, BOTTOM_SPLINE_POINTS, True)


def main():
    svg = lxml.etree.Element("svg",
                             xmlns=SVG_NS,
                             width=str(WIDTH),
                             height=str(HEIGHT))
    tree = lxml.etree.ElementTree(svg)
    left_eye = lxml.etree.SubElement(svg, "g", fill=GREEN)
    eye(left_eye)
    with open("logo_gear_eyes_text.svg", "wb") as f:
        tree.write(f)

if __name__ == "__main__":
    main()
