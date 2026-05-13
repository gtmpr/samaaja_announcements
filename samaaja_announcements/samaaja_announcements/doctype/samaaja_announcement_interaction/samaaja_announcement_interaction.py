import frappe
from frappe.model.document import Document

class SamaajaAnnouncementInteraction(Document):
	def after_insert(self):
		if self.interaction_type == "View":
			frappe.db.set_value("Samaaja Announcement", self.announcement, "total_views", (frappe.db.get_value("Samaaja Announcement", self.announcement, "total_views") or 0) + 1)
		elif self.interaction_type == "Click":
			frappe.db.set_value("Samaaja Announcement", self.announcement, "total_clicks", (frappe.db.get_value("Samaaja Announcement", self.announcement, "total_clicks") or 0) + 1)
