# -*- coding: utf-8 -*-
# CAR RAMP GENERATOR - Revit 2025 / Dynamo CPython3
# Egyptian Garage Code reference: uploaded Egyptian garage code draft (2023).
# Creates sloped ramp Floors + raised curb Floors, then groups all created elements.
#
# INPUTS
# IN[0]  Level A (Revit Level)
# IN[1]  Level B (Revit Level) - order does not matter
# IN[2]  Main slope percent (default 15; max 15)
# IN[3]  CLEAR lane width in mm (default 3000 per lane)
# IN[4]  Start X mm (top/high end, left corner)
# IN[5]  Start Y mm
# IN[6]  Direction angle degrees (0 = down along +X, 90 = down along +Y)
# IN[7]  Ramp/drive Floor Type element OR exact Floor Type name (optional; first type if empty)
# IN[8]  Traffic type: 'one-way' or 'two-way' (default 'one-way')
# IN[9]  Curb Floor Type element OR exact Floor Type name (optional; seeks ~150mm type)
# IN[10] Side curb width mm (default 500)
# IN[11] Center curb width mm (default 300; only for two-way)
# IN[12] Side curb height mm (default 150; code draft says curb height max 150mm)
# IN[13] Center curb height mm (default 100; code draft says center divider max 100mm)
# IN[14] Vehicle class: 'standard', 'service', or 'waste' (service/waste clear lane = 4000mm)
# IN[15] Required overhead clear height mm (default 2200; reported as design clearance target)
#
# NOTES
# - Total ramp width is calculated automatically:
#   one-way = clear lane + 2 side curbs
#   two-way = 2 clear lanes + 2 side curbs + center curb
# - Curb floors are modeled as narrow sloped Floor strips whose TOP surface is raised
#   above the driving surface by the configured curb height. The selected curb Floor Type
#   should have a compound-structure thickness close to that height (e.g. 150mm side curb).
# - The 2023 code PDF text/table appears to show a 500mm central divider in the ramp table,
#   while this script defaults to the requested 300mm. Confirm this design choice with the
#   responsible designer/authority before using for compliance.
# - For main slope > 10%, two 3000mm transitions at half the main slope are generated.
# - OUT = [group, report_lines, [bottom_left_X_mm, bottom_left_Y_mm]]

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')

from Autodesk.Revit.DB import (
    XYZ, Line, CurveLoop, Floor, FloorType, Level, Options, PlanarFace,
    ElementId, ElementTransformUtils, FilteredElementCollector, SubTransaction
)
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from System.Collections.Generic import List
import math


doc = DocumentManager.Instance.CurrentDBDocument
FT = 1.0 / 304.8  # mm to feet
TRANS_LEN_MM = 3000.0


def get_in(i, default):
    try:
        v = IN[i]
        return default if v is None else v
    except Exception:
        return default


def norm_text(value):
    try:
        return str(value).strip().lower().replace('_', '-').replace(' ', '-')
    except Exception:
        return ''


def resolve_floor_type(value, all_types, fallback=None):
    """Accept a FloorType element or an exact type name string."""
    if value is not None:
        try:
            el = UnwrapElement(value)
            if el is not None and isinstance(el, FloorType):
                return el
        except Exception:
            pass
        try:
            wanted = str(value).strip().lower()
            if wanted:
                for ft in all_types:
                    try:
                        if ft.Name.strip().lower() == wanted:
                            return ft
                    except Exception:
                        pass
        except Exception:
            pass
    return fallback


def type_thickness_mm(ftype):
    try:
        cs = ftype.GetCompoundStructure()
        if cs is not None:
            return cs.GetWidth() / FT
    except Exception:
        pass
    return None


# ---------- resolve levels from selected Level elements OR exact level names ----------
all_levels = list(FilteredElementCollector(doc).OfClass(Level))

def resolve_level(value, index):
    candidate = None
    try:
        candidate = UnwrapElement(value)
    except Exception:
        candidate = value
    if candidate is not None and isinstance(candidate, Level):
        return candidate
    wanted = '' if value is None else str(value).strip().lower()
    if wanted:
        for level in all_levels:
            try:
                if level.Name.strip().lower() == wanted:
                    return level
            except Exception:
                pass
    names = ', '.join(sorted([str(l.Name) for l in all_levels]))
    raise ValueError('IN[%d]: enter an exact Level name from this project. Available Levels: %s' % (index, names))

lv_a = resolve_level(get_in(0, None), 0)
lv_b = resolve_level(get_in(1, None), 1)

