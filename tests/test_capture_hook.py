import pytest
from rest_framework.test import APIClient

from igar.apps.capture.models import CaptureUploadRecord


def _valid_payload(upload_id: str = "upload-1", mime_type: str = "application/pdf", size: int = 1024):
    return {
        "Type": "post-finish",
        "Event": {
            "Upload": {
                "ID": upload_id,
                "Size": size,
                "MetaData": {
                    "filename": "facture.pdf",
                    "filetype": mime_type,
                },
            }
        },
    }


@pytest.mark.django_db
class TestTusHookAPIView:
    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/v1/capture/tus-hook/"

    def test_accepts_valid_post_finish_payload(self):
        response = self.client.post(self.url, _valid_payload(), format="json")
        assert response.status_code == 200
        assert response.data["status"] == "accepted"

        record = CaptureUploadRecord.objects.get(upload_id="upload-1")
        assert record.bucket == "igar-temp"
        assert record.storage_key == "upload-1/facture.pdf"

    def test_rejects_invalid_payload_with_rfc7807(self):
        response = self.client.post(self.url, {"Type": "post-finish"}, format="json")
        assert response.status_code == 400
        assert response.data["status"] == 400
        assert response.data["type"].endswith("/invalid_request")

    def test_rejects_unsupported_mime_type(self):
        payload = _valid_payload(mime_type="application/x-msdownload")
        response = self.client.post(self.url, payload, format="json")
        assert response.status_code == 422

    def test_rejects_duplicate_upload_id(self):
        first = self.client.post(self.url, _valid_payload(upload_id="dup-upload"), format="json")
        second = self.client.post(self.url, _valid_payload(upload_id="dup-upload"), format="json")
        assert first.status_code == 200
        assert second.status_code == 409
