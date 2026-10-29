# -*- coding: utf-8 -*-
"""Number parking elements in the active view with text notes.

INPUT
    IN[0] Starting number (rounded to the nearest integer; fallback 1)

OUTPUT
    OUT[0] Created text-note records
    OUT[1] Per-element errors
    OUT[2] Parking element IDs without a bounding box
    OUT[3] Summary dictionary, including spaces skipped because existing text
         overlaps the parking bounding box

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

# Starting number comes from the Dynamo Number node (IN[0]).
try:
    START_NUMBER = int(round(float(IN[0])))
except Exception:
    START_NUMBER = 1


# ============================================================
# CONFIGURATION
# ============================================================

# START_NUMBER is provided by IN[0].

# Tolerance for grouping parking spaces into the same row.
# Revit internal units = feet.
#
# 1.0 ft ≈ 304.8 mm
#
# Increase this if one physical row is being split into
# multiple rows.
ROW_TOLERANCE = 1.0

# True:
#   Highest Y row → lowest Y row
#
# False:
#   Lowest Y row → highest Y row
ROWS_TOP_TO_BOTTOM = True

# Text size in millimeters
TEXT_SIZE_MM = 150


# ============================================================
# STEP 1
# GET PARKING ELEMENTS VISIBLE IN THE ACTIVE VIEW
# ============================================================

collector = (
    FilteredElementCollector(doc, view.Id)
    .OfCategory(BuiltInCategory.OST_Parking)
    .WhereElementIsNotElementType()
)

parking_elements = list(collector.ToElements())


# ============================================================
# STEP 2
# GET CENTER OF EACH PARKING
# ============================================================
#
# IMPORTANT:
# We use the Bounding Box of the parking element
# transformed to model coordinates.
#
# This computes the true geometric center for rotated/oriented
# parking spaces and avoids depending on the Family Origin /
# LocationPoint being at the visual center.
#


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
                    # Defensive fallback for unusual/invalid transforms.
                    corners.append(local_point)

    return corners


def get_center(element):
    """Get the center of the element's bounding box with fallbacks."""
    bbox = element.get_BoundingBox(view)

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
            return XYZ(center_x, center_y, center_z)

    # Fallback to LocationPoint if bounding box is unavailable
    try:
        loc = element.Location
        if hasattr(loc, "Point"):
            return loc.Point
    except Exception:
        pass

    return None


def get_axis_aligned_bounds(bbox):
    """Return model-coordinate min/max bounds for a BoundingBoxXYZ."""
    corners = get_bbox_corners(bbox)

    if not corners:
        return None

    return (
        min(p.X for p in corners),
        min(p.Y for p in corners),
        min(p.Z for p in corners),
        max(p.X for p in corners),
        max(p.Y for p in corners),
        max(p.Z for p in corners)
    )


def bounds_overlap(a, b, tolerance=0.0):
    """Check whether two axis-aligned bounds overlap."""
    if a is None or b is None:
        return False

    # Compare XY only: TextNotes live in the active view plane, and their
    # bounding-box Z range may not match the parking family's model Z range.
    return not (
        a[3] < b[0] - tolerance or b[3] < a[0] - tolerance or
        a[4] < b[1] - tolerance or b[4] < a[1] - tolerance
    )