if lv_a.Elevation >= lv_b.Elevation:
    lv_top, lv_bot = lv_a, lv_b
else:
    lv_top, lv_bot = lv_b, lv_a

Z_TOP = lv_top.Elevation / FT  # mm
Z_BOT = lv_bot.Elevation / FT  # mm
DROP = Z_TOP - Z_BOT
if DROP <= 0:
    raise ValueError('The two levels have the same elevation.')

SLOPE = float(get_in(2, 15.0))
CLEAR_LANE = float(get_in(3, 3000.0))
OX = float(get_in(4, 0.0))
OY = float(get_in(5, 0.0))
ANG = math.radians(float(get_in(6, 0.0)))
DX, DY = math.cos(ANG), math.sin(ANG)
TRAFFIC = norm_text(get_in(8, 'one-way'))
SIDE_CURB_W = float(get_in(10, 500.0))
CENTER_CURB_W = float(get_in(11, 300.0))
SIDE_CURB_H = float(get_in(12, 150.0))
CENTER_CURB_H = float(get_in(13, 100.0))
VEHICLE_CLASS = norm_text(get_in(14, 'standard'))
OVERHEAD_CLEAR_MM = float(get_in(15, 2200.0))

# Service and waste vehicles require a 4000mm clear lane by requested project rule.
if VEHICLE_CLASS in ('service', 'service-vehicle', 'waste', 'waste-vehicle', 'garbage', 'garbage-truck', 'refuse'):
    CLEAR_LANE = 4000.0
elif VEHICLE_CLASS not in ('standard', 'car', 'passenger-car', 'normal', 'none', ''):
    raise ValueError("IN[14] must be 'standard', 'service', or 'waste'.")

if SLOPE <= 0 or SLOPE > 15.0:
    raise ValueError('Main slope must be greater than 0% and no more than 15%.')
if CLEAR_LANE <= 0:
    raise ValueError('Clear lane width must be positive.')
if SIDE_CURB_W < 0 or CENTER_CURB_W < 0:
    raise ValueError('Curb widths cannot be negative.')
if SIDE_CURB_H <= 0 or CENTER_CURB_H <= 0:
    raise ValueError('Curb heights must be positive.')
if OVERHEAD_CLEAR_MM <= 0:
    raise ValueError('Overhead clear height must be positive.')
if TRAFFIC in ('oneway', 'one-way', '1-way', 'single'):
    TRAFFIC = 'one-way'
elif TRAFFIC in ('twoway', 'two-way', '2-way', 'double'):
    TRAFFIC = 'two-way'
else:
    raise ValueError("IN[8] must be 'one-way' or 'two-way'.")

if TRAFFIC == 'one-way':
    TOTAL_WIDTH = CLEAR_LANE + 2.0 * SIDE_CURB_W
else:
    TOTAL_WIDTH = 2.0 * CLEAR_LANE + 2.0 * SIDE_CURB_W + CENTER_CURB_W

all_levels = list(FilteredElementCollector(doc).OfClass(Level))
all_floor_types = list(FilteredElementCollector(doc).OfClass(FloorType))
if not all_floor_types:
    raise ValueError('No Floor Types were found in this project.')


def nearest_level(z_ft):
    return min(all_levels, key=lambda l: abs(l.Elevation - z_ft))


def P(x, y, z_ft):
    """Local x along ramp and y across ramp, coordinates in mm; z_ft in Revit feet."""
    gx = OX + x * DX - y * DY
    gy = OY + x * DY + y * DX
    return XYZ(gx * FT, gy * FT, z_ft)


ramp_type = resolve_floor_type(get_in(7, None), all_floor_types, all_floor_types[0])
if ramp_type is None:
    ramp_type = all_floor_types[0]

curb_type_input = get_in(9, None)
curb_type = resolve_floor_type(curb_type_input, all_floor_types, None)
if curb_type is None:
    # If not supplied, prefer a type whose compound thickness is closest to 150mm.
    candidates = []
    for ft in all_floor_types:
        th = type_thickness_mm(ft)
        if th is not None:
            candidates.append((abs(th - SIDE_CURB_H), ft))
    curb_type = sorted(candidates, key=lambda item: item[0])[0][1] if candidates else ramp_type


