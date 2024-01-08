import frappe
from frappe.push_notification import PushNotification

__version__ = "16.0.0-dev"


def refetch_resource(cache_key: str | list, user=None):
	frappe.publish_realtime(
		"hrms:refetch_resource",
		{"cache_key": cache_key},
		user=user or frappe.session.user,
		after_commit=True,
	)


PushNotification.set_project("hrms")
