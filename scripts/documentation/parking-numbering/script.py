# -*- coding: utf-8 -*-
"""Number parking elements in the active view with text notes.

INPUT
    IN[0] Starting number (rounded to the nearest integer; fallback 1)

OUTPUT
    OUT[0] Created text-note records
    OUT[1] Per-element errors
    OUT[2] Parking element IDs without a bounding box
    OUT[3] Summary dictionary

Target: Revit 2025 / Dynamo 3 / CPython 3.
"""

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
# in the ACTIVE VIEW.
#
# This avoids depending on the Family Origin /
# LocationPoint being at the visual center.
#


def get_center(element):

    bbox = element.get_BoundingBox(view)

    if bbox is None:
        return None

    center_x = (bbox.Min.X + bbox.Max.X) / 2.0
    center_y = (bbox.Min.Y + bbox.Max.Y) / 2.0

    # Use the element's bounding box Z center
    center_z = (bbox.Min.Z + bbox.Max.Z) / 2.0

    return XYZ(
        center_x,
        center_y,
        center_z
    )


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


TransactionManager.Instance.EnsureInTransaction(doc)


for index, item in enumerate(ordered_parking):

    element = item["element"]
    point = item["point"]

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