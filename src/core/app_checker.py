import shutil

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from packaging.version import Version, InvalidVersion

from .constants import PROJECT_LATEST_RELEASE_URL, PROJECT_VERSION

REQUEST_TIMEOUT_MS = 8000


class AppChecker(QObject):
    internet_checked = Signal(bool)
    update_checked = Signal(bool)
    ffmpeg_checked = Signal(bool)

    def __init__(self):
        super().__init__()
        self.manager = QNetworkAccessManager(self)

    # ------------------------------------------------------------ update check

    def check_for_update(self) -> None:
        request = QNetworkRequest(QUrl(PROJECT_LATEST_RELEASE_URL))

        request.setAttribute(
            QNetworkRequest.Attribute.RedirectPolicyAttribute,
            QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy,
        )
        request.setTransferTimeout(REQUEST_TIMEOUT_MS)

        reply = self.manager.get(request)
        reply.finished.connect(lambda: self._handle_update_response(reply))

    def _handle_update_response(self, reply: QNetworkReply) -> None:
        if reply.error() != QNetworkReply.NetworkError.NoError:
            self.update_checked.emit(False)
            reply.deleteLater()
            return

        final_url = reply.url().toString()
        latest_tag = final_url.rstrip("/").split("/")[-1]
        latest_version = latest_tag.lstrip("v")

        try:
            result = Version(latest_version) > Version(PROJECT_VERSION)
        except InvalidVersion:
            result = False

        self.update_checked.emit(result)
        reply.deleteLater()

    # ------------------------------------------------------------ internet check

    def check_for_internet(self) -> None:
        request = QNetworkRequest(QUrl("https://www.google.com"))
        request.setTransferTimeout(REQUEST_TIMEOUT_MS)

        reply = self.manager.head(request)
        reply.finished.connect(lambda: self._handle_internet_response(reply))

    def _handle_internet_response(self, reply: QNetworkReply) -> None:
        if reply.error() != QNetworkReply.NetworkError.NoError:
            self.internet_checked.emit(False)
            reply.deleteLater()
            return

        status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        self.internet_checked.emit(status == 200)
        reply.deleteLater()

    # ------------------------------------------------------------ ffmpeg check

    def exists_ffmpeg(self) -> None:
        self.ffmpeg_checked.emit(shutil.which("ffmpeg") is not None)
