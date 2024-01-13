# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from urllib.parse import urlparse

import frappe
from frappe.model.document import Document

import hrms

from frappe.push_notification import PushNotification

class PWANotification(Document):
	def on_update(self):
		hrms.refetch_resource("hrms:notifications", self.to_user)
		self.publish_update()

	def publish_update(self):
		frappe.publish_realtime(
			event="hrms:update_notifications",
			user=self.to_user,
			after_commit=True,
		)
		try:
			link = urlparse(frappe.utils.get_url()).hostname
			push_notification = PushNotification("hrms")
			if push_notification.is_enabled():
				push_notification.send_notification_to_user(
					self.to_user,
					self.reference_document_type,
					self.message,
					link="https://"+link,
					truncate_body=True
				)
		except Exception as e:
			print("Error sending notification: " + str(e))
