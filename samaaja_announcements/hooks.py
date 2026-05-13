app_name = "samaaja_announcements"
app_title = "Samaaja Announcements"
app_publisher = "Impactyaan"
app_description = "Announcements for Samaaja"
app_email = "contact@impactyaan.org"
app_license = "mit"

# Fixtures for custom fields (e.g. on User doctype)
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Samaaja Announcements"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "Samaaja Announcements"]]}
]

scheduler_events = {
	"hourly": [
		"samaaja_announcements.samaaja_announcements.tasks.process_announcements"
	]
}
