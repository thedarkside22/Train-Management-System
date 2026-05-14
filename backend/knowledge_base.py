"""
knowledge_base.py - Train System Knowledge Base by Ziyad

all policies, and system information for the RAG chatbot.
"""

DOCUMENTS = [{
        "id": "booking_process",
        "title": "Ticket Booking Process",
        "category": "booking",
        "content": (
            "To book a ticket, staff must follow these steps: "
            "1) Log into the system with staff or admin credentials. "
            "2) Navigate to the Reservations page from the sidebar. "
            "3) Click the 'Book Ticket' button at the top right. "
            "4) In the 'Find Passenger' section, search for the passenger by name or national ID. "
            "If the passenger is not registered, they must be registered first on the Passengers page. "
            "5) Click on the correct passenger from the search results — they will be highlighted in blue. "
            "6) In the 'Select Schedule' section, choose an available schedule from the list. "
            "Only schedules with available seats are shown. Each shows train name, route, time, price, and seats. "
            "7) Review the booking summary at the bottom: passenger name, train, route, date, time, and price. "
            "8) Click the green 'Confirm Booking' button. "
            "9) The system generates a unique booking reference in format TRN-XXXXXX (e.g., TRN-A3X7K9). "
            "10) The available seats for that schedule decrease by one automatically. "
            "Each passenger can only have one confirmed booking per schedule. "
            "Attempting to book the same passenger on the same schedule will be rejected with error 409."
        ),
    },
    {
        "id": "booking_for_others",
        "title": "Booking Tickets for Other Passengers",
        "category": "booking",
        "content": (
            "Staff members can book tickets for any registered passenger. "
            "The person making the booking does not need to be the traveler. "
            "To book for someone else: search for their name or national ID in the booking flow. "
            "Each booking is for one passenger on one schedule. "
            "To book for multiple passengers (e.g., a family), create separate bookings for each person. "
            "Each person gets their own booking reference. "
            "Round trips require two separate bookings: one for the outgoing journey and one for the return."
        ),
    },
    {
        "id": "booking_changes",
        "title": "Modifying an Existing Booking",
        "category": "booking",
        "content": (
            "The system does not support direct modification of existing bookings. "
            "To change a booking (different date, time, or route): "
            "1) Cancel the existing booking using its reference number. "
            "2) The seat is automatically released. "
            "3) Create a new booking with the desired schedule. "
            "If the new schedule is fully booked, try alternative times or dates. "
            "The original booking's refund policy still applies to the cancellation."
        ),
    },
 
    {
        "id": "cancellation_policy",
        "title": "Ticket Cancellation Policy",
        "category": "cancellation",
        "content": (
            "Cancellation rules and procedures: "
            "Staff or admin can cancel any confirmed reservation from the Reservations page. "
            "To cancel: find the booking by reference number or passenger name, then click Cancel. "
            "When a booking is cancelled: "
            "1) The reservation status changes from 'confirmed' to 'cancelled'. "
            "2) The seat is automatically released and becomes available for other passengers. "
            "3) The available seat count for that schedule increases by one. "
            "4) The cancellation timestamp is recorded in the system. "
            "Cancelled bookings remain in the system for record-keeping but the ticket is no longer valid. "
            "After cancelling, the passenger can rebook on the same or a different schedule."
        ),
    },
    {
        "id": "refund_policy",
        "title": "Refund Policy",
        "category": "cancellation",
        "content": (
            "Refund amounts depend on when the cancellation is made relative to departure: "
            "- More than 48 hours before departure: 100% full refund. "
            "- Between 24 and 48 hours before departure: 75% refund. "
            "- Between 2 and 24 hours before departure: 50% refund. "
            "- Less than 2 hours before departure: 25% refund. "
            "- After departure (no-show): No refund. "
            "Refunds are processed automatically by the system. "
            "The refund amount is calculated based on the price_paid field of the reservation. "
            "Refunds are returned to the original payment method. "
            "Processing time: refunds typically appear within 3-5 business days."
        ),
    },
 
    {
        "id": "passenger_registration",
        "title": "Passenger Registration Requirements",
        "category": "passenger",
        "content": (
            "To register a new passenger, the following information is required: "
            "1) Full name: Minimum 2 characters, maximum 100 characters. Must match the official ID. "
            "2) National ID: Must be exactly 10 digits. "
            "   - IDs starting with 1 are for Saudi citizens. "
            "   - IDs starting with 2 are for residents (iqama holders). "
            "   - No other starting digits are accepted. The system validates this automatically. "
            "3) Phone number: Must be a valid Saudi mobile number in 05XXXXXXXX format (10 digits total). "
            "   The system also accepts +966 and 966 international formats and converts them automatically. "
            "   Example: +966512345678 becomes 0512345678. "
            "4) Email address: Optional. If provided, must be a valid email format. "
            "   Each email can only be used once across all passengers. "
            "Each national ID can only be registered once in the system. "
            "If a passenger is already registered, search for them on the Passengers page instead. "
            "Both staff and admin users can register passengers."
        ),
    },
    {
        "id": "passenger_search",
        "title": "Finding Existing Passengers",
        "category": "passenger",
        "content": (
            "To find an existing passenger: "
            "1) Go to the Passengers page from the sidebar. "
            "2) Use the search bar at the top to search by: "
            "   - Full name (partial matches work, e.g., 'Mohammed' finds 'Mohammed Ali'). "
            "   - National ID (exact or partial match). "
            "   - Phone number (exact or partial match). "
            "3) There is also a dedicated endpoint to look up by national ID directly. "
            "Staff can use the passenger search during the booking flow to find passengers quickly. "
            "If the passenger is not found, they need to be registered first."
        ),
    },
 
    {
        "id": "pricing_policy",
        "title": "Ticket Pricing Policy",
        "category": "pricing",
        "content": (
            "Ticket prices are set by administrators when creating schedules. "
            "All prices are displayed in Saudi Riyals (SAR). "
            "Price ranges by route (approximate): "
            "- Riyadh to Jeddah: 150 to 300 SAR depending on train type and departure time. "
            "- Riyadh to Dammam: 100 to 200 SAR. "
            "- Jeddah to Medina: 80 to 150 SAR via Haramain High-Speed Railway. "
            "- Dammam to Riyadh: 100 to 200 SAR (same as Riyadh-Dammam). "
            "Prices may vary based on demand and time of day. "
            "Peak hours (morning 7-9 AM and evening 4-7 PM) typically have higher prices. "
            "Off-peak hours may offer lower prices for the same route. "
            "The price is locked at booking time. If the schedule price changes later, "
            "existing bookings keep their original price. "
            "There are currently no discount programs (student, senior, child). "
            "Group bookings receive the standard per-ticket price."
        ),
    },
 
    {
        "id": "routes_info",
        "title": "Available Train Routes",
        "category": "schedules",
        "content": (
            "Available train routes in Saudi Arabia: "
            "1) Riyadh to Jeddah: High-speed service, approximately 2 hours 30 minutes. "
            "   Typical daily departures: 6:00 AM, 8:00 AM, 12:00 PM, 4:00 PM, 8:00 PM. "
            "2) Riyadh to Dammam: Eastern Line, approximately 3 hours 30 minutes. "
            "   Typical daily departures: 7:00 AM, 11:00 AM, 3:00 PM, 5:00 PM. "
            "3) Jeddah to Medina: Haramain High-Speed Railway, approximately 2 hours. "
            "   Multiple daily departures from early morning to evening. "
            "4) Dammam to Riyadh: Return service via Eastern Line, same duration. "
            "5) Jeddah to Riyadh: Return high-speed service. "
            "6) Medina to Jeddah: Return Haramain service. "
            "All routes are bidirectional. Check the Schedules page for current availability."
        ),
    },
    {
        "id": "schedule_management",
        "title": "Schedule Creation and Management",
        "category": "schedules",
        "content": (
            "Schedule management is restricted to administrators. "
            "To create a new schedule: "
            "1) Go to the Schedules page and click 'Add Schedule'. "
            "2) Select a train from the dropdown (only Active trains are shown). "
            "3) Enter origin city, destination city (must be different). "
            "4) Set departure date, departure time, and arrival time. "
            "5) Set ticket price in SAR (must be greater than 0). "
            "6) Available seats are automatically set to the train's total capacity. "
            "The system prevents duplicate schedules: "
            "the same train cannot have two schedules with the same date and departure time. "
            "Schedules can only be created for trains with 'Active' status. "
            "Inactive or Maintenance trains cannot have new schedules. "
            "Administrators can also edit schedule details (route, times, price) and delete schedules."
        ),
    },
    {
        "id": "schedule_search",
        "title": "Searching and Filtering Schedules",
        "category": "schedules",
        "content": (
            "The Schedules page provides several filter options: "
            "1) Origin city: Shows only schedules departing from this city (partial match). "
            "2) Destination city: Shows only schedules arriving at this city (partial match). "
            "3) Departure date: Shows only schedules on this specific date. "
            "4) Available Only checkbox: Hides fully booked schedules (0 available seats). "
            "Filters can be combined. For example: origin=Riyadh, destination=Jeddah, date=2026-04-01. "
            "Results are sorted by departure date and time (earliest first). "
            "Each schedule card shows: train name, train type, route, departure/arrival times, "
            "ticket price in SAR, and available seats with color coding."
        ),
    },
 
    {
        "id": "seat_tracking",
        "title": "Seat Availability Tracking",
        "category": "seats",
        "content": (
            "Seat availability is managed automatically by the system using database transactions. "
            "When a new schedule is created, available seats equals the train's total capacity. "
            "For example, if a train has 300 seats, a new schedule starts with 300 available seats. "
            "Each confirmed booking decreases available seats by 1. "
            "Each cancellation increases available seats by 1. "
            "The system uses atomic database transactions to prevent overbooking: "
            "if two staff members try to book the last seat simultaneously, "
            "only one will succeed and the other receives an error message. "
            "The Schedules page shows real-time seat availability with color coding: "
            "Green (>50% available), Yellow (20-50%), Orange (<20%), Red (fully booked / 0 seats). "
            "Staff should check availability before attempting to book. "
            "If a schedule is fully booked, suggest alternative departure times or dates."
        ),
    },
 
    {
        "id": "admin_role",
        "title": "Administrator Role and Permissions",
        "category": "roles",
        "content": (
            "Administrators have full access to all system features: "
            "- Train management: Add new trains, edit train details (name, type, seats, status), "
            "  delete trains (WARNING: cascade deletes all schedules and reservations). "
            "- Schedule management: Create, edit, and delete schedules. Set ticket prices. "
            "- Passenger management: Register and search passengers (same as staff). "
            "- Reservation management: Book tickets, cancel reservations, look up bookings. "
            "- Dashboard: View system statistics (total trains, schedules, passengers, reservations). "
            "- Reports: Generate daily, weekly, and monthly reports. Export as PDF or CSV. "
            "  Revenue reports show earnings by route and train. "
            "- AI features: Access demand forecasting and dynamic pricing suggestions. "
            "Admin accounts are created by selecting 'Admin' role during registration."
        ),
    },
    {
        "id": "staff_role",
        "title": "Staff Role and Permissions",
        "category": "roles",
        "content": (
            "Staff members have access to day-to-day operations: "
            "- Passenger management: Register new passengers, search existing passengers. "
            "- Reservations: Book tickets for passengers, cancel reservations, look up by reference. "
            "- Schedules: View and search schedules (read-only, cannot create/edit/delete). "
            "- Trains: View train list (read-only, cannot create/edit/delete). "
            "Staff CANNOT: create trains, create schedules, set prices, view reports, "
            "access the dashboard analytics, or use AI features. "
            "If a staff member tries to access an admin-only feature, "
            "they receive a 403 Forbidden error. "
            "Staff accounts are the default role when registering."
        ),
    },
 
    {
        "id": "login_procedure",
        "title": "Login Procedure",
        "category": "security",
        "content": (
            "To access the system: "
            "1) Open the system URL in a web browser (Chrome, Firefox, Safari, or Edge). "
            "2) Enter your username and password on the login page. "
            "3) Click 'Sign In'. "
            "4) You will be redirected to the Dashboard (admin) or Reservations page (staff). "
            "If you don't have an account: click 'Register' to create one. "
            "Registration requires: username (letters, numbers, underscores only), "
            "email address, password, full name, and role selection. "
            "After registering, you are automatically logged in."
        ),
    },
    {
        "id": "password_policy",
        "title": "Password Requirements and Security",
        "category": "security",
        "content": (
            "Password requirements: "
            "- Minimum 8 characters. "
            "- At least one uppercase letter (A-Z). "
            "- At least one lowercase letter (a-z). "
            "- At least one digit (0-9). "
            "Example valid password: TrainSystem1 "
            "Example invalid passwords: train123 (no uppercase), TRAIN123 (no lowercase), TrainSystem (no digit). "
            "Security features: "
            "- Passwords are hashed with bcrypt before storage. Plain text is never stored. "
            "- JWT tokens expire after 24 hours. You must log in again after expiry. "
            "- Failed logins return a generic error to prevent username enumeration. "
            "- Self-service password change is not currently available. Contact admin for resets."
        ),
    },
 
    {
        "id": "booking_reference",
        "title": "Booking Reference System",
        "category": "booking",
        "content": (
            "Every confirmed booking receives a unique reference number. "
            "Format: TRN-XXXXXX where X is a random uppercase letter or digit. "
            "Examples: TRN-A3X7K9, TRN-B5M2P8, TRN-9KL4W2. "
            "The reference is generated automatically and checked for uniqueness. "
            "Uses for the booking reference: "
            "1) Look up booking details on the Reservations page search bar. "
            "2) Staff use it to find and cancel specific bookings. "
            "3) Passengers should save it for check-in at the station. "
            "4) Customer service uses it to identify bookings quickly. "
            "If a passenger loses their reference: staff can find their bookings "
            "by searching with the passenger's name or national ID on the Reservations page. "
            "References are permanent — even cancelled bookings keep their reference for records."
        ),
    },
 
    {
        "id": "train_management",
        "title": "Train Management (Admin Only)",
        "category": "trains",
        "content": (
            "Train management is restricted to administrators. "
            "Each train has these properties: "
            "- Name: Unique identifier (e.g., 'Riyadh Express', 'Eastern Line 01'). "
            "- Type: 'High-Speed', 'Regional', or 'Local'. "
            "- Total seats: Capacity between 1 and 2000 passengers. "
            "- Status: 'Active' (in service), 'Inactive' (not running), or 'Maintenance' (under repair). "
            "Actions: "
            "- Add train: Click 'Add Train', fill in name, type, seats, status. "
            "- Edit train: Click 'Edit' next to any train, change any field. "
            "- Delete train: Click 'Delete'. WARNING — cascade delete removes ALL schedules "
            "  and ALL reservations for that train. A confirmation dialog appears first. "
            "- Search: Use the search bar to filter by name or type. "
            "Only Active trains can have new schedules created for them."
        ),
    },
 
    {
        "id": "dashboard_info",
        "title": "Dashboard Overview",
        "category": "reports",
        "content": (
            "The Dashboard shows key system statistics at a glance: "
            "- Total trains: Number of trains in the system (all statuses). "
            "- Total schedules: Number of active schedules. "
            "- Registered passengers: Total passenger count. "
            "- Total reservations: All bookings (confirmed + cancelled). "
            "The Dashboard refreshes automatically when you visit it. "
            "It is accessible to both admin and staff users. "
            "For detailed analytics, administrators should use the Reports page."
        ),
    },
    {
        "id": "reports_info",
        "title": "Reports (Admin Only)",
        "category": "reports",
        "content": (
            "Reports are available to administrators only. Available report types: "
            "1) Daily booking report: All bookings made on a specific date, with details. "
            "2) Weekly summary: Total bookings, cancellations, and revenue for 7 days. "
            "3) Monthly revenue report: Revenue breakdown by route and train type. "
            "4) Occupancy report: Average seat utilization percentage per schedule. "
            "5) Route popularity: Which routes have the most bookings. "
            "All reports can be filtered by date range. "
            "Export options: PDF (for printing/sharing) or CSV (for Excel analysis). "
            "Revenue calculations are based on the price_paid field of confirmed reservations."
        ),
    },
 
    {
        "id": "system_tech",
        "title": "System Technical Overview",
        "category": "technical",
        "content": (
            "Technology stack: "
            "- Frontend: React with Vite build tool and Tailwind CSS for styling. "
            "- Backend: FastAPI (Python) with SQLAlchemy ORM. "
            "- Database: PostgreSQL for production, SQLite for local development. "
            "- Authentication: JWT tokens with bcrypt password hashing. "
            "- AI: Chatbot powered by Llama language model with RAG pipeline, "
            "  demand forecasting using LSTM neural network, "
            "  dynamic pricing using machine learning. "
            "The system is a web application accessible from modern browsers "
            "(Chrome, Firefox, Safari, Edge) on desktop and mobile. "
            "An internet connection is required. "
            "API documentation is available at /docs (Swagger UI). "
            "The backend runs on port 8000, frontend on port 5173."
        ),
    },
    {
        "id": "troubleshooting",
        "title": "Troubleshooting Common Issues",
        "category": "technical",
        "content": (
            "Common issues and solutions: "
            "1) 'Invalid username or password': Check caps lock. Passwords are case-sensitive. "
            "2) 'Token expired' (401 error): Your session expired after 24 hours. Log in again. "
            "3) 'Access denied' (403 error): You don't have permission. Ask admin for the right role. "
            "4) 'National ID already registered' (409 error): Passenger exists. Search for them instead. "
            "5) 'No seats available' (400 error): Train is full. Try a different time or date. "
            "6) 'Passenger already booked' (409 error): This person already has a ticket for this schedule. "
            "7) Page not loading: Check internet, clear browser cache, try a different browser. "
            "8) System down: Contact the system administrator. Data is safe in the database. "
            "For any other issues, contact the system administrator with the error message."
        ),
    },
 
    {
        "id": "system_purpose",
        "title": "System Purpose and Scope",
        "category": "general",
        "content": (
            "This is the Train Schedule and Reservation Management System for Saudi Arabia. "
            "The system handles: train management, schedule creation, passenger registration, "
            "ticket booking, cancellations, seat tracking, and reporting. "
            "The AI chatbot can answer questions about all of these topics. "
            "The chatbot CANNOT help with: weather, general knowledge, food orders, "
            "math problems, creative writing, or any topic outside train operations. "
            "For questions outside the scope of the train system, "
            "the chatbot will politely redirect users to train-related topics."
        ),
    },
    ]