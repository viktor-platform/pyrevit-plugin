#! python3
import json
import re
import requests

from pyrevit import forms
from forms import VIKTORWindow

from variables import set_viktor_global_data, get_viktor_global_var
from pathlib import Path


FORMS_DIR = Path(__file__).parent / "forms"


class PersonalAccessTokenWindow(VIKTORWindow):
    """VIKTOR Personal Access Token window"""

    def __init__(self):
        VIKTORWindow.__init__(self, str(FORMS_DIR / "VIKTORPATWindow.xaml"))

    @property
    def pat(self):
        return self.patBox.Password

    def cancel_button_click(self, sender, args):
        self.Close()

    def save_button_click(self, sender, args):
        pat = self.pat
        if not pat:
            forms.alert("Personal Access Token must be filled in!")
            return
        if not pat.startswith("vktrpat_"):
            forms.alert("Personal Access Token is invalid.")
            return
        set_viktor_global_data(VIKTOR_PAT=self.pat)
        self.Close()


def ask_for_personal_access_token():
    PersonalAccessTokenWindow().ShowDialog()
    pat = get_viktor_global_var('VIKTOR_PAT')
    if not pat:
        forms.alert("Personal Access Token is not set.")
    return pat


def _get_requests_authorization_header(token):
    return {'Authorization': 'Bearer ' + token}


def _get_requests_headers(token):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'viktor-revit-plugin/v0.0.1',
    }
    headers.update(_get_requests_authorization_header(token))
    return headers


_REQUEST_TIMEOUT = 10


def upload_file_to_s3(upload_url, upload_data, file):
    response = requests.post(
        upload_url, data=upload_data, timeout=_REQUEST_TIMEOUT, files={'file': file}
    )
    response.raise_for_status()
    return


class API:

    def __init__(self, environment, token):
        self.host = "https://" + environment + ".viktor.ai/api/"
        self._token = token
        self._session = requests.Session()
        self._session.headers = _get_requests_headers(token)

    def verify(self):
        url = self.host + "verify/"
        response = self._session.get(url, timeout=_REQUEST_TIMEOUT)
        if response.status_code == 401:
            raise ValueError("Cannot authenticate with VIKTOR. Please reset your Personal Access Token.")

    @classmethod
    def parse_resource_url(cls, resource_url):
        if not resource_url.startswith("https://"):
            raise ValueError("url invalid")
        pattern = re.compile(
            r"https://(?P<env>[a-z0-9\-]+\.?[a-z0-9]+)\.viktor\.ai/workspaces/?(?P<workspace>\d+)?(?:/app/editor/(?P<entity>\d+))?"
        )
        match = pattern.match(resource_url).groupdict()
        env = match["env"]
        workspace = int(match["workspace"]) if match["workspace"] else None
        entity = int(match["entity"]) if match["entity"] else None
        return env, workspace, entity

    def upload_file(self, workspace_id, entity_id, filename, file):
        # get upload information
        data = {"entity_id": entity_id, "filename": filename, "scope": "entity"}
        url = self.host + "workspaces/" + str(workspace_id) + "/files/"
        response = self._session.post(url, data=json.dumps(data), timeout=_REQUEST_TIMEOUT)
        if response.status_code == 401:
            raise ValueError("Cannot authenticate with VIKTOR. Please reset your Personal Access Token.")
        if response.status_code == 403:
            raise ValueError("You do not have access to this URL location. Please update the URL or ask an Admin.")
        response.raise_for_status()

        upload_url = response.json()['temp_upload_url']
        upload_data = response.json()['temp_upload_data']
        file_id = response.json()["id"]

        # upload file
        upload_file_to_s3(upload_url, upload_data, file)

        url = self.host + "workspaces/" + str(workspace_id) + "/files/"+  str(file_id) + "/uploaded/"
        response = self._session.post(url, data=data, timeout=_REQUEST_TIMEOUT)
        response.raise_for_status()
