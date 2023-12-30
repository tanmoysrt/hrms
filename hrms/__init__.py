__version__ = "16.0.0-dev"

from hrms.frappe_notification import FrappeNotification

FrappeNotification.set_project("hrms")
FrappeNotification.set_central_server_endpoint("http://notification.relay:8000")