# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from hrms.frappe_notification import FrappeNotification

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
			FrappeNotification.send_notification_to_user(self.to_user, self.reference_document_type, self.message)
		except Exception as e:
			print("Error sending notification: " + str(e))
