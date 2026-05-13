import frappe
from frappe.utils import now_datetime, add_to_date, get_datetime

def process_announcements():
	now = now_datetime()
	
	# 1. Process Scheduled Publish
	# Query for announcements that should be published but are not yet
	scheduled = frappe.get_all("Samaaja Announcement", 
		filters={
			"published": 0,
			"publish_on": ["<=", now]
		},
		fields=["name", "title"]
	)
	
	for s in scheduled:
		doc = frappe.get_doc("Samaaja Announcement", s.name)
		doc.published = 1
		doc.valid_from = now # Ensure it shows up on frontend immediately
		doc.save(ignore_permissions=True)
		deliver_announcement(doc)
		frappe.db.commit()

	# 2. Process Recurring Announcements
	# Query for published recurring announcements
	recurring = frappe.get_all("Samaaja Announcement",
		filters={
			"published": 1,
			"is_recurring": 1
		},
		fields=["name", "frequency", "last_sent_on", "repeat_until", "total_repeat_times", "current_repeat_count"]
	)
	
	for r in recurring:
		# Check if it has expired by date
		if r.repeat_until and get_datetime(r.repeat_until) < now:
			continue
			
		# Check if it has reached the max repeat count
		if r.total_repeat_times and r.current_repeat_count >= r.total_repeat_times:
			continue

		# Check if it is time to send based on frequency
		should_send = False
		if not r.last_sent_on:
			should_send = True
		else:
			last_sent = get_datetime(r.last_sent_on)
			if r.frequency == "Hourly" and add_to_date(last_sent, hours=1) <= now:
				should_send = True
			elif r.frequency == "Daily" and add_to_date(last_sent, days=1) <= now:
				should_send = True
			elif r.frequency == "Weekly" and add_to_date(last_sent, weeks=1) <= now:
				should_send = True
			elif r.frequency == "Monthly" and add_to_date(last_sent, months=1) <= now:
				should_send = True
				
		if should_send:
			doc = frappe.get_doc("Samaaja Announcement", r.name)
			deliver_announcement(doc)
			doc.last_sent_on = now
			doc.current_repeat_count = (doc.current_repeat_count or 0) + 1
			doc.save(ignore_permissions=True)
			frappe.db.commit()

def deliver_announcement(doc):
	"""Main delivery hub for all channels"""
	if not doc.delivery_channels:
		return
		
	for channel in doc.delivery_channels:
		if not channel.enabled:
			continue
			
		if channel.channel_name == "Email":
			send_email(doc)
		elif channel.channel_name == "App Notification":
			send_app_notification(doc)
		elif channel.channel_name == "WhatsApp":
			send_whatsapp(doc)

def send_email(doc):
	# Fetch target users based on audience
	users = get_target_users(doc.target_audience)
	if not users:
		return
		
	frappe.sendmail(
		recipients=users,
		subject=doc.title,
		message=doc.message,
		reference_doctype=doc.doctype,
		reference_name=doc.name
	)

def send_app_notification(doc):
	# Creates a standard Frappe notification log
	users = get_target_users(doc.target_audience)
	for user in users:
		frappe.get_doc({
			"doctype": "Notification Log",
			"for_user": user,
			"subject": doc.title,
			"email_content": doc.message,
			"document_type": doc.doctype,
			"document_name": doc.name,
			"type": "Alert"
		}).insert(ignore_permissions=True)

def send_whatsapp(doc):
	# Pluggable Architecture for WhatsApp / Glific
	users = get_target_users(doc.target_audience)
	frappe.log_error(f"WhatsApp requested for {doc.name}, but Glific API integration is pending configuration.", "WhatsApp Delivery")

def get_target_users(audience):
	if audience == "All":
		return frappe.get_all("User", filters={"enabled": 1}, pluck="name")
	elif audience == "Registered Users":
		# Exclude Guest
		return frappe.get_all("User", filters={"enabled": 1, "name": ["!=", "Guest"]}, pluck="name")
	return []
