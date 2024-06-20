from pathlib import Path

from io import BytesIO

from pyrevit import script
from pyrevit.revit.db.transaction import Transaction

from Autodesk.Revit.DB import IFCExportOptions


def export_to_ifc(doc, folder, filename):
    with Transaction("Exporting to IFC"):
        options = IFCExportOptions()
        options.FilterViewId = doc.ActiveView.Id
        doc.Export(str(folder), filename + ".ifc", options=options)


EXPORTERS = {
    ".ifc": export_to_ifc
}


def export_to_file(doc, filetype):
    # Define a temporary filepath
    tmp_filename = script.get_unique_id()
    tmp_folder = Path(script.get_instance_data_file(tmp_filename)).parent
    # note that files from the `get_instance_data_file` get deleted by pyRevit on start-up

    try:
        exporter = EXPORTERS[filetype]
    except KeyError:
        raise ValueError("Selected file type is not supported")

    # Do the export
    exporter(doc, tmp_folder, tmp_filename)

    file_path = tmp_folder / "{}{}".format(tmp_filename, filetype)
    with file_path.open("rb") as f:
        return BytesIO(f.read())
