╔══════════════════════════════════════════════╗
║       EMPLOYEE OF THE WEEK — Flask App       ║
║              Version 2.0                     ║
╚══════════════════════════════════════════════╝

DEFAULT MANAGER LOGIN:
  Username: admin
  Password: admin123
  (Change from dashboard → Change Password button)

──────────────────────────────────────────────
HOW TO RUN (Windows)
──────────────────────────────────────────────
1. Install Python from python.org (if not installed)
2. Open CMD in this folder
3. Run:
      pip install flask
      python app.py
4. Open browser → http://localhost:5000
5. Other devices on WiFi → http://YOUR_IP:5000
   (Find IP: run ipconfig → look for IPv4 Address)

──────────────────────────────────────────────
HOW TO RUN (Mac / Linux)
──────────────────────────────────────────────
1. Open Terminal in this folder
2. Run:
      pip3 install flask
      python3 app.py
3. Open browser → http://localhost:5000
4. Other devices on WiFi → http://YOUR_IP:5000
   (Find IP: run hostname -I in Terminal)

──────────────────────────────────────────────
EMPLOYEE FLOW
──────────────────────────────────────────────
1. Opens the link → Voting page appears
2. Selects their name from "Who are you?" dropdown
3. Selects who to vote for from the dropdown
4. Writes a reason
5. Submits → Thank You page with their name shown
6. Cannot vote again until next week or manager resets

──────────────────────────────────────────────
MANAGER FLOW
──────────────────────────────────────────────
1. Same voting page as employees
2. Clicks "Manager Access" at the very bottom
3. Enters username & password → Dashboard opens
4. Dashboard shows:
   - Total employees, total votes, who hasn't voted
   - All nominees with vote counts and reasons
   - Full vote log with timestamps
   - Declare winner button
   - Download PDF report
   - Change password
   - Reset week

──────────────────────────────────────────────
PDF REPORT INCLUDES
──────────────────────────────────────────────
✅ Winner at the top
✅ All nominees ranked by votes
✅ Each voter's name, designation, reason, timestamp
✅ List of employees who did NOT vote this week

──────────────────────────────────────────────
DATA
──────────────────────────────────────────────
All data saved in data.json (same folder).
Do NOT delete it — it has all records.
