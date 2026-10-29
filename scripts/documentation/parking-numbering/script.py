# -*- coding: utf-8 -*-
"""Number parking elements in the active view with text notes.

INPUT
    IN[0] Starting number (rounded to the nearest integer; fallback 1)
    IN[1] Renumber existing labels (bool, default False: safe skip mode)

OUTPUT
    OUT[0] Numbered text-note records (created and updated)
    OUT[1] Per-element errors
    OUT[2] Parking element IDs without a bounding box / usable location
    OUT[3] Summary dictionary (counts, skipped items, settings)

Target: Revit 2025 / Dynamo 3 / CPython 3.
"""

import re
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')

from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager


# ============================================================
# DOCUMENT / ACTIVE VIEW
# ============================================================

doc = DocumentManager.Instance.CurrentDBDocument
view = doc.ActiveView

# Starting number comes from IN[0] (fallback 1)
try:
    START_NUMBER = int(round(float(IN[0])))
except Exception:
    START_NUMBER = 1

# Renumber existing mode comes from IN[1] (fallback False: safe skip mode)
try:
    RENUMBER_EXISTING = bool(IN[1])
except Exception:
    RENUMBER_EXISTING = False


# ============================================================
# CONFIGURATION
# ============================================================

# Tolerance for grouping parking spaces into the same row (Revit feet; 1.0 ft ≈ 304.8 mm)
ROW_TOLERANCE = 1.0

# True: Highest Y row → lowest Y row; False: Lowest Y row → highest Y row
ROWS_TOP_TO_BOTTOM = True

# Text size in millimeters
TEXT_SIZE_MM = 150

# Maximum distance (in Revit internal feet) to associate an existing text note
# with a parking space center (~3.5 ft ≈ 1.07 m). This strictly isolates each
# stall's label and prevents matching adjacent angled bays (spaced >= 7.5 ft).
ASSOCIATION_RADIUS_FT = 3.5


# ============================================================
# STEP 1: GET PARKING ELEMENTS VISIBLE IN THE ACTIVE VIEW
# ============================================================

collector = (
    FilteredElementCollector(doc, view.Id)
    .OfCategory(BuiltInCategory.OST_Parking)
    .WhereElementIsNotElementType()
)

parking_elements = list(collector.ToElements())


# ============================================================
# STEP 2: HELPER FUNCTIONS & GEOMETRIC CENTER
# ============================================================

def get_bbox_corners(bbox):
    """Return all eight bounding-box corners in model coordinates."""
    if bbox is None:
        return []

    transform = bbox.Transform
    corners = []

    for x in (bbox.Min.X, bbox.Max.X):
        for y in (bbox.Min.Y, bbox.Max.Y):
            for z in (bbox.Min.Z, bbox.Max.Z):
                local_point = XYZ(x, y, z)
                try:
                    corners.append(transform.OfPoint(local_point))
                except Exception:
                    corners.append(local_point)

    return corners


def _extract_geometry_points(geom_container, pts):
    """Recursively collect 3D XYZ points from a Revit GeometryElement or container."""
    if geom_container is None:
        return
    try:
        for obj in geom_container:
            if obj is None:
                continue
            if hasattr(obj, "GetSymbolGeometry"):
                sym_geom = obj.GetSymbolGeometry()
                if sym_geom is not None:
                    _extract_geometry_points(sym_geom, pts)
                else:
                    inst_geom = getattr(obj, "GetInstanceGeometry", lambda: None)()
                    if inst_geom is not None:
                        _extract_geometry_points(inst_geom, pts)
            elif hasattr(obj, "GetEndPoint"):
                pts.append(obj.GetEndPoint(0))
                pts.append(obj.GetEndPoint(1))
            elif hasattr(obj, "GetCoordinates"):
                for coord in obj.GetCoordinates():
                    pts.append(coord)
            elif hasattr(obj, "Edges"):
                for edge in obj.Edges:
                    pts.append(edge.Evaluate(0.0))
                    pts.append(edge.Evaluate(1.0))
            elif hasattr(obj, "Vertices"):
                for v in obj.Vertices:
                    pts.append(v)
    except Exception:
        pass