def is_numbering_text(text):
    """Return True if text appears to be a parking number annotation.
    
    Identifies numeric labels (e.g. '01', '1', '99', '100', 'P-01', '#1')
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


# Snapshot existing text notes in the active view BEFORE creating anything.
# This makes repeated runs non-destructive: spaces already containing a
# numbering note are skipped rather than receiving duplicate overlapping notes.
existing_text_notes = list(
    FilteredElementCollector(doc, view.Id)
    .OfClass(TextNote)
    .WhereElementIsNotElementType()
    .ToElements()
)

existing_text_bounds = []
for existing_note in existing_text_notes:
    try:
        note_bbox = existing_note.get_BoundingBox(view)
        note_bounds = get_axis_aligned_bounds(note_bbox)
        if note_bounds is not None:
            try:
                note_text = existing_note.Text
            except Exception:
                note_text = ""
            existing_text_bounds.append({
                "id": existing_note.Id.IntegerValue,
                "bounds": note_bounds,
                "text": note_text
            })
    except Exception:
        pass


# Store parking + center point
parking_data = []

no_location = []


for element in parking_elements:

    point = get_center(element)

    if point is None:

        no_location.append(
            element.Id.IntegerValue
        )

    else:

        parking_data.append({
            "element": element,
            "point": point
        })


# ============================================================
# STEP 3
# SORT PARKING BY Y
# ============================================================

parking_data.sort(
    key=lambda item: item["point"].Y,
    reverse=ROWS_TOP_TO_BOTTOM
)


# ============================================================
# STEP 4
# GROUP PARKING INTO ROWS
# ============================================================

rows = []

current_row = []
row_reference_y = None


for item in parking_data:

    y = item["point"].Y

    # First parking
    if row_reference_y is None:

        current_row = [item]
        row_reference_y = y

    # Same row
    elif abs(y - row_reference_y) <= ROW_TOLERANCE:

        current_row.append(item)

    # New row
    else:

        rows.append(current_row)

        current_row = [item]
        row_reference_y = y


# Add last row
if current_row:
    rows.append(current_row)


# ============================================================
# STEP 5
# SORT EACH ROW LEFT → RIGHT
# ============================================================

for row in rows:

    row.sort(
        key=lambda item: item["point"].X
    )


# ============================================================
# STEP 6
# CREATE FINAL NUMBERING ORDER
# ============================================================

ordered_parking = []

for row in rows:

    ordered_parking.extend(row)


# ============================================================
# STEP 7
# GET DEFAULT TEXT NOTE TYPE
# ============================================================

text_type_id = doc.GetDefaultElementTypeId(
    ElementTypeGroup.TextNoteType
)


# ============================================================
# STEP 8
# TEXT NOTE OPTIONS
# ============================================================

text_options = TextNoteOptions(
    text_type_id
)

# Center text horizontally around insertion point
text_options.HorizontalAlignment = (
    HorizontalTextAlignment.Center
)

# Keep text horizontal
text_options.Rotation = 0


# ============================================================
# STEP 9
# CONVERT TEXT SIZE
# ============================================================
#
# Revit internal unit = feet
# 1 foot = 304.8 mm
#

TEXT_SIZE_FT = TEXT_SIZE_MM / 304.8


# ============================================================
# STEP 10
# CREATE TEXT NOTES
# ============================================================

created_notes = []
errors = []
skipped_existing_text = []


TransactionManager.Instance.EnsureInTransaction(doc)


for index, item in enumerate(ordered_parking):

    element = item["element"]
    point = item["point"]

    # Skip a parking space if an existing numbering note overlaps its bounding box.
    # This prevents duplicate numbering upon re-running while preserving existing notes.
    # Unrelated descriptive annotations (e.g. 'RESERVED', 'EV ONLY') do not cause
    # the space to be skipped.
    try:
        parking_bbox = element.get_BoundingBox(view)
        if parking_bbox is None:
            parking_bbox = element.get_BoundingBox(None)
        parking_bounds = get_axis_aligned_bounds(parking_bbox)
    except Exception:
        parking_bounds = None

    conflicting_note_ids = []
    if parking_bounds is not None:
        for existing_note in existing_text_bounds:
            if bounds_overlap(parking_bounds, existing_note["bounds"]):
                if is_numbering_text(existing_note.get("text", "")):
                    conflicting_note_ids.append(existing_note["id"])

    if conflicting_note_ids:
        skipped_existing_text.append({
            "ParkingId": element.Id.IntegerValue,
            "ExistingTextNoteIds": conflicting_note_ids
        })
        continue

    # Example:
    # 01
    # 02
    # 03
    # ...
    number = START_NUMBER + index

    text = "{:02d}".format(number)


    try:

        # Create Text Note
        note = TextNote.Create(
            doc,
            view.Id,
            point,
            text,
            text_options
        )


        # Set text size
        text_size_parameter = note.get_Parameter(
            BuiltInParameter.TEXT_SIZE
        )


        if text_size_parameter is not None:

            if not text_size_parameter.IsReadOnly:

                text_size_parameter.Set(
                    TEXT_SIZE_FT
                )


        # Store result
        created_notes.append({

            "ParkingId":
                element.Id.IntegerValue,

            "Number":
                text,

            "TextNoteId":
                note.Id.IntegerValue,

            "X":
                point.X,

            "Y":
                point.Y

        })


    except Exception as e:

        errors.append({

            "ParkingId":
                element.Id.IntegerValue,

            "Number":
                text,

            "Error":
                str(e)

        })


# Finish transaction
TransactionManager.Instance.TransactionTaskDone()


# ============================================================
# OUTPUT
# ============================================================

summary = {

    "ParkingFound":
        len(parking_elements),

    "ParkingWithLocation":
        len(parking_data),

    "RowsDetected":
        len(rows),

    "TextNotesCreated":
        len(created_notes),

    "SkippedExistingText":
        len(skipped_existing_text),

    "ExistingTextConflicts":
        skipped_existing_text,

    "NoLocation":
        len(no_location),

    "Errors":
        len(errors),

    "ActiveView":
        view.Name

}


OUT = (
    created_notes,
    errors,
    no_location,
    summary
)
