The announcement module - trying to make it as self-servable as possible.

Features:
1. Create Announcements with title, body, linked URL, hero image
2. Schedule and Set repeat of annoucement (a background task (process_announcements) that handles recurring announcements (Hourly, Daily, Weekly, Monthly) and scheduled publishing.)
3. Samaaja Announcement Channel: A child table used to define delivery methods (e.g., "App Notification", "Email", "WhatsApp").
4. Samaaja Announcement Interaction: Tracks user behavior - Logs "Views" and "Clicks" per user (or IP address for guests) to calculate engagement and unread counts.

Install instructions
1. Clone to root folder where docker-compose.yml is there (git clone https://github.com/gtmpr/samaaja_announcements.git)
2. Get name of the frappe container
3. docker exec -it [container_id_or_name] bench --site [site-name] install-app samaaja_announcements
4. docker exec -it [container_id_or_name] bench --site [site-name] migrate


Summary of what is that we are delivering:
   * Modular Backend: A standalone Frappe app that maintainers can install via bench get-app. No manual scripts; we uses fixtures (This module does not modify the core User DocType code. Instead, it uses Frappe Fixtures) to automatically configure
     Custom Fields on the User doctype.
   * Clean Frontend Merge: The UI code is now fully synced with their latest upstream changes (including vue-i18n for multi-language support) while adding the
     new Announcements view and the unread alerts badge.
   * Production Ready: Includes the Nginx configuration and Dockerfile fixes to ensure the SPA routing and API proxying work out-of-the-box in their environment.

How Fixtures Work:
We have registered Custom Field and Property Setter as fixtures in hooks.py. When you install this app:
   1. Frappe looks into the fixtures/ directory of this app.
   2. It automatically injects any custom fields we've defined (e.g., custom tracking fields on the User DocType) into the site database.
   3. Benefit: This allows the module to be "non-intrusive." The maintainers don't need to manually add fields to the User DocType; the app handles it automatically during bench migrate.

API Endpoints
  The module exposes the following whitelisted endpoints for the frontend:
   * get_active_announcements: Returns a filtered list of announcements based on date and target audience.
   * get_unread_count: Compares active announcements against the user's interaction logs to return a real-time "unread" badge count.
   * record_interaction: Securely logs when a user views or clicks an announcement.

Engagement Tracking
  Engagement is calculated automatically.
   * Total Views: Incremented every time an announcement is loaded in the frontend list.
   * Total Clicks: Incremented when a user clicks the "Action" button or URL link.
   * Unread Badge: The frontend calls get_unread_count on login and periodically to update the red notification badge on the "Alerts" tab.

Frontend Integration
   1. Pull the announcement_updates branch
   2. Ensure the nginx.conf is configured to handle SPA routing (redirecting 404s to index.html).
   3. Rebuild the frontend container:

   1    docker-compose build frontend
   2    docker-compose up -d frontend