def get_center_from_geometry(element, active_view=None):
    """Calculate the exact physical center using local family geometry and instance transform.
    
    Extracts unrotated symbol geometry in the family's local coordinate space,
    computes the local bounding box midpoint, and maps it to model space via
    element.GetTransform(). This correctly centers stalls facing North, West,
    East, South, or diagonal angles, even when the family insertion origin
    is anchored at the curb/baseline edge.
    """
    if not hasattr(element, "GetTransform"):
        return None

    try:
        transform = element.GetTransform()
        if transform is None:
            return None

        # Build geometry options if Revit API Options is available
        geom_elem = None
        if "Options" in globals():
            options = Options()
            if active_view is not None:
                options.View = active_view
            options.ComputeReferences = False
            options.IncludeNonVisibleObjects = False
            try:
                geom_elem = element.get_Geometry(options)
            except Exception:
                geom_elem = None
            if geom_elem is None and active_view is not None:
                try:
                    options.View = None
                    geom_elem = element.get_Geometry(options)
                except Exception:
                    geom_elem = None
        else:
            try:
                geom_elem = element.get_Geometry(None)
            except Exception:
                geom_elem = None

        if geom_elem is None:
            return None

        local_pts = []
        world_pts = []

        for obj in geom_elem:
            if hasattr(obj, "GetSymbolGeometry"):
                sym = obj.GetSymbolGeometry()
                if sym is not None:
                    _extract_geometry_points(sym, local_pts)
                inst = getattr(obj, "GetInstanceGeometry", lambda: None)()
                if inst is not None:
                    _extract_geometry_points(inst, world_pts)
            else:
                _extract_geometry_points([obj], world_pts)

        # 1. Local symbol points mapped through instance transform
        if local_pts:
            min_x = min(p.X for p in local_pts)
            max_x = max(p.X for p in local_pts)
            min_y = min(p.Y for p in local_pts)
            max_y = max(p.Y for p in local_pts)
            min_z = min(p.Z for p in local_pts)
            max_z = max(p.Z for p in local_pts)
            xyz_type = globals().get("XYZ", type(local_pts[0]))
            local_center = xyz_type(
                (min_x + max_x) / 2.0,
                (min_y + max_y) / 2.0,
                (min_z + max_z) / 2.0
            )
            return transform.OfPoint(local_center)

        # 2. World points transformed into local unrotated space via inverse transform
        if world_pts:
            try:
                inv = getattr(transform, "Inverse", None)
                if inv is not None:
                    local_mapped = [inv.OfPoint(p) for p in world_pts]
                    min_x = min(p.X for p in local_mapped)
                    max_x = max(p.X for p in local_mapped)
                    min_y = min(p.Y for p in local_mapped)
                    max_y = max(p.Y for p in local_mapped)
                    min_z = min(p.Z for p in local_mapped)
                    max_z = max(p.Z for p in local_mapped)
                    xyz_type = globals().get("XYZ", type(world_pts[0]))
                    local_center = xyz_type(
                        (min_x + max_x) / 2.0,
                        (min_y + max_y) / 2.0,
                        (min_z + max_z) / 2.0
                    )
                    return transform.OfPoint(local_center)
            except Exception:
                pass

            min_x = min(p.X for p in world_pts)
            max_x = max(p.X for p in world_pts)
            min_y = min(p.Y for p in world_pts)
            max_y = max(p.Y for p in world_pts)
            min_z = min(p.Z for p in world_pts)
            max_z = max(p.Z for p in world_pts)
            xyz_type = globals().get("XYZ", type(world_pts[0]))
            return xyz_type(
                (min_x + max_x) / 2.0,
                (min_y + max_y) / 2.0,
                (min_z + max_z) / 2.0
            )

    except Exception:
        pass

    return None


def get_center_from_parameters(element):
    """Estimate stall center using FacingOrientation and length/depth parameters when geometry is unavailable."""
    try:
        loc = getattr(element, "Location", None)
        origin = getattr(loc, "Point", None)
        if origin is None:
            return None

        # Look up stall length/depth parameter
        length_val = None
        for param_name in ("Length", "Stall Length", "Parking Length", "Depth", "Stall Depth"):
            p = None
            if hasattr(element, "LookupParameter"):
                p = element.LookupParameter(param_name)
            if p is None and hasattr(element, "Symbol") and element.Symbol is not None:
                p = element.Symbol.LookupParameter(param_name)
            if p is not None and getattr(p, "HasValue", False):
                length_val = p.AsDouble()
                if length_val and length_val > 0:
                    break

        if length_val and length_val > 0:
            facing = getattr(element, "FacingOrientation", None)
            if facing is not None:
                # Family origin is at curb (baseline). Center is offset by length / 2 along FacingOrientation.
                half_len = length_val / 2.0
                xyz_type = globals().get("XYZ", type(origin))
                return xyz_type(
                    origin.X + facing.X * half_len,
                    origin.Y + facing.Y * half_len,
                    origin.Z + facing.Z * half_len
                )
    except Exception:
        pass
    return None