# ---------- segment calculation ----------
def make_segments(drop_mm):
    if SLOPE > 10.0:
        trans_slope = SLOPE / 2.0
        trans_drop = TRANS_LEN_MM * trans_slope / 100.0
        main_drop = drop_mm - 2.0 * trans_drop
        if main_drop <= 0:
            raise ValueError(
                'Height difference %.0fmm is too small for two 3000mm transitions at %.2f%%.'
                % (drop_mm, trans_slope)
            )
        main_len = main_drop / (SLOPE / 100.0)
        return [
            (TRANS_LEN_MM, trans_slope, 'top transition'),
            (main_len, SLOPE, 'main ramp'),
            (TRANS_LEN_MM, trans_slope, 'bottom transition')
        ]
    return [(drop_mm / (SLOPE / 100.0), SLOPE, 'main ramp')]


def top_face_normal(fl):
    best = None
    try:
        for g in fl.get_Geometry(Options()):
            if not hasattr(g, 'Faces'):
                continue
            for face in g.Faces:
                if isinstance(face, PlanarFace) and face.FaceNormal.Z > 0.5:
                    if best is None or face.FaceNormal.Z > best.Z:
                        best = face.FaceNormal
    except Exception:
        pass
    return best


def build_sloped_floor(xa, xb, y0, y1, z_high_mm, slope_pct, ftype, label, report):
    """Create one sloped floor strip. High end is xa; ramp falls toward +x."""
    length = xb - xa
    if length <= 0 or y1 <= y0:
        raise ValueError('Invalid geometry for %s.' % label)

    z_low_mm = z_high_mm - length * slope_pct / 100.0
    ref_level = nearest_level(z_low_mm * FT)
    z_profile = ref_level.Elevation
    pts = [(xa, y0), (xb, y0), (xb, y1), (xa, y1)]
    loop = CurveLoop()
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        loop.Append(Line.CreateBound(P(a[0], a[1], z_profile), P(b[0], b[1], z_profile)))
    loops = List[CurveLoop]()
    loops.Add(loop)

    ymid = (y0 + y1) / 2.0
    # Arrow points from low end to high end, so the floor rises along the arrow.
    arrow = Line.CreateBound(P(xb, ymid, z_profile), P(xa, ymid, z_profile))
    fl = Floor.Create(doc, loops, ftype.Id, ref_level.Id, False, arrow, slope_pct / 100.0)
    doc.Regenerate()

    n = top_face_normal(fl)
    if n is None:
        raise Exception('%s: could not find a valid upward planar face to verify slope.' % label)
    along = n.X * DX + n.Y * DY
    if along <= 1e-9:
        doc.Delete(fl.Id)
        arrow_rev = Line.CreateBound(P(xa, ymid, z_profile), P(xb, ymid, z_profile))
        fl = Floor.Create(doc, loops, ftype.Id, ref_level.Id, False, arrow_rev, slope_pct / 100.0)
        doc.Regenerate()
        n = top_face_normal(fl)
        if n is None or (n.X * DX + n.Y * DY) <= 1e-9:
            raise Exception('%s: slope direction remains incorrect after rebuilding.' % label)

    # Align the upper end of the TOP face to the target elevation.
    bb = fl.get_BoundingBox(None)
    if bb is None:
        raise Exception('%s: no bounding box returned by Revit.' % label)
    dz = z_high_mm * FT - bb.Max.Z
    if abs(dz) > 1e-7:
        ElementTransformUtils.MoveElement(doc, fl.Id, XYZ(0, 0, dz))
        doc.Regenerate()

    n = top_face_normal(fl)
    if n is None or n.Z <= 0:
        raise Exception('%s: invalid top-face normal after elevation correction.' % label)
    measured = math.hypot(n.X, n.Y) / n.Z * 100.0
    along = n.X * DX + n.Y * DY
    if along <= 0:
        raise Exception('%s: floor slopes in the wrong direction.' % label)
    if abs(measured - slope_pct) > 0.25:
        raise Exception('%s: measured slope %.3f%% differs from target %.3f%%.' %
                        (label, measured, slope_pct))

    bb = fl.get_BoundingBox(None)
    report.append(
        '%s | width %.0fmm | length %.0fmm | slope target %.2f%% / measured %.2f%% | '
        'high-end target %.0fmm / bbox max %.0fmm'
        % (label, y1 - y0, length, slope_pct, measured, z_high_mm, bb.Max.Z / FT)
    )
    return fl


