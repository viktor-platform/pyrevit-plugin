"""Pushes the Active View to the VIKTOR Platform, in ifc format."""
from viktor.api import API, ask_for_personal_access_token
from viktor.variables import get_viktor_doc_var, get_viktor_global_var, set_viktor_doc_data
from viktor.revit_exporter import export_to_file
from viktor.forms import VIKTORWindow
from pyrevit import forms
from pyrevit.framework import Input


doc = __revit__.ActiveUIDocument.Document


class PushDataWindow(VIKTORWindow):
    """VIKTOR Push Data window"""

    def __init__(self):
        VIKTORWindow.__init__(self, "VIKTORPushWindow.xaml")

        self.filenameTextBox.Text = "{} - {}".format(doc.ProjectInformation.Number, doc.ProjectInformation.Name)
        self.urlTextBox.Text = get_viktor_doc_var("default_resource_url") or "<entity_URL>"

    def handle_input_key(self, sender, args):    #pylint: disable=W0613
        """Handle keyboard input and close the window on Escape."""
        if args.Key == Input.Key.Escape:
            self.Close()
        if args.Key == Input.Key.Enter:
            self.send_button_click(sender, args)
            self.Close()

    @property
    def resource_url(self):
        resource_url = self.urlTextBox.Text
        if not resource_url:
            forms.alert("Entity URL must be filled in!", exitscript=True)
        return resource_url

    @property
    def filetype(self):
        filetype = self.fileType.Text
        if not filetype:
            forms.alert("filetype must be filled in!", exitscript=True)
        return filetype

    @property
    def filename(self):
        filename = self.filenameTextBox.Text
        if not filename:
            forms.alert("filename must be filled in!", exitscript=True)
        return filename

    def cancel_button_click(self, sender, args):
        self.Close()

    def send_button_click(self, sender, args):
        resource_url = self.resource_url
        filename = self.filename + self.filetype
        set_viktor_doc_data(default_resource_url=self.resource_url)
        with forms.ProgressBar(title="Checking VIKTOR credentials ...", height=50) as pb:
            try:
                pb.title = "Checking VIKTOR credentials ..."
                pb.update_progress(1, 5)
                environment, workspace_id, entity_id = API.parse_resource_url(resource_url)
                api = API(environment=environment, token=token)
                api.verify()

                pb.title = "Exporting to {} ...".format(self.filetype)
                pb.update_progress(2, 5)
                file = export_to_file(doc, self.filetype)

                pb.title = "Uploading to VIKTOR platform ..."
                pb.update_progress(4, 5)
                api.upload_file(workspace_id=workspace_id, entity_id=entity_id, filename=filename, file=file)
                pb.update_progress(5, 5)

            except ValueError as err:
                forms.alert(str(err), exitscript=True)

        forms.toast(
            "Data successfully uploaded to VIKTOR!",
            title="VIKTOR Push", appid="VIKTOR", click=resource_url, actions={"Open in VIKTOR": resource_url}
        )
        self.Close()


if __name__ == '__main__':
    token = get_viktor_global_var('VIKTOR_PAT')
    if not token:
        token = ask_for_personal_access_token()
    PushDataWindow().show_dialog()

