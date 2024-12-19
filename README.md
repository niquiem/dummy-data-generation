# Makeup Database Generator for Accommodation Platforms

This project is a Python-based tool to simulate a database for an accommodation rental platform (like Airbnb). Perfect for testing database designs, workflows, or analysis without relying on live data.

If you’re working on a project that requires database design but lacks suitable test data, this tool is for you. It includes:
	•	Generated CSV files for tables like users, accommodations, bookings, payments, and more.
	•	Python scripts to customize and generate data for various entities, ensuring logical relationships and constraints are respected.

## Features
1. **Comprehensive tables**
   - **User Table**: Includes user types (guest, host, admin), demographics, and activity data. Ensures at least 20 entries, with proportional roles.
   - **Accommodation Table**: Contains property details like price, location, and amenities, with at least 20 entries.
   - **Booking & Payment Tables**: Tracks user bookings, payments, and statuses, with all bookings referencing valid users and accommodations.
   - **Additional Tables**: Generates reviews, cancellations, notifications, admin actions, and more, while adhering to logical constraints such as minimum entries and valid relationships.

2. Constraints and Logical Rules
   •	Ensures valid relationships between users, accommodations, bookings, and more.
   •	Guarantees minimum entries for each table (e.g., 20 users, 20 properties).

2. Relationships:
	•	All foreign keys reference valid primary keys in related tables.
	•	Accommodations must have valid hosts from the Users table.
	•	Bookings reference both valid guests and accommodations.
	•	Reviews and payments are tied to confirmed bookings.

3.	Dynamic Logic:
	•	Automatically scales related entries (e.g., cities per country, reviews per booking).
	•	Validates data integrity (e.g., sufficient hosts for accommodations).

4. Customizable Scripts
   •	Easily tweak data parameters to suit different scenarios or platform requirements.

## How to Use

### If you just want CSV files:
1. Clone the repository and run the script:
   ```bash
   python generate_data.py

2.	Find the generated files in the output_data/folder.

3.	Open them in any spreadsheet or database tool for analysis.

### If you want to customize the data:
1. Open the script in your IDE.
2. Adjust the parameters in the main() function (e.g., number of users, accommodations).
3. Run the script to generate customized datasets.


 ## Logical rules at a glance
* Minimum Entries: Each table starts with 20 rows.
* Relationships: All foreign keys reference valid primary keys.
* Data Validation: Ensures bookings have valid users and accommodations.
* Time-Specific Data: All generated records (e.g., bookings, payments, reviews) fall within the month of June 2024.


### Behind the scenes
Data is generated using the Faker library.
Parameters and distributions for realism are inspired by real-world use cases.

### Support
This project is for educational and testing purposes only. For any issues, suggestions, or questions, feel free to open an issue in the repository or contact me directly.

Ready to streamline your database testing? Start generating today! 🚀