# ---------- create all ramp and curb floors inside a rollback-capable subtransaction ----------
report = []
created_ids = List[ElementId]()
subtx = None
TransactionManager.Instance.EnsureInTransaction(doc)
try:
    subtx = SubTransaction(doc)
    subtx.Start()

    segs = make_segments(DROP)
    x = 0.0
    z_high = Z_TOP
    curb_side_positions = [(0.0, SIDE_CURB_W),
                           (TOTAL_WIDTH - SIDE_CURB_W, TOTAL_WIDTH)]
    center_position = ((TOTAL_WIDTH - CENTER_CURB_W) / 2.0,
                       (TOTAL_WIDTH + CENTER_CURB_W) / 2.0)

    ramp_floors = []
    curb_floors = []
    for i, (length, slope, seg_label) in enumerate(segs):
        xa, xb = x, x + length
        fl = build_sloped_floor(
            xa, xb, 0.0, TOTAL_WIDTH, z_high, slope, ramp_type,
            'Ramp %d (%s)' % (i + 1, seg_label), report
        )
        ramp_floors.append(fl)
        created_ids.Add(fl.Id)

        # Curb top surfaces are raised above the driving surface.
        for side_i, (y0, y1) in enumerate(curb_side_positions):
            side_fl = build_sloped_floor(
                xa, xb, y0, y1, z_high + SIDE_CURB_H, slope, curb_type,
                'Side curb %d / segment %d' % (side_i + 1, i + 1), report
            )
            curb_floors.append(side_fl)
            created_ids.Add(side_fl.Id)

        if TRAFFIC == 'two-way' and CENTER_CURB_W > 0:
            center_fl = build_sloped_floor(
                xa, xb, center_position[0], center_position[1],
                z_high + CENTER_CURB_H, slope, curb_type,
                'Center divider / segment %d' % (i + 1), report
            )
            curb_floors.append(center_fl)
            created_ids.Add(center_fl.Id)

        x = xb
        z_high -= length * slope / 100.0

    # Group the ramp deck and all curb strips together.
    group_name = 'Car Ramp %s to %s (%s)' % (lv_top.Name, lv_bot.Name, TRAFFIC)
    grp = doc.Create.NewGroup(created_ids)
    try:
        grp.GroupType.Name = group_name
    except Exception:
        report.append('Group created; Revit did not accept the requested Group Type name (possibly duplicate).')

    ramp_th = type_thickness_mm(ramp_type)
    curb_th = type_thickness_mm(curb_type)
    report.insert(0,
        '%s | drop %.0fmm | total length %.2fm | traffic %s | '
        'vehicle %s | clear lane %.0fmm | total width %.0fmm | overhead clearance target %.0fmm | ramp type "%s" | curb type "%s"'
        % (group_name, DROP, x / 1000.0, TRAFFIC, VEHICLE_CLASS, CLEAR_LANE, TOTAL_WIDTH,
           OVERHEAD_CLEAR_MM, ramp_type.Name, curb_type.Name)
    )
    report.append('Ramp Floor Type thickness: %s mm.' % ('unknown' if ramp_th is None else '%.0f' % ramp_th))
    report.append('Curb Floor Type thickness: %s mm. Check that it matches the intended curb build-up.' %
                  ('unknown' if curb_th is None else '%.0f' % curb_th))
    report.append('OVERHEAD CLEARANCE TARGET: %.0fmm (verify actual underside of beams/ducts/doors in a section; this script reports the target and does not create a physical overhead element).' % OVERHEAD_CLEAR_MM)
    if OVERHEAD_CLEAR_MM < 2200.0:
        report.append('WARNING: overhead clearance target is below 2200mm; verify applicable code and vehicle envelope.')
    if VEHICLE_CLASS in ('service', 'service-vehicle', 'waste', 'waste-vehicle', 'garbage', 'garbage-truck', 'refuse'):
        report.append('Service/waste vehicle selected: clear lane automatically set to 4000mm.')
    if curb_type_input is None:
        report.append('Curb type was selected automatically; provide IN[9] with an exact type name or Floor Type for explicit control.')
    if TRAFFIC == 'two-way':
        report.append('Center divider: width %.0fmm, height %.0fmm. Code draft table appears to indicate 500mm width and <=100mm height; confirm requested 300mm width.' %
                      (CENTER_CURB_W, CENTER_CURB_H))

    subtx.Commit()
except Exception as ex:
    try:
        if subtx is not None and subtx.GetStatus().ToString() == 'Started':
            subtx.RollBack()
    except Exception:
        pass
    raise Exception('Ramp creation failed; created elements were rolled back. Details: %s' % ex)
finally:
    TransactionManager.Instance.TransactionTaskDone()

end_pt = P(x, 0.0, 0.0)
OUT = [grp, report, [end_pt.X / FT, end_pt.Y / FT]]
