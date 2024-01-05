# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from urllib.parse import urlparse

import frappe
from frappe.model.document import Document
from frappe.push_notification import PushNotification

class PWANotification(Document):
	def on_update(self):
		self.publish_update()

	def publish_update(self):
		frappe.publish_realtime(
			event="hrms:update_notifications",
			user=self.to_user,
			after_commit=True,
		)
		try:
			link = urlparse(frappe.utils.get_url()).hostname
			push_notification = PushNotification()
			if push_notification.is_enabled():
				PushNotification().send_notification_to_user(
					self.to_user,
					self.reference_document_type,
					self.message,
					link="https://"+link,
					truncate_body=True
				)
		except Exception as e:
			print("Error sending notification: " + str(e))
