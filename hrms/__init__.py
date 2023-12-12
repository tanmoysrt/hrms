__version__ = "16.0.0-dev"

from hrms.frappe_notification import FrappeNotification

# TODO - need to set from site config or system settings
FrappeNotification.set_project("hrms")
FrappeNotification.set_site_name("hrms.test")
FrappeNotification.set_credential("cb612e4fd1eaced", "72972402d802f3d")
