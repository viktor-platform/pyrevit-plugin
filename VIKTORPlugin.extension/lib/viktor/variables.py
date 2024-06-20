import json
from pathlib import Path
from pyrevit import script

def _read_data_file(filepath):
    try:
        with filepath.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, ValueError):
        return {}


def _get_viktor_global_file_path():
    return Path(script.get_universal_data_file('myVIKTORdata', 'json'))


def _get_viktor_doc_file_path():
    return Path(script.get_document_data_file('myVIKTORdata', 'json'))


def get_viktor_global_var(varname):
    data = _read_data_file(_get_viktor_global_file_path())
    return data.get(varname)


def get_viktor_doc_var(varname):
    data = _read_data_file(_get_viktor_doc_file_path())
    return data.get(varname)


def set_viktor_global_data(**kwargs):
    file_path = _get_viktor_global_file_path()
    data = _read_data_file(file_path)
    data.update(kwargs)
    with file_path.open("w+", encoding="utf-8") as f:
        json.dump(data, f)


def set_viktor_doc_data(**kwargs):
    file_path = _get_viktor_doc_file_path()
    data = _read_data_file(file_path)
    data.update(kwargs)
    with file_path.open("w+", encoding="utf-8") as f:
        json.dump(data, f)