def get_center(element):
    """Get the geometric center of the element with safe fallbacks."""
    active_view = globals().get("view", None)

    # 1. Primary: True physical center from local unrotated symbol geometry via GetTransform()
    geom_center = get_center_from_geometry(element, active_view)
    if geom_center is not None:
        return geom_center

    # 2. Parameter-based orientation offset (FacingOrientation * Length / 2)
    param_center = get_center_from_parameters(element)
    if param_center is not None:
        return param_center

    # 3. View / model bounding box transformed to model space
    bbox = None
    if hasattr(element, "get_BoundingBox"):
        try:
            bbox = element.get_BoundingBox(active_view)
        except Exception:
            bbox = None
        if bbox is None:
            try:
                bbox = element.get_BoundingBox(None)
            except Exception:
                bbox = None

    if bbox is not None:
        corners = get_bbox_corners(bbox)
        if corners:
            center_x = sum(p.X for p in corners) / float(len(corners))
            center_y = sum(p.Y for p in corners) / float(len(corners))
            center_z = sum(p.Z for p in corners) / float(len(corners))
            xyz_type = globals().get("XYZ", type(corners[0]))
            return xyz_type(center_x, center_y, center_z)

    # 4. Fallback to LocationPoint if bounding box is unavailable
    try:
        loc = element.Location
        if hasattr(loc, "Point"):
            return loc.Point
    except Exception:
        pass

    return None


def point_distance(p1, p2):
    """Euclidean distance between two XYZ points in model coordinates."""
    dx = p1.X - p2.X
    dy = p1.Y - p2.Y
    dz = p1.Z - p2.Z
    return (dx * dx + dy * dy + dz * dz) ** 0.5


def is_numbering_text(text):
    """Return True if text appears to be a parking number annotation.
    
    Identifies numeric labels (e.g. '01', '1', '99', '100', 'P-01', '#1', 'Bay 12')
    while ignoring unrelated descriptive text (e.g. 'RESERVED', 'EV ONLY',
    'DO NOT BLOCK', 'ACCESSIBLE').
    """
    if not text:
        return False
    s = str(text).strip()
    if not s:
        return False
    if s.isdigit():
        return True
    if re.match(r'^(?:#|no\.?|p-?|bay\s*|sp-?)\s*\d+$', s, re.IGNORECASE):
        return True
    return False


# ============================================================
# STEP 3: SNAPSHOT EXISTING TEXT NOTES IN ACTIVE VIEW
# ============================================================

existing_text_notes = list(
    FilteredElementCollector(doc, view.Id)
    .OfClass(TextNote)
    .WhereElementIsNotElementType()
    .ToElements()
)

existing_number_notes = []
for existing_note in existing_text_notes:
    try:
        note_text = existing_note.Text
        if is_numbering_text(note_text):
            loc_pt = getattr(existing_note, "Coord", None)
            if loc_pt is None:
                note_bbox = existing_note.get_BoundingBox(view)
                if note_bbox is not None:
                    corners = get_bbox_corners(note_bbox)
                    if corners:
                        loc_pt = XYZ(
                            sum(p.X for p in corners) / float(len(corners)),
                            sum(p.Y for p in corners) / float(len(corners)),
                            sum(p.Z for p in corners) / float(len(corners))
                        )
            if loc_pt is not None:
                existing_number_notes.append({
                    "id": existing_note.Id.IntegerValue,
                    "element": existing_note,
                    "point": loc_pt,
                    "text": str(note_text).strip()
                })
    except Exception:
        pass


# ============================================================
# STEP 4: COLLECT PARKING CENTERS & SORT
# ============================================================

parking_data = []
no_location = []

for element in parking_elements:
    point = get_center(element)
    if point is None:
        no_location.append(element.Id.IntegerValue)
    else:
        parking_data.append({
            "element": element,
            "point": point
        })

# Sort parking by Y
parking_data.sort(
    key=lambda item: item["point"].Y,
    reverse=ROWS_TOP_TO_BOTTOM
)

# Group parking into rows
rows = []
current_row = []
row_reference_y = None

for item in parking_data:
    y = item["point"].Y
    if row_reference_y is None:
        current_row = [item]
        row_reference_y = y
    elif abs(y - row_reference_y) <= ROW_TOLERANCE:
        current_row.append(item)
    else:
        rows.append(current_row)
        current_row = [item]
        row_reference_y = y

