import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_active_announcements():
	now = frappe.utils.now_datetime()
	
	# Fetch all published announcements
	announcements = frappe.get_all("Announcement", 
		filters={"published": 1},
		fields=["name", "title", "message", "url_link", "image", "valid_from", "valid_to", "target_audience", "total_views", "total_clicks"]
	)
	
	filtered_announcements = []
	for a in announcements:
		# 1. Valid From Check
		if a.valid_from and a.valid_from > now:
			continue
			
		# 2. Valid To Check
		if a.valid_to and a.valid_to < now:
			continue
		
		# 3. Audience Check
		if a.target_audience == "Registered Users" and frappe.session.user == "Guest":
			continue
			
		filtered_announcements.append(a)
		
	# Sort by valid_from descending
	filtered_announcements.sort(key=lambda x: x.valid_from, reverse=True)
		
	return filtered_announcements

@frappe.whitelist(allow_guest=True)
def get_unread_count():
	"""Returns count of active announcements not yet viewed by current user"""
	active = get_active_announcements()
	if not active:
		return 0
		
	active_names = [a.name for a in active]
	
	# Identify views by this user
	viewed_filters = {
		"announcement": ["in", active_names],
		"interaction_type": "View"
	}
	
	if frappe.session.user != "Guest":
		viewed_filters["user"] = frappe.session.user
	else:
		viewed_filters["ip_address"] = frappe.local.request.remote_addr if hasattr(frappe.local, "request") else "unknown"
		
	viewed_names = frappe.get_all("Announcement Interaction", 
		filters=viewed_filters, 
		pluck="announcement"
	)
	
	# Remove duplicates (one user might view multiple times)
	viewed_names = list(set(viewed_names))
	
	unread_count = len(active_names) - len(viewed_names)
	return max(0, unread_count)

@frappe.whitelist(allow_guest=True)
def record_interaction(announcement, interaction_type, contact_id=None):
	if interaction_type not in ["View", "Click"]:
		frappe.throw(_("Invalid interaction type"))
	
	doc = frappe.get_doc({
		"doctype": "Announcement Interaction",
		"announcement": announcement,
		"interaction_type": interaction_type,
		"user": frappe.session.user if frappe.session.user != "Guest" else None,
		"contact_id": contact_id,
		"ip_address": frappe.local.request.remote_addr if hasattr(frappe.local, "request") else None
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	
	return {"status": "success"}
