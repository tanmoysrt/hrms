__version__ = "16.0.0-dev"

from hrms.frappe_notification import FrappeNotification

FrappeNotification.set_project("hrms")
FrappeNotification.CENTRAL_SERVER_ENDPOINT = "http://notification.relay:8000"