if current_row:
    rows.append(current_row)

# Sort each row left to right (by X)
for row in rows:
    row.sort(key=lambda item: item["point"].X)

ordered_parking = []
for row in rows:
    ordered_parking.extend(row)


# ============================================================
# STEP 5: PREPARE TEXT OPTIONS & SIZE
# ============================================================

text_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.TextNoteType)
text_options = TextNoteOptions(text_type_id)
text_options.HorizontalAlignment = HorizontalTextAlignment.Center
text_options.Rotation = 0

TEXT_SIZE_FT = TEXT_SIZE_MM / 304.8


# ============================================================
# STEP 6: NUMBER PARKING SPACES
# ============================================================

created_notes = []
updated_notes = []
skipped_existing_text = []
errors = []
used_note_ids = set()
assigned_count = 0

TransactionManager.Instance.EnsureInTransaction(doc)

for item in ordered_parking:
    element = item["element"]
    point = item["point"]

    # Associate closest existing numbering note within the stall's radius
    matched_note = None
    min_dist = ASSOCIATION_RADIUS_FT
    for candidate in existing_number_notes:
        if candidate["id"] not in used_note_ids:
            d = point_distance(point, candidate["point"])
            if d < min_dist:
                min_dist = d
                matched_note = candidate

    # Safe skip mode: preserve existing note without consuming a number
    if matched_note is not None and not RENUMBER_EXISTING:
        used_note_ids.add(matched_note["id"])
        skipped_existing_text.append({
            "ParkingId": element.Id.IntegerValue,
            "ExistingTextNoteId": matched_note["id"],
            "ExistingText": matched_note["text"],
            "Reason": "existing_label_present"
        })
        continue

    # Allocate the next sequential number (never skips numbers for skipped spaces)
    number = START_NUMBER + assigned_count
    text = "{:02d}".format(number)

    if matched_note is not None and RENUMBER_EXISTING:
        # Renumbering mode: update existing note in-place
        try:
            note_elem = matched_note["element"]
            note_elem.Text = text
            try:
                note_elem.Coord = point
            except Exception:
                pass
            try:
                param = note_elem.get_Parameter(BuiltInParameter.TEXT_SIZE)
                if param is not None and not param.IsReadOnly:
                    param.Set(TEXT_SIZE_FT)
            except Exception:
                pass

            used_note_ids.add(matched_note["id"])
            updated_notes.append({
                "ParkingId": element.Id.IntegerValue,
                "Number": text,
                "TextNoteId": matched_note["id"],
                "X": point.X,
                "Y": point.Y,
                "Action": "Updated"
            })
            assigned_count += 1
        except Exception as e:
            errors.append({
                "ParkingId": element.Id.IntegerValue,
                "Number": text,
                "Error": str(e)
            })
    else:
        # Create a new text note
        try:
            note = TextNote.Create(doc, view.Id, point, text, text_options)
            try:
                param = note.get_Parameter(BuiltInParameter.TEXT_SIZE)
                if param is not None and not param.IsReadOnly:
                    param.Set(TEXT_SIZE_FT)
            except Exception:
                pass

            created_notes.append({
                "ParkingId": element.Id.IntegerValue,
                "Number": text,
                "TextNoteId": note.Id.IntegerValue,
                "X": point.X,
                "Y": point.Y,
                "Action": "Created"
            })
            assigned_count += 1
        except Exception as e:
            errors.append({
                "ParkingId": element.Id.IntegerValue,
                "Number": text,
                "Error": str(e)
            })

TransactionManager.Instance.TransactionTaskDone()


# ============================================================
# STEP 7: ASSEMBLE OUTPUT
# ============================================================

# All numbered records (created and updated)
numbered_notes = created_notes + updated_notes

summary = {
    "ParkingFound": len(parking_elements),
    "ParkingWithLocation": len(parking_data),
    "RowsDetected": len(rows),
    "TextNotesCreated": len(created_notes),
    "TextNotesUpdated": len(updated_notes),
    "TotalNumbered": len(numbered_notes),
    "SkippedExistingText": len(skipped_existing_text),
    "ExistingTextConflicts": skipped_existing_text,
    "NoLocation": len(no_location),
    "Errors": len(errors),
    "ActiveView": view.Name,
    "StartNumber": START_NUMBER,
    "RenumberExisting": RENUMBER_EXISTING
}

OUT = (
    numbered_notes,
    errors,
    no_location,
    summary
)
