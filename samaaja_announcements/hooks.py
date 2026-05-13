app_name = "samaaja_announcements"
app_title = "Samaaja Announcements"
app_publisher = "Impactyaan"
app_description = "Announcements for Samaaja"
app_email = "contact@impactyaan.org"
app_license = "mit"

scheduler_events = {
	"hourly": [
		"samaaja_announcements.samaaja_announcements.tasks.process_announcements"
	]
}
