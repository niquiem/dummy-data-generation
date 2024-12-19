from datetime import date, timedelta
import pandas as pd
from faker import Faker
import random
import re
import os
import itertools

fake = Faker()

# a local directory for saving files
output_directory = "output_data"
os.makedirs(output_directory, exist_ok=True)

"""
Function: populate_user_table

Purpose:
Generates a synthetic dataset for the "users" table, ensuring a proportional distribution of user roles 
(admins, hosts, and guests). The function creates realistic user profiles with attributes such as name, 
email, address, and user type, and saves the data to a CSV file.

Parameters:
- num_users (int): The desired number of users to generate (default: 100).
- output_filename (str): The name of the output CSV file (default: "users.csv").
- min_admins (int): The minimum number of admins to include in the dataset (default: 20).

Key Features:
- Ensures admins are at least 5% of the total users or `min_admins`, whichever is higher.
- At least 25% of users are hosts, with the remaining users assigned as guests.
- Generates realistic data using the `faker` library for attributes like name, email, and address.
- Saves the generated data to a CSV file.

Returns:
- A pandas DataFrame containing the generated user data.
- Returns an empty DataFrame with appropriate columns in case of an error.
"""
def populate_user_table(num_users=100, output_filename="users.csv", min_admins=20):
    try:
        min_users_needed = max(num_users, min_admins * 20)
        total_users = max(min_users_needed, num_users)

        num_admins = min_admins
        num_hosts = max(5, int(total_users * 0.25)) 
        num_guests = total_users - (num_admins + num_hosts)

        print(f"Generating {total_users} users: {num_guests} guests, {num_hosts} hosts, {num_admins} admins.")

        email_providers = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com']
        users = []
        guest_count = 0
        host_count = 0
        admin_count = 0

        for user_id in range(1, total_users + 1):
            name = fake.name()
            local_part = fake.user_name()
            domain = random.choice(email_providers)
            email = f"{local_part}@{domain}"
            password = fake.password()
            phone = re.sub(r'\D', '', fake.phone_number()) if fake.boolean(chance_of_getting_true=90) else None
            date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=75)
            gender = random.choice(['Male', 'Female', 'Other']) if fake.boolean(chance_of_getting_true=95) else None
            address = fake.street_address() + ", " + fake.city() + ", " + fake.country()
            registration_date = fake.date_this_decade()
            last_login = fake.date_time_this_year() if fake.boolean(chance_of_getting_true=85) else None
            user_status = random.choice(['active', 'inactive'])

            if admin_count < num_admins:
                user_type = 'admin'
                admin_count += 1
            elif host_count < num_hosts:
                user_type = 'host'
                host_count += 1
            else:
                user_type = 'guest'
                guest_count += 1

            users.append({
                "UserID": user_id,
                "Name": name,
                "Email": email,
                "Password": password,
                "Phone": phone,
                "UserType": user_type,
                "DateOfBirth": date_of_birth,
                "Gender": gender,
                "Address": address,
                "RegistrationDate": registration_date,
                "LastLogin": last_login,
                "UserStatus": user_status
            })

        assert admin_count >= min_admins, "Insufficient admins generated."
        assert host_count + guest_count + admin_count == total_users, "Role counts do not add up."

        df_users = pd.DataFrame(users)

        file_path = os.path.join(output_directory, output_filename)
        df_users.to_csv(file_path, index=False)
        print(f"User table data saved to: {file_path}")

        return df_users
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame(columns=[
            "UserID", "Name", "Email", "Password", "Phone",
            "UserType", "DateOfBirth", "Gender", "Address",
            "RegistrationDate", "LastLogin", "UserStatus"
        ])

"""
Function: populate_country_table

Purpose:
Generates a synthetic dataset for a "countries" table, creating a list of fictional country names. Each 
country is assigned a unique ID and a generated name based on random combinations of predefined prefixes 
and suffixes. The data is saved to a CSV file.

Parameters:
- output_filename (str): The name of the output CSV file (default: "countries.csv").
- num_countries (int): The number of countries to generate (default: 20).

Key Features:
- Creates unique country names by combining random prefixes and suffixes.
- Assigns a unique ID to each country.
- Saves the generated data to a CSV file.

Returns:
- A pandas DataFrame containing the generated country data.
- Returns an empty DataFrame with appropriate columns in case of an error.
"""
def populate_country_table(output_filename="countries.csv", num_countries=20):
    try:
        country_prefixes = ["New", "Old", "North", "South", "East", "West", "Great", "United", "Republic of"]
        country_suffixes = ["land", "stan", "ia", "nia", "lia", "rica", "esia", "dor", "ovia", "burg"]

        countries = []
        for i in range(num_countries):
            prefix = random.choice(country_prefixes)
            suffix = random.choice(country_suffixes)
            country_name = f"{prefix} {suffix}"
            countries.append({"CountryID": i + 1, "CountryName": country_name})

        df_countries = pd.DataFrame(countries)

        file_path = os.path.join(output_directory, output_filename)
        df_countries.to_csv(file_path, index=False)
        print(f"Country data successfully saved to: {file_path}")

        return df_countries
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame(columns=["CountryID", "CountryName"])


"""
Function: populate_city_table

Purpose:
Generates a synthetic dataset for a "cities" table, associating cities with countries from the provided 
countries DataFrame. Each country is guaranteed to have at least three cities, and additional cities 
are distributed randomly among countries. The data is saved to a CSV file.

Parameters:
- df_countries (DataFrame): A DataFrame containing country data, including `CountryID`.
- output_filename (str): The name of the output CSV file (default: "cities.csv").
- num_cities (int, optional): The total number of cities to generate. If not provided or insufficient, 
  it defaults to at least 3 cities per country.

Key Features:
- Ensures every country in the input DataFrame has a minimum of three cities.
- Generates realistic city names using a combination of fake first names and city suffixes.
- Randomly distributes additional cities across all countries if the `num_cities` requirement exceeds 
  the minimum needed.

Returns:
- A pandas DataFrame containing the generated city data.
- Returns an empty DataFrame with appropriate columns in case of an error.
"""
def populate_city_table(df_countries, output_filename="cities.csv", num_cities=None):
    try:
        if df_countries.empty:
            raise ValueError("No countries found. Cannot populate cities.")

        num_countries = len(df_countries)
        min_cities_required = num_countries * 3  

        if num_cities is None or num_cities < min_cities_required:
            num_cities = min_cities_required
            print(f"Adjusted num_cities to meet the minimum requirement: {num_cities}")

        city_suffixes = ["ville", "town", "burg", " City", "side", "port", "field", "bridge"]
        cities = []
        city_id = 1

        for _, country in df_countries.iterrows():
            for _ in range(3):  
                city_name = fake.first_name() + random.choice(city_suffixes)
                cities.append({
                    "CityID": city_id,
                    "CountryID": country["CountryID"],
                    "CityName": city_name
                })
                city_id += 1

        remaining_cities = num_cities - len(cities)
        while remaining_cities > 0:
            random_country = df_countries.sample(1).iloc[0]
            city_name = fake.first_name() + random.choice(city_suffixes)
            cities.append({
                "CityID": city_id,
                "CountryID": random_country["CountryID"],
                "CityName": city_name
            })
            city_id += 1
            remaining_cities -= 1

        df_cities = pd.DataFrame(cities)

        file_path = os.path.join(output_directory, output_filename)
        df_cities.to_csv(file_path, index=False)
        print(f"City data successfully saved to: {file_path}")

        return df_cities
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame(columns=["CityID", "CountryID", "CityName"])


"""
Function: populate_accommodation_table

Purpose:
Generates a synthetic dataset for an "accommodations" table, creating realistic accommodation entries 
associated with hosts, cities, and countries. The generated data includes various attributes such as 
price, property type, ratings, and availability, and saves the output to a CSV file.

Parameters:
- users_df (DataFrame): DataFrame containing user data, used to identify valid hosts.
- cities_df (DataFrame): DataFrame containing city data, used to assign CityIDs to accommodations.
- countries_df (DataFrame): DataFrame containing country data, used to assign CountryIDs to accommodations.
- output_filename (str): The name of the output CSV file (default: "accommodations.csv").
- num_accommodations (int): The total number of accommodations to generate (default: 50).

Key Features:
- Ensures accommodations are linked to valid hosts from the user data.
- Associates each accommodation with a valid city and country.
- Generates diverse property types, pricing, availability, and ratings.
- Handles validation for missing or empty data in the inputs.

Returns:
- A pandas DataFrame containing the generated accommodation data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_accommodation_table(users_df, cities_df, countries_df, output_filename="accommodations.csv", num_accommodations=50):
    try:
        valid_hosts = users_df[users_df["UserType"] == "host"]["UserID"].tolist()
        if not valid_hosts:
            raise ValueError("No valid hosts found in Users table. Cannot populate Accommodations table.")

        city_ids = cities_df["CityID"].tolist()
        country_ids = countries_df["CountryID"].tolist()
        if not city_ids or not country_ids:
            raise ValueError("City or Country table is empty. Cannot assign CityID or CountryID.")

        property_types = ["apartment", "house", "studio", "villa", "boathouse", "cabin"]
        accommodations = []

        for accommodation_id in range(1, num_accommodations + 1):
            host_id = random.choice(valid_hosts)
            title = f"Accommodation {accommodation_id}"
            description = fake.text(max_nb_chars=200)
            address = fake.street_address()
            city_id = random.choice(city_ids)
            country_id = random.choice(country_ids)
            price_per_night = round(random.uniform(50, 500), 2)
            availability_status = random.choice(['available', 'unavailable'])
            property_type = random.choice(property_types)
            num_bedrooms = random.randint(1, 5)
            num_bathrooms = random.randint(1, 3)
            square_footage = random.randint(300, 3000)
            neighborhood = fake.city() if fake.boolean(chance_of_getting_true=70) else None
            host_rating = round(random.uniform(2.5, 5.0), 1)
            accommodation_rating = round(random.uniform(2.5, 5.0), 1)
            registration_date = fake.date_this_decade()
            last_updated = fake.date_time_this_year()

            accommodations.append({
                "AccommodationID": accommodation_id,
                "HostID": host_id,
                "Title": title,
                "Description": description,
                "Address": address,
                "CityID": city_id,
                "CountryID": country_id,
                "PricePerNight": price_per_night,
                "AvailabilityStatus": availability_status,
                "PropertyType": property_type,
                "NumberOfBedrooms": num_bedrooms,
                "NumberOfBathrooms": num_bathrooms,
                "SquareFootage": square_footage,
                "Neighborhood": neighborhood,
                "HostRating": host_rating,
                "AccommodationRating": accommodation_rating,
                "RegistrationDate": registration_date,
                "LastUpdated": last_updated
            })

        accommodations_df = pd.DataFrame(accommodations)

        file_path = os.path.join(output_directory, output_filename)
        accommodations_df.to_csv(file_path, index=False)
        print(f"Accommodation table data successfully saved to: {file_path}")

        return accommodations_df
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=[
            "AccommodationID", "HostID", "Title", "Description", "Address",
            "CityID", "CountryID", "PricePerNight", "AvailabilityStatus",
            "PropertyType", "NumberOfBedrooms", "NumberOfBathrooms",
            "SquareFootage", "Neighborhood", "HostRating", "AccommodationRating",
            "RegistrationDate", "LastUpdated"
        ])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=[
            "AccommodationID", "HostID", "Title", "Description", "Address",
            "CityID", "CountryID", "PricePerNight", "AvailabilityStatus",
            "PropertyType", "NumberOfBedrooms", "NumberOfBathrooms",
            "SquareFootage", "Neighborhood", "HostRating", "AccommodationRating",
            "RegistrationDate", "LastUpdated"
        ])


"""
Function: populate_booking_table

Purpose:
Generates a synthetic dataset for a "bookings" table, simulating guest bookings for accommodations over 
a specified period. Each booking includes details such as check-in and check-out dates, total amount, 
status, and discount applied. The data is saved to a CSV file.

Parameters:
- df_users (DataFrame): DataFrame containing user data, used to identify guests.
- df_accommodations (DataFrame): DataFrame containing accommodation data.
- output_filename (str): The name of the output CSV file (default: "bookings.csv").
- max_bookings_per_guest (int): Maximum number of bookings a single guest can make (default: 3).
- max_total_bookings_multiplier (float): Multiplier to limit the total number of bookings based on 
  the number of guests (default: 1.5).

Key Features:
- Ensures only guests from the users table can create bookings.
- Simulates realistic booking details, including random check-in/check-out dates, discount rates, 
  and payment/booking statuses.
- Limits total bookings to avoid oversaturation and ensures bookings fit within the given timeframe.
- Supports flexible guest booking limits and total booking thresholds.

Returns:
- A pandas DataFrame containing the generated booking data.
- Returns an empty DataFrame with appropriate columns in case of an error.
"""
def populate_booking_table(
    df_users, 
    df_accommodations, 
    output_filename="bookings.csv", 
    max_bookings_per_guest=3, 
    max_total_bookings_multiplier=1.5
):
    try:
        guests = df_users[df_users["UserType"] == "guest"]
        if guests.empty:
            raise ValueError("No guests found. Cannot create bookings.")

        total_guests = len(guests)
        max_total_bookings = int(total_guests * max_total_bookings_multiplier)

        bookings = []
        start_date = date(2024, 6, 1)  
        end_date = date(2024, 6, 30)  
        booking_id = 1

        for _, guest in guests.iterrows():
            num_bookings = random.randint(1, max_bookings_per_guest)
            for _ in range(num_bookings):
                if len(bookings) >= max_total_bookings:
                    break

                if random.random() > 0.3:  
                    accommodation = df_accommodations.sample(1).iloc[0]
                    accommodation_id = accommodation["AccommodationID"]
                    price_per_night = accommodation["PricePerNight"]

                    check_in_date = fake.date_between(start_date=start_date, end_date=end_date)
                    max_checkout_date = min(check_in_date + timedelta(days=7), end_date)
                    check_out_date = fake.date_between(start_date=check_in_date, end_date=max_checkout_date)

                    num_nights = (check_out_date - check_in_date).days
                    if num_nights <= 0:
                        continue

                    base_amount = num_nights * price_per_night
                    discount = round(random.uniform(0, 20), 2) if random.random() < 0.8 else 0
                    total_amount = round(base_amount - (base_amount * (discount / 100)), 2)

                    booking_status = random.choices(['confirmed', 'cancelled', 'pending'], weights=[60, 20, 20], k=1)[0]
                    payment_status = random.choice(['paid', 'unpaid', 'failed'])

                    bookings.append({
                        "BookingID": booking_id,
                        "GuestID": guest["UserID"],
                        "AccommodationID": accommodation_id,
                        "CheckInDate": check_in_date,
                        "CheckOutDate": check_out_date,
                        "TotalAmount": total_amount,
                        "BookingStatus": booking_status,
                        "DiscountApplied": discount,
                        "PaymentStatus": payment_status,
                        "CreatedAt": pd.Timestamp.now(),
                        "UpdatedAt": pd.Timestamp.now()
                    })
                    booking_id += 1

        df_bookings = pd.DataFrame(bookings)
        file_path = os.path.join(output_directory, output_filename)
        df_bookings.to_csv(file_path, index=False)
        print(f"Booking table data successfully saved to: {file_path}")

        return df_bookings
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame(columns=[
            "BookingID", "GuestID", "AccommodationID", "CheckInDate",
            "CheckOutDate", "TotalAmount", "BookingStatus", "DiscountApplied",
            "PaymentStatus", "CreatedAt", "UpdatedAt"
        ])


"""
Function: populate_cancellation_table

Purpose:
Generates a synthetic dataset for a "cancellations" table, creating records of booking cancellations. 
The function ensures a minimum number of cancellations by including already cancelled bookings and 
randomly selecting additional bookings if necessary. Each record includes a cancellation date and reason.

Parameters:
- df_bookings (DataFrame): DataFrame containing booking data, used to identify cancelled and eligible bookings.
- output_filename (str): The name of the output CSV file (default: "cancellations.csv").
- min_cancellations (int): The minimum number of cancellation records to generate (default: 20).

Key Features:
- Ensures at least `min_cancellations` records, supplementing existing cancelled bookings with random selections.
- Generates realistic cancellation reasons and ensures cancellation dates precede check-in dates.
- Saves the generated cancellation data to a CSV file.

Returns:
- A pandas DataFrame containing the generated cancellation data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_cancellation_table(df_bookings, output_filename="cancellations.csv", min_cancellations=20):
    try:
        cancelled_bookings = df_bookings[df_bookings["BookingStatus"] == "cancelled"]

        if len(cancelled_bookings) < min_cancellations:
            additional_cancellations_needed = min_cancellations - len(cancelled_bookings)
            eligible_bookings = df_bookings[df_bookings["BookingStatus"] != "cancelled"]
            additional_bookings = eligible_bookings.sample(
                min(additional_cancellations_needed, len(eligible_bookings))
            )
            cancelled_bookings = pd.concat([cancelled_bookings, additional_bookings])

        cancellation_reasons = [
            "Change of travel plans",
            "Unexpected personal reasons",
            "Booking made by mistake",
            "Found a better alternative",
            "Health issues",
            "Travel restrictions",
            "Work-related obligations",
            "Accommodation reviews were concerning",
            "Budget constraints",
            "Host unresponsive or uncooperative"
        ]

        cancellations = []
        for _, booking in cancelled_bookings.iterrows():
            booking_id = booking["BookingID"]
            check_in_date = pd.to_datetime(booking["CheckInDate"]).date()

            start_date = pd.to_datetime("2024-01-01").date()
            end_date = check_in_date - timedelta(days=1)
            cancellation_date = fake.date_between(start_date=start_date, end_date=end_date).isoformat()
            cancellation_reason = random.choice(cancellation_reasons)

            cancellations.append({
                "BookingID": booking_id,
                "CancellationDate": cancellation_date,
                "CancellationReason": cancellation_reason
            })

        df_cancellations = pd.DataFrame(cancellations)

        file_path = os.path.join(output_directory, output_filename)
        df_cancellations.to_csv(file_path, index=False)
        print(f"Cancellation table data successfully saved to: {file_path}")

        return df_cancellations
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["BookingID", "CancellationDate", "CancellationReason"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["BookingID", "CancellationDate", "CancellationReason"])



"""
Function: populate_availability_table

Purpose:
Generates a synthetic dataset for an "availability" table, detailing the daily availability status of 
accommodations over a specified period. Availability is determined by existing bookings, with dates 
marked as unavailable if they overlap with confirmed bookings. The data is saved to a CSV file.

Parameters:
- df_accommodations (DataFrame): DataFrame containing accommodation data, used to identify accommodations.
- df_bookings (DataFrame): DataFrame containing booking data, used to determine availability.
- output_filename (str): The name of the output CSV file (default: "availability.csv").

Key Features:
- Initializes all dates within the specified period as available for each accommodation.
- Marks dates as unavailable based on confirmed bookings associated with each accommodation.
- Creates a comprehensive record of availability status for all accommodations over the period.

Returns:
- A pandas DataFrame containing the generated availability data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_availability_table(df_accommodations, df_bookings, output_filename="availability.csv"):
    try:
        if df_accommodations.empty:
            raise ValueError("The accommodations DataFrame is empty. Cannot generate availability data.")
        if df_bookings.empty:
            raise ValueError("The bookings DataFrame is empty. Cannot generate availability data.")

        availability = []
        start_date = date(2024, 6, 1)
        end_date = date(2024, 6, 30)

        for _, accommodation in df_accommodations.iterrows():
            accommodation_id = accommodation["AccommodationID"]

            availability_dates = {start_date + timedelta(days=i): True for i in range((end_date - start_date).days + 1)}

            confirmed_bookings = df_bookings[
                (df_bookings["AccommodationID"] == accommodation_id) &
                (df_bookings["BookingStatus"] == "confirmed")
            ]

            for _, booking in confirmed_bookings.iterrows():
                check_in_date = pd.to_datetime(booking["CheckInDate"]).date()
                check_out_date = pd.to_datetime(booking["CheckOutDate"]).date()

                for d in range((check_out_date - check_in_date).days):
                    date_to_mark = check_in_date + timedelta(days=d)
                    if date_to_mark in availability_dates:
                        availability_dates[date_to_mark] = False

            for availability_date, is_available in availability_dates.items():
                availability.append({
                    "AccommodationID": accommodation_id,
                    "Date": availability_date.isoformat(),
                    "IsAvailable": is_available
                })

        df_availability = pd.DataFrame(availability)

        file_path = os.path.join(output_directory, output_filename)
        df_availability.to_csv(file_path, index=False)
        print(f"Availability table data successfully saved to: {file_path}")

        return df_availability
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["AccommodationID", "Date", "IsAvailable"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["AccommodationID", "Date", "IsAvailable"])
    

"""
Function: populate_photo_table

Purpose:
Generates a synthetic dataset for a "photos" table, associating photo records with accommodations. Each 
record includes a unique PhotoID, the corresponding AccommodationID, and a randomly generated photo URL. 
The function ensures all accommodations have at least one photo and distributes additional photos as specified.

Parameters:
- df_accommodations (DataFrame): DataFrame containing accommodation data, used to assign photos.
- total_photos (int): The total number of photos to generate across all accommodations (default: 255).
- output_filename (str): The name of the output CSV file (default: "photos.csv").

Key Features:
- Ensures each accommodation receives at least one photo.
- Distributes additional photos randomly among accommodations until the total photo count is met.
- Generates realistic photo URLs using a fake data generator.
- Validates the input DataFrame to ensure it contains accommodations and an 'AccommodationID' column.

Returns:
- A pandas DataFrame containing the generated photo data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_photo_table(df_accommodations, total_photos=255, output_filename="photos.csv"):
    try:
        if df_accommodations.empty:
            raise ValueError("The accommodations DataFrame is empty. Cannot generate photos.")
        if "AccommodationID" not in df_accommodations.columns:
            raise ValueError("The accommodations DataFrame must include an 'AccommodationID' column.")

        photos = []
        photo_id = 1
        accommodation_ids = df_accommodations["AccommodationID"].tolist()

        min_photos = 1

        for accommodation_id in accommodation_ids:
            num_photos = random.randint(min_photos, min(10, total_photos))
            for _ in range(num_photos):
                photos.append({
                    "PhotoID": photo_id,
                    "AccommodationID": accommodation_id,
                    "PhotoURL": fake.image_url()
                })
                photo_id += 1

            total_photos -= num_photos

            if total_photos <= 0:
                break

        while total_photos > 0:
            random_accommodation = random.choice(accommodation_ids)
            photos.append({
                "PhotoID": photo_id,
                "AccommodationID": random_accommodation,
                "PhotoURL": fake.image_url()
            })
            photo_id += 1
            total_photos -= 1

        df_photos = pd.DataFrame(photos)

        file_path = os.path.join(output_directory, output_filename)
        df_photos.to_csv(file_path, index=False)
        print(f"Photo table data successfully saved to: {file_path}")

        return df_photos
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["PhotoID", "AccommodationID", "PhotoURL"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["PhotoID", "AccommodationID", "PhotoURL"])


"""
Function: populate_message_table

Purpose:
Generates a synthetic dataset for a "messages" table, simulating user-to-user messaging activity. Each 
message includes a sender, receiver, message content, and a timestamp. The function ensures all users 
can participate in messaging and randomly generates realistic message interactions.

Parameters:
- df_users (DataFrame): DataFrame containing user data, used to assign senders and receivers.
- min_messages (int): The minimum number of messages to generate (default: 20).
- scaling_factor (int): Multiplier to scale the number of messages relative to the number of users (default: 2).
- output_filename (str): The name of the output CSV file (default: "messages.csv").

Key Features:
- Ensures a minimum number of messages is generated, scaled by the number of users.
- Randomly assigns unique sender-receiver pairs to prevent users from messaging themselves.
- Generates realistic message content and timestamps using a fake data generator.
- Validates the input DataFrame to ensure it contains user data and at least two users.

Returns:
- A pandas DataFrame containing the generated message data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_message_table(df_users, min_messages=20, scaling_factor=2, output_filename="messages.csv"):
    try:
        if df_users.empty:
            raise ValueError("The users DataFrame is empty. Cannot generate messages.")
        if "UserID" not in df_users.columns:
            raise ValueError("The users DataFrame must include a 'UserID' column.")

        messages = []
        user_ids = df_users["UserID"].tolist()

        if len(user_ids) < 2:
            raise ValueError("At least two users are required to generate messages.")

        total_messages = max(min_messages, len(user_ids) * scaling_factor)

        for message_id in range(1, total_messages + 1):
            sender = random.choice(user_ids)
            receiver = random.choice(user_ids)
            while sender == receiver:  
                receiver = random.choice(user_ids)

            messages.append({
                "MessageID": message_id,
                "SenderID": sender,
                "ReceiverID": receiver,
                "MessageContent": fake.text(),
                "MessageDate": fake.date_this_year().isoformat()
            })

        df_messages = pd.DataFrame(messages)

        file_path = os.path.join(output_directory, output_filename)
        df_messages.to_csv(file_path, index=False)
        print(f"Message table data successfully saved to: {file_path}")

        return df_messages 
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["MessageID", "SenderID", "ReceiverID", "MessageContent", "MessageDate"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["MessageID", "SenderID", "ReceiverID", "MessageContent", "MessageDate"])


"""
Function: populate_house_rule_table

Purpose:
Generates a dataset for a "house rules" table, listing common rules for accommodations. Each rule is 
assigned a unique ID and a descriptive text. The function saves the data to a CSV file for use in 
applications requiring standardized house rules.

Parameters:
- output_filename (str): The name of the output CSV file (default: "house_rules.csv").

Key Features:
- Provides a predefined list of house rules commonly used in accommodations.
- Assigns unique IDs to each rule.
- Saves the generated data to a CSV file for database initialization or testing purposes.

Returns:
- A pandas DataFrame containing the house rule data.
- Returns an empty DataFrame with appropriate columns in case of an error.
"""
def populate_house_rule_table(output_filename="house_rules.csv"):
    try:
        house_rules = [
            "No smoking", "No pets allowed", "Quiet hours after 10 PM",
            "No parties or events", "Dispose of garbage properly",
            "Shoes off indoors", "No loud music", "No outside visitors",
            "Turn off lights when leaving", "No cooking after midnight",
            "Report damages immediately", "Use water sparingly",
            "Separate recyclables from trash", "No food in bedrooms",
            "Close windows when leaving", "Do not rearrange furniture",
            "Keep the front door locked", "Do not disturb neighbors",
            "No laundry after 9 PM", "Respect shared spaces"
        ]

        df_house_rules = pd.DataFrame(
            [{"HouseRuleID": idx + 1, "RuleDescription": rule} for idx, rule in enumerate(house_rules)]
        )

        file_path = os.path.join(output_directory, output_filename)
        df_house_rules.to_csv(file_path, index=False)
        print(f"House rule table successfully saved to: {file_path}")

        return df_house_rules 
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame(columns=["HouseRuleID", "RuleDescription"])
    

"""
Function: populate_house_rule_table

Purpose:
Generates a dataset for an "accommodation house rules" table, combining a list of predefined rules with 
dynamically generated ones to ensure a minimum number of rules. Each rule is assigned a unique ID and 
saved to a CSV file for use in applications involving accommodation policies.

Parameters:
- output_filename (str): The name of the output CSV file (default: "house_rules.csv").
- min_rules (int): The minimum number of house rules to generate (default: 20).

Key Features:
- Includes a predefined set of common house rules for realism.
- Dynamically generates additional rules if the predefined set does not meet the minimum count.
- Ensures no duplicate rules are included.
- Saves the generated rules to a CSV file.

Returns:
- A pandas DataFrame containing the house rules data.
- Returns an empty DataFrame with appropriate columns in case of an error.
"""
def populate_house_rule_table(output_filename="house_rules.csv", min_rules=20):
    try:
        predefined_rules = [
            "No smoking", "No pets allowed", "Quiet hours after 10 PM",
            "No parties or events", "Dispose of garbage properly",
            "Shoes off indoors", "No loud music", "No outside visitors",
            "Turn off lights when leaving", "No cooking after midnight",
            "Report damages immediately", "Use water sparingly",
            "Separate recyclables from trash", "No food in bedrooms",
            "Close windows when leaving", "Do not rearrange furniture",
            "Keep the front door locked", "Do not disturb neighbors",
            "No laundry after 9 PM", "Respect shared spaces"
        ]

        dynamic_rules = []
        while len(predefined_rules) + len(dynamic_rules) < min_rules:
            action = random.choice(["Avoid", "Do not", "Keep", "Ensure", "Respect", "Always"])
            item = random.choice(["noise levels", "cleanliness", "neighbor privacy", "shared spaces", "property rules"])
            detail = random.choice([
                "at all times", "especially at night", "during your stay",
                "when using shared facilities", "to maintain harmony"
            ])
            rule = f"{action} {item} {detail}"
            if rule not in predefined_rules and rule not in dynamic_rules:
                dynamic_rules.append(rule)

        all_rules = predefined_rules + dynamic_rules

        df_house_rules = pd.DataFrame(
            [{"HouseRuleID": idx + 1, "RuleDescription": rule} for idx, rule in enumerate(all_rules)]
        )

        file_path = os.path.join(output_directory, output_filename)
        df_house_rules.to_csv(file_path, index=False)
        print(f"House rule table successfully saved to: {file_path}")

        return df_house_rules
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame(columns=["HouseRuleID", "RuleDescription"])


"""
Function: populate_payment_table

Purpose:
Generates a dataset for a "payments" table, containing payment records for bookings with a status of 
'paid'. Each record includes details such as PaymentID, BookingID, PaymentDate, and the payment amount. 
The data is saved to a CSV file for use in applications managing payment processing.

Parameters:
- booking_data (DataFrame): DataFrame containing booking data, including `BookingID`, `PaymentStatus`, 
  `CheckInDate`, `CheckOutDate`, and `TotalAmount`.
- output_filename (str): The name of the output CSV file (default: "payments.csv").

Key Features:
- Filters bookings with `PaymentStatus == 'paid'` to create corresponding payment records.
- Ensures each payment record has a valid payment date within the booking period.
- Validates the integrity of PaymentIDs and BookingIDs to avoid inconsistencies.
- Saves the generated payment data to a CSV file.

Returns:
- A pandas DataFrame containing the payment data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_payment_table(booking_data, output_filename="payments.csv"):
    try:
        if booking_data.empty:
            raise ValueError("The booking data DataFrame is empty.")
        if "BookingID" not in booking_data.columns or "PaymentStatus" not in booking_data.columns:
            raise ValueError("The booking data DataFrame must include 'BookingID' and 'PaymentStatus' columns.")

        paid_bookings = booking_data[booking_data['PaymentStatus'] == 'paid']

        if paid_bookings.empty:
            raise ValueError("No bookings with PaymentStatus == 'paid' found. Payment table generation cannot proceed.")

        payments = []
        for i, booking in paid_bookings.iterrows():
            try:
                check_in_date = pd.to_datetime(booking["CheckInDate"])
                check_out_date = pd.to_datetime(booking["CheckOutDate"])

                payment_date = fake.date_between(start_date=check_in_date, end_date=check_out_date)
                amount = round(booking['TotalAmount'], 2)

                payments.append({
                    "PaymentID": i + 1,  
                    "BookingID": booking["BookingID"],
                    "PaymentDate": payment_date,
                    "Amount": amount
                })
            except Exception as inner_error:
                print(f"Error processing booking ID {booking['BookingID']}: {inner_error}")

        df_payments = pd.DataFrame(payments)

        missing_bookings = set(df_payments["BookingID"]) - set(booking_data["BookingID"])
        if missing_bookings:
            raise ValueError(f"Payments generated for non-existent BookingIDs: {missing_bookings}")

        file_path = os.path.join(output_directory, output_filename)
        df_payments.to_csv(file_path, index=False)
        print(f"Payment table successfully saved to: {file_path}")

        return df_payments

    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["PaymentID", "BookingID", "PaymentDate", "Amount"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["PaymentID", "BookingID", "PaymentDate", "Amount"])
    

"""
Function: populate_accommodation_house_rule_table

Purpose:
Generates a dataset for an "accommodation house rules" table, linking accommodations to specific house 
rules. Each link represents a rule applied to an accommodation. The function ensures each accommodation 
has at least one house rule and distributes additional rules randomly to create a diverse set of entries.

Parameters:
- accommodations_df (DataFrame): DataFrame containing accommodation data with an 'AccommodationID' column.
- house_rules_df (DataFrame): DataFrame containing house rule data with a 'HouseRuleID' column.
- output_filename (str): The name of the output CSV file (default: "accommodation_house_rules.csv").
- total_entries (int): The total number of entries to generate in the table (default: 85).

Key Features:
- Guarantees every accommodation is associated with at least one house rule.
- Randomly distributes additional house rules to accommodations without duplicates.
- Converts the generated associations into a DataFrame and saves the data to a CSV file.

Returns:
- A pandas DataFrame containing the accommodation-house rule mappings.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_accommodation_house_rule_table(accommodations_df, house_rules_df, 
                                            output_filename="accommodation_house_rules.csv", 
                                            total_entries=85):
    try:
        if accommodations_df.empty or 'AccommodationID' not in accommodations_df.columns:
            raise ValueError("Accommodations DataFrame is empty or missing 'AccommodationID' column.")
        if house_rules_df.empty or 'HouseRuleID' not in house_rules_df.columns:
            raise ValueError("House Rules DataFrame is empty or missing 'HouseRuleID' column.")

        accommodations = accommodations_df['AccommodationID'].tolist()
        house_rules = house_rules_df['HouseRuleID'].tolist()

        if not accommodations or not house_rules:
            raise ValueError("No accommodations or house rules found. Cannot populate the table.")

        accommodation_house_rules = set() 
        accommodation_count = len(accommodations)
        house_rule_count = len(house_rules)

        for accommodation_id in accommodations:
            selected_rule = random.choice(house_rules)
            accommodation_house_rules.add((accommodation_id, selected_rule))
            total_entries -= 1

            if total_entries <= 0:
                break

        while total_entries > 0:
            random_accommodation = random.choice(accommodations)
            random_rule = random.choice(house_rules)

            if (random_accommodation, random_rule) not in accommodation_house_rules:
                accommodation_house_rules.add((random_accommodation, random_rule))
                total_entries -= 1

        accommodation_house_rules_list = [
            {"AccommodationID": accommodation_id, "HouseRuleID": house_rule_id}
            for accommodation_id, house_rule_id in accommodation_house_rules
        ]

        df_accommodation_house_rules = pd.DataFrame(accommodation_house_rules_list)

        file_path = os.path.join(output_directory, output_filename)
        df_accommodation_house_rules.to_csv(file_path, index=False)
        print(f"AccommodationHouseRule table successfully saved to: {file_path}")

        return df_accommodation_house_rules
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["AccommodationID", "HouseRuleID"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["AccommodationID", "HouseRuleID"])



"""
Function: generate_diverse_bio

Purpose:
Creates a synthetic, diverse bio by combining randomly selected components such as hobbies, professions, 
traits, and aspirations. The generated bio is a brief, creative description suitable for user profiles 
or other contexts requiring personal introductions.

Key Features:
- Randomly selects a hobby, profession, personal trait, and aspiration from predefined lists.
- Constructs a cohesive and engaging bio sentence by combining the selected components.
- Provides variation in output, making it suitable for creating diverse user profiles.

Returns:
- A string representing the generated bio.
"""
def generate_diverse_bio():
    """Generate a diverse bio by combining random components."""
    hobbies = [
        "travels the world", "is a food lover", "enjoys hiking",
        "loves painting", "is a marathon runner", "plays the guitar",
        "writes poetry", "is a bookworm", "photographs wildlife",
        "dances salsa"
    ]
    professions = [
        "a software developer", "a teacher", "a chef",
        "a photographer", "an entrepreneur", "a designer",
        "a fitness trainer", "a musician", "an author",
        "a scientist"
    ]
    traits = [
        "passionate", "dedicated", "creative", "ambitious",
        "curious", "outgoing", "kind-hearted", "driven",
        "optimistic", "thoughtful"
    ]
    aspirations = [
        "to explore new cultures", "to change the world",
        "to inspire others", "to write a best-selling novel",
        "to innovate in technology", "to create stunning art",
        "to lead a healthier life", "to start a global movement",
        "to build meaningful connections", "to learn something new every day"
    ]

    hobby = random.choice(hobbies)
    profession = random.choice(professions)
    trait = random.choice(traits)
    aspiration = random.choice(aspirations)

    bio = f"{trait.capitalize()} and {hobby}, working as {profession}, with a dream {aspiration}."
    return bio




"""
Function: populate_profile_table

Purpose:
Generates a dataset for a "profiles" table, creating profiles for non-admin users. Each profile includes 
details such as a bio, profile picture URL, and a social network link. The function ensures every eligible 
user has a corresponding profile, and the data is saved to a CSV file.

Parameters:
- df_users (DataFrame): DataFrame containing user data, used to filter non-admin users and assign profiles.
- output_filename (str): The name of the output CSV file (default: "profiles.csv").

Key Features:
- Filters out admin users, ensuring profiles are only generated for regular users.
- Randomly generates diverse bio content, profile picture URLs, and social network links.
- Validates that all generated profiles correspond to valid user IDs from the input DataFrame.
- Saves the generated profile data to a CSV file.

Returns:
- A pandas DataFrame containing the profile data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_profile_table(df_users, output_filename="profiles.csv"):
    try:
        non_admin_users = df_users[df_users["UserType"] != "admin"]

        if non_admin_users.empty:
            raise ValueError("No non-admin users available to generate profiles.")

        profiles = []
        for i, user in non_admin_users.iterrows():
            user_id = user["UserID"]

            bio = generate_diverse_bio()[:255]
            profile_picture = fake.image_url()[:255]
            social_network_link = generate_social_network_url(random.choice(["Facebook", "Twitter", "Instagram", "LinkedIn"]))

            profiles.append({
                "ProfileID": len(profiles) + 1,
                "UserID": user_id,
                "Bio": bio,
                "ProfilePicture": profile_picture,
                "SocialNetworkLink": social_network_link
            })
        df_profiles = pd.DataFrame(profiles)

        missing_users = set(df_profiles["UserID"]) - set(df_users["UserID"])
        if missing_users:
            raise ValueError(f"Profiles generated for non-existent UserIDs: {missing_users}")

        file_path = os.path.join(output_directory, output_filename)
        df_profiles.to_csv(file_path, index=False)
        print(f"Profile table data successfully saved to: {file_path}")

        return df_profiles

    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["ProfileID", "UserID", "Bio", "ProfilePicture", "SocialNetworkLink"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["ProfileID", "UserID", "Bio", "ProfilePicture", "SocialNetworkLink"])
        

"""
Function: generate_social_network_url

Purpose:
Generates a realistic social network URL for a given platform by combining a base URL with a randomly 
generated username. If the specified network name is not recognized, a generic URL is generated.

Parameters:
- network_name (str): The name of the social network (e.g., "Twitter", "Facebook", "Instagram", "LinkedIn").

Key Features:
- Uses predefined base URLs for popular social networks.
- Appends a randomly generated username to create a realistic user profile URL.
- Defaults to a generic URL if the network name is not recognized.

Returns:
- A string containing the generated social network URL.
"""
def generate_social_network_url(network_name):
    """Generate a realistic social network URL based on the network name."""
    base_urls = {
        "Twitter": "https://twitter.com",
        "Facebook": "https://facebook.com",
        "Instagram": "https://instagram.com",
        "LinkedIn": "https://linkedin.com/in"
    }
    username = fake.user_name()
    return f"{base_urls.get(network_name, fake.url())}/{username}"


"""
Function: populate_social_network_table

Purpose:
Generates a dataset for a "social networks" table, linking users to their social network profiles. The 
function randomly assigns up to three social networks per user, each with a unique profile URL, and saves 
the data to a CSV file.

Parameters:
- df_users (DataFrame): DataFrame containing user data, used to associate social networks with users.
- output_filename (str): The name of the output CSV file (default: "social_networks.csv").

Key Features:
- Assigns social network profiles to a subset of users (30% chance per user).
- Each user may have between one and three unique social networks.
- Generates realistic social network profile URLs using predefined network names and random usernames.
- Saves the generated social network data to a CSV file.

Returns:
- A pandas DataFrame containing the social network data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_social_network_table(df_users, output_filename="social_networks.csv"):
    try:
        if df_users.empty:
            raise ValueError("The users DataFrame is empty. Cannot generate social networks.")
        if "UserID" not in df_users.columns:
            raise ValueError("The users DataFrame must include a 'UserID' column.")

        social_networks = []
        user_ids = df_users["UserID"].tolist()

        for user_id in user_ids:
            if random.random() <= 0.3:  
                num_networks = random.randint(1, 3) 
                used_networks = set()
                for _ in range(num_networks):
                    network_name = random.choice(['Facebook', 'Twitter', 'Instagram', 'LinkedIn'])
                    if network_name in used_networks:
                        continue
                    used_networks.add(network_name)

                    social_networks.append({
                        "UserID": user_id,
                        "NetworkName": network_name,
                        "NetworkProfileURL": generate_social_network_url(network_name)
                    })

        df_social_networks = pd.DataFrame(social_networks)

        file_path = os.path.join(output_directory, output_filename)
        df_social_networks.to_csv(file_path, index=False)
        print(f"SocialNetwork table successfully saved to: {file_path}")

        return df_social_networks
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["UserID", "NetworkName", "NetworkProfileURL"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["UserID", "NetworkName", "NetworkProfileURL"])


"""
Function: populate_price_table

Purpose:
Generates a dataset for a "prices" table, assigning dynamically calculated prices to accommodations. 
The function derives prices based on attributes such as property type, square footage, and host rating, 
and saves the data to a CSV file.

Parameters:
- df_accommodations (DataFrame): DataFrame containing accommodation data, used to calculate prices.
- output_filename (str): The name of the output CSV file (default: "prices.csv").

Key Features:
- Validates the accommodations DataFrame to ensure required columns are present.
- Dynamically calculates prices using the `generate_dynamic_price` function, considering property-specific attributes.
- Validates that all generated prices correspond to valid accommodations.
- Saves the generated price data to a CSV file.

Returns:
- A pandas DataFrame containing the price data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_price_table(df_accommodations, output_filename="prices.csv"):
    try:
        if df_accommodations.empty:
            raise ValueError("The accommodations DataFrame is empty. Cannot generate prices.")

        required_columns = {"AccommodationID", "PropertyType", "SquareFootage", "HostRating"}
        if not required_columns.issubset(df_accommodations.columns):
            raise ValueError(f"Missing required columns in accommodations table: {required_columns}")

        print(f"Generating prices for {len(df_accommodations)} accommodations...")

        prices = []
        for i, (_, accommodation) in enumerate(df_accommodations.iterrows(), start=1):
            accommodation_id = accommodation["AccommodationID"]
            property_type = accommodation["PropertyType"]
            square_footage = accommodation["SquareFootage"]
            host_rating = accommodation["HostRating"]

            amount = generate_dynamic_price(property_type, square_footage, host_rating)

            prices.append({
                "PriceID": i, 
                "AccommodationID": accommodation_id,
                "Amount": amount
            })

        df_prices = pd.DataFrame(prices)

        missing_accommodations = set(df_prices["AccommodationID"]) - set(df_accommodations["AccommodationID"])
        if missing_accommodations:
            raise ValueError(f"Prices generated for non-existent AccommodationIDs: {missing_accommodations}")

        file_path = os.path.join(output_directory, output_filename)
        df_prices.to_csv(file_path, index=False)
        print(f"Price table successfully saved to: {file_path}")

        return df_prices

    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["PriceID", "AccommodationID", "Amount"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["PriceID", "AccommodationID", "Amount"])   


"""
Function: generate_dynamic_price

Purpose:
Calculates dynamic pricing for accommodations based on their property type, square footage, and host rating. 
The function adjusts base prices using property attributes to create realistic price variations.

Parameters:
- property_type (str): The type of property (e.g., "apartment", "villa", "house").
- square_footage (float): The size of the property in square feet.
- host_rating (float): The host's rating on a scale of 0 to 5.

Key Features:
- Uses a predefined base price for each property type.
- Adjusts prices dynamically based on square footage and host rating.
- Ensures final price is within a realistic range (minimum $50, maximum $1000).
- Returns the dynamically calculated price rounded to two decimal places.

Returns:
- A float representing the calculated price.
"""
def generate_dynamic_price(property_type, square_footage, host_rating):
    base_price = {
        "apartment": 50,
        "villa": 100,
        "house": 80,
        "studio": 40,
        "cabin": 60,
        "boathouse": 90
    }.get(property_type.lower(), 50)   

    price_modifier = (square_footage / 1000) + (host_rating / 5)
    final_price = round(base_price * price_modifier, 2)

    return max(50, min(final_price, 1000))


"""
Function: populate_amenity_table

Purpose:
Generates a dataset for an "amenities" table, including a predefined list of amenities and dynamically 
created ones to meet a specified minimum count. Each amenity is assigned a unique ID and saved to a CSV file.

Parameters:
- output_filename (str): The name of the output CSV file (default: "amenities.csv").
- min_amenities (int): The minimum number of amenities to include in the table (default: 20).

Key Features:
- Provides a predefined list of common amenities for accommodations.
- Dynamically generates additional amenities if the predefined list does not meet the minimum count.
- Ensures all amenities are unique and realistic.
- Saves the generated data to a CSV file.

Returns:
- A pandas DataFrame containing the amenities data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_amenity_table(output_filename="amenities.csv", min_amenities=20):
    try:
        predefined_amenities = [
            'WiFi', 'Air Conditioning', 'Kitchen', 'Parking', 'Swimming Pool',
            'Gym', 'Pet Friendly', 'Washer/Dryer', 'Hot Tub', 'Heating',
            'TV', 'Private Entrance', 'Smoke Alarm', 'Carbon Monoxide Detector',
            'Balcony', 'Garden', 'Fireplace', 'Breakfast Included', 'Beach Access',
            'Bicycle Rental'
        ]

        dynamic_amenities = []
        while len(predefined_amenities) + len(dynamic_amenities) < min_amenities:
            new_amenity = fake.word().capitalize() + " Facility"
            if new_amenity not in predefined_amenities and new_amenity not in dynamic_amenities:
                dynamic_amenities.append(new_amenity)

        all_amenities = predefined_amenities + dynamic_amenities

        df_amenities = pd.DataFrame({
            "AmenityID": range(1, len(all_amenities) + 1),
            "AmenityName": all_amenities
        })

        file_path = os.path.join(output_directory, output_filename)
        df_amenities.to_csv(file_path, index=False)
        print(f"Amenity table successfully saved to: {file_path}")

        return df_amenities
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["AmenityID", "AmenityName"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["AmenityID", "AmenityName"])
    

"""
Function: populate_accommodation_amenity_table

Purpose:
Generates a dataset for an "accommodation amenities" table, linking accommodations to their respective 
amenities. The function ensures every accommodation has at least one amenity and randomly distributes 
additional amenities to meet a specified total number of entries. The data is saved to a CSV file.

Parameters:
- accommodations (DataFrame): DataFrame containing accommodation data with an 'AccommodationID' column.
- amenities (DataFrame): DataFrame containing amenity data with an 'AmenityID' column.
- output_filename (str): The name of the output CSV file (default: "accommodation_amenities.csv").
- total_entries (int): The total number of entries to generate in the table (default: 153).

Key Features:
- Ensures every accommodation is assigned at least one amenity.
- Distributes additional amenities randomly across accommodations without duplicating existing pairs.
- Converts the generated data into a DataFrame and saves it to a CSV file.

Returns:
- A pandas DataFrame containing the accommodation-amenity mappings.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_accommodation_amenity_table(accommodations, amenities, 
                                         output_filename="accommodation_amenities.csv", 
                                         total_entries=153):
    try:
        if accommodations.empty:
            raise ValueError("The accommodations DataFrame is empty. Cannot populate AccommodationAmenity table.")
        if amenities.empty:
            raise ValueError("The amenities DataFrame is empty. Cannot populate AccommodationAmenity table.")

        accommodation_amenities = []
        accommodation_amenity_id = 1

        remaining_entries = total_entries
        for _, accommodation in accommodations.iterrows():
            accommodation_id = accommodation["AccommodationID"]

            selected_amenities = random.sample(list(amenities["AmenityID"]), k=1)
            for amenity_id in selected_amenities:
                accommodation_amenities.append({
                    "AccommodationAmenityID": accommodation_amenity_id,
                    "AccommodationID": accommodation_id,
                    "AmenityID": amenity_id
                })
                accommodation_amenity_id += 1
                remaining_entries -= 1

            if remaining_entries <= 0:
                break

        while remaining_entries > 0:
            random_accommodation = random.choice(accommodations["AccommodationID"])
            random_amenity = random.choice(amenities["AmenityID"])

            if not any(
                entry["AccommodationID"] == random_accommodation and entry["AmenityID"] == random_amenity
                for entry in accommodation_amenities
            ):
                accommodation_amenities.append({
                    "AccommodationAmenityID": accommodation_amenity_id,
                    "AccommodationID": random_accommodation,
                    "AmenityID": random_amenity
                })
                accommodation_amenity_id += 1
                remaining_entries -= 1

        df_accommodation_amenities = pd.DataFrame(accommodation_amenities)

        file_path = os.path.join(output_directory, output_filename)
        df_accommodation_amenities.to_csv(file_path, index=False)
        print(f"AccommodationAmenity table successfully saved to: {file_path}")

        return df_accommodation_amenities
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["AccommodationAmenityID", "AccommodationID", "AmenityID"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["AccommodationAmenityID", "AccommodationID", "AmenityID"])

"""
Function: generate_realistic_review

Purpose:
Generates a short, realistic review text by randomly selecting from a predefined list of review sentiments. 
The function provides varied, human-like feedback suitable for simulating user reviews.

Key Features:
- Includes a mix of positive, neutral, and slightly critical review sentiments.
- Randomly selects a review text to ensure diversity in generated reviews.
- Produces concise, realistic feedback suitable for user review simulations.

Returns:
- A string representing a realistic review.
"""
def generate_realistic_review():
    sentiments = [
        "Excellent stay!", "Highly recommended!", "A very cozy place.",
        "Would definitely book again.", "The amenities were great.",
        "Perfect location!", "Wonderful host!", "A bit noisy but manageable.",
        "Loved the view!", "Clean and comfortable.", "A true home away from home.",
        "Met all my expectations.", "The pool was fantastic!", "Convenient and affordable.",
        "I'll be coming back for sure.", "Forever am I at work here."
    ]
    return random.choice(sentiments)

"""
Function: populate_review_table

Purpose:
Generates a dataset for a "reviews" table, creating reviews for accommodations based on confirmed bookings 
and additional simulated feedback if needed. Each review includes text, a rating, and a date, and is saved 
to a CSV file.

Parameters:
- accommodations (DataFrame): DataFrame containing accommodation data, used to link reviews to accommodations.
- bookings (DataFrame): DataFrame containing booking data, used to generate reviews from confirmed bookings.
- users (DataFrame): DataFrame containing user data, used to assign reviews to guests.
- output_filename (str): The name of the output CSV file (default: "reviews.csv").
- min_reviews (int): The minimum number of reviews to generate (default: 20).

Key Features:
- Generates reviews only for confirmed bookings to ensure realism.
- Includes realistic review text and ratings between 3 and 5.
- Ensures a minimum number of reviews by randomly generating additional reviews as needed.
- Saves the generated review data to a CSV file.

Returns:
- A pandas DataFrame containing the review data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_review_table(accommodations, bookings, users, 
                          output_filename="reviews.csv", 
                          min_reviews=20):
    try:
        if accommodations.empty:
            raise ValueError("The accommodations DataFrame is empty. Cannot populate Review table.")
        if bookings.empty:
            raise ValueError("The bookings DataFrame is empty. Cannot populate Review table.")
        if users.empty:
            raise ValueError("The users DataFrame is empty. Cannot populate Review table.")

        reviews = []
        review_id = 1

        confirmed_bookings = bookings[bookings["BookingStatus"] == "confirmed"]

        if confirmed_bookings.empty:
            raise ValueError("No confirmed bookings found. Reviews cannot be generated.")

        print(f"Generating reviews based on {len(confirmed_bookings)} confirmed bookings...")

        for _, booking in confirmed_bookings.iterrows():
            accommodation_id = booking["AccommodationID"]
            user_id = booking["GuestID"]  
            review_text = generate_realistic_review()
            rating = random.randint(3, 5)
            review_date = fake.date_between(start_date=booking["CheckInDate"], end_date='today').isoformat()

            reviews.append({
                "ReviewID": review_id,
                "AccommodationID": accommodation_id,
                "UserID": user_id,
                "ReviewText": review_text,
                "Rating": rating,
                "ReviewDate": review_date
            })
            review_id += 1

        additional_reviews_needed = max(0, min_reviews - len(reviews))
        accommodation_ids = accommodations["AccommodationID"].tolist()

        while additional_reviews_needed > 0:
            accommodation_id = random.choice(accommodation_ids)
            user_id = random.choice(users["UserID"])
            review_text = generate_realistic_review()
            rating = random.randint(3, 5)
            review_date = fake.date_between(start_date='-2y', end_date='today').isoformat()

            reviews.append({
                "ReviewID": review_id,
                "AccommodationID": accommodation_id,
                "UserID": user_id,
                "ReviewText": review_text,
                "Rating": rating,
                "ReviewDate": review_date
            })
            review_id += 1
            additional_reviews_needed -= 1

        df_reviews = pd.DataFrame(reviews)

        file_path = os.path.join(output_directory, output_filename)
        df_reviews.to_csv(file_path, index=False)
        print(f"Review table successfully saved to: {file_path}")

        print(f"Total reviews generated: {len(df_reviews)}")
        return df_reviews

    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["ReviewID", "AccommodationID", "UserID", "ReviewText", "Rating", "ReviewDate"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["ReviewID", "AccommodationID", "UserID", "ReviewText", "Rating", "ReviewDate"])



"""
Function: populate_host_response_table

Purpose:
Generates a dataset for a "host responses" table, creating responses from hosts to reviews. Each response 
is linked to a specific review and includes text written by the host. The function ensures a minimum number 
of responses and saves the data to a CSV file.

Parameters:
- reviews (DataFrame): DataFrame containing review data, used to associate responses with reviews.
- output_filename (str): The name of the output CSV file (default: "host_responses.csv").
- min_responses (int): The minimum number of host responses to generate (default: 20).

Key Features:
- Generates responses for a random subset of reviews, with a 50% chance for each review to receive a response.
- Ensures a minimum number of responses by randomly selecting additional reviews if necessary.
- Saves the generated host response data to a CSV file.

Returns:
- A pandas DataFrame containing the host response data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""   
def populate_host_response_table(reviews, output_filename="host_responses.csv", min_responses=20):
    try:
        if reviews.empty:
            raise ValueError("Reviews DataFrame is empty. Cannot populate HostResponse table.")

        host_responses = []
        eligible_reviews = reviews["ReviewID"].tolist()

        if len(eligible_reviews) < min_responses:
            raise ValueError(f"Insufficient reviews ({len(eligible_reviews)}) to generate the required minimum {min_responses} host responses.")

        print(f"Generating at least {min_responses} host responses...")

        for review_id in eligible_reviews:
            if random.random() < 0.5:  
                response_text = fake.text()
                host_responses.append({
                    "ReviewID": review_id,
                    "ResponseText": response_text
                })

        additional_responses_needed = max(0, min_responses - len(host_responses))
        if additional_responses_needed > 0:
            additional_reviews = random.sample(eligible_reviews, additional_responses_needed)
            for review_id in additional_reviews:
                response_text = fake.text()
                host_responses.append({
                    "ReviewID": review_id,
                    "ResponseText": response_text
                })

        df_host_responses = pd.DataFrame(host_responses)

        file_path = os.path.join(output_directory, output_filename)
        df_host_responses.to_csv(file_path, index=False)
        print(f"HostResponse table successfully saved to: {file_path}")

        return df_host_responses
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["ReviewID", "ResponseText"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["ReviewID", "ResponseText"])



"""
Function: populate_commission_table

Purpose:
Generates a dataset for a "commissions" table, calculating commissions for confirmed bookings based on 
a tiered percentage structure. The function ensures commissions are logical and linked to valid bookings, 
and saves the data to a CSV file.

Parameters:
- bookings (DataFrame): DataFrame containing booking data, used to calculate commissions for confirmed bookings.
- output_filename (str): The name of the output CSV file (default: "commissions.csv").

Key Features:
- Processes only confirmed bookings to calculate commission amounts.
- Applies a tiered commission rate based on the booking's total amount:
  - 5% for amounts > $1000
  - 10% for amounts > $500
  - 15% for amounts ≤ $500
- Skips bookings with invalid or non-positive total amounts.
- Validates that all calculated commissions correspond to valid BookingIDs.
- Saves the generated commission data to a CSV file.

Returns:
- A pandas DataFrame containing the commission data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_commission_table(bookings, output_filename="commissions.csv"):
    try:
        if bookings.empty:
            print("Bookings DataFrame is empty. Returning an empty DataFrame.")
            return pd.DataFrame(columns=["BookingID", "Amount"])

        confirmed_bookings = bookings[bookings["BookingStatus"] == "confirmed"]
        print(f"Total Confirmed Bookings: {len(confirmed_bookings)}")

        if confirmed_bookings.empty:
            print("No confirmed bookings found. Returning an empty DataFrame.")
            return pd.DataFrame(columns=["BookingID", "Amount"])

        commissions = []

        for _, booking in confirmed_bookings.iterrows():
            booking_id = booking["BookingID"]
            total_amount = booking["TotalAmount"]

            if total_amount <= 0:
                print(f"Skipping booking ID {booking_id} due to invalid TotalAmount: {total_amount}")
                continue

            if total_amount > 1000:
                commission_percentage = 5  
            elif total_amount > 500:
                commission_percentage = 10 
            else:
                commission_percentage = 15  

            amount = round(total_amount * (commission_percentage / 100), 2)

            commissions.append({
                "BookingID": booking_id,
                "Amount": amount
            })

        df_commissions = pd.DataFrame(commissions)

        missing_booking_ids = set(df_commissions["BookingID"]) - set(bookings["BookingID"])
        if missing_booking_ids:
            raise ValueError(f"Commissions generated for non-existent BookingIDs: {missing_booking_ids}")

        file_path = os.path.join(output_directory, output_filename)
        df_commissions.to_csv(file_path, index=False)
        print(f"Commission table successfully saved to: {file_path}")

        return df_commissions

    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame(columns=["BookingID", "Amount"])


"""
Function: populate_admin_table

Purpose:
Generates a dataset for an "admins" table, creating entries for users marked as administrators. Each admin 
is assigned a role (e.g., SuperAdmin, Admin, Moderator) based on a weighted selection. The data is saved 
to a CSV file.

Parameters:
- users (DataFrame): DataFrame containing user data, used to identify users with an 'admin' user type.
- output_filename (str): The name of the output CSV file (default: "admins.csv").
- min_admins (int): The minimum number of admins required in the dataset (default: 20).

Key Features:
- Filters user data to include only those marked as 'admin.'
- Assigns roles to admins using a weighted random selection.
- Ensures the minimum number of admin users are present in the dataset.
- Saves the generated admin data to a CSV file.

Returns:
- A pandas DataFrame containing the admin data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_admin_table(users, output_filename="admins.csv", min_admins=20):
    try:
        if users.empty:
            raise ValueError("User DataFrame is empty. Cannot populate Admin table.")

        admin_users = users[users["UserType"] == "admin"]

        if len(admin_users) < min_admins:
            raise ValueError(f"Insufficient admin users in the Users table. Found {len(admin_users)}, required {min_admins}.")

        print(f"Ensuring all {len(admin_users)} users marked as admins are listed in the Admin table.")

        roles = ['SuperAdmin', 'Admin', 'Moderator']
        admin_entries = []

        for _, user in admin_users.iterrows():
            role = random.choices(roles, weights=[30, 50, 20], k=1)[0] 
            admin_entries.append({
                "AdminID": len(admin_entries) + 1,
                "UserID": user["UserID"],
                "Role": role
            })

        df_admins = pd.DataFrame(admin_entries)

        file_path = os.path.join(output_directory, output_filename)
        df_admins.to_csv(file_path, index=False)
        print(f"Admin table successfully saved to: {file_path}")

        return df_admins
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame(columns=["AdminID", "UserID", "Role"])


"""
Function: populate_admin_action_table

Purpose:
Generates a dataset for an "admin actions" table, recording actions performed by admins. Each action 
includes an admin ID, a description of the action, and the date the action occurred. The function ensures 
a minimum number of actions and scales the number dynamically with the number of admins. The data is saved 
to a CSV file.

Parameters:
- admins (DataFrame): DataFrame containing admin data, used to assign actions to admins.
- output_filename (str): The name of the output CSV file (default: "admin_actions.csv").
- min_actions (int): The minimum number of admin actions to generate (default: 50).

Key Features:
- Assigns a set of random actions to each admin, ensuring at least `min_actions` total.
- Dynamically scales the number of actions based on the number of admins.
- Generates realistic action descriptions and timestamps.
- Saves the generated admin action data to a CSV file.

Returns:
- A pandas DataFrame containing the admin action data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_admin_action_table(admins, output_filename="admin_actions.csv", min_actions=50):
    try:
        if admins.empty:
            raise ValueError("Admins DataFrame is empty. Cannot populate AdminAction table.")
        if "AdminID" not in admins.columns:
            raise ValueError("Admins DataFrame must include an 'AdminID' column.")

        admin_actions = []
        action_id = 1  

        total_actions = max(min_actions, len(admins) * 10) 
        print(f"Generating at least {min_actions} actions for {len(admins)} admins...")

        actions_per_admin = total_actions // len(admins)
        remaining_actions = total_actions % len(admins)

        for _, admin in admins.iterrows():
            admin_id = admin["AdminID"]

            num_actions = actions_per_admin + (1 if remaining_actions > 0 else 0)
            if remaining_actions > 0:
                remaining_actions -= 1

            for _ in range(num_actions):
                action_description = random.choice([
                    "Updated user profile",
                    "Moderated a review",
                    "Deleted a comment",
                    "Resolved a user complaint",
                    "Banned a user",
                    "Approved new accommodation",
                    "Changed booking status",
                    "Reviewed system logs"
                ])
                action_date = fake.date_this_year().isoformat()

                admin_actions.append({
                    "ActionID": action_id,
                    "AdminID": admin_id,
                    "ActionDescription": action_description,
                    "ActionDate": action_date
                })
                action_id += 1

        df_admin_actions = pd.DataFrame(admin_actions)

        file_path = os.path.join(output_directory, output_filename)
        df_admin_actions.to_csv(file_path, index=False)
        print(f"AdminAction table successfully saved to: {file_path}")

        return df_admin_actions

    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["ActionID", "AdminID", "ActionDescription", "ActionDate"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["ActionID", "AdminID", "ActionDescription", "ActionDate"])


"""
Function: populate_transaction_table

Purpose:
Generates a dataset for a "transactions" table, recording financial transactions associated with payments. 
Each transaction includes details such as transaction date, type, amount, and payment method. The function 
ensures all transactions correspond to valid payments and saves the data to a CSV file.

Parameters:
- payments (DataFrame): DataFrame containing payment data, used to link transactions to payments.
- output_filename (str): The name of the output CSV file (default: "transactions.csv").
- total_transactions (int, optional): The total number of transactions to generate. If not specified, 
  defaults to the number of unique payments.

Key Features:
- Associates each transaction with a valid payment ID.
- Randomly generates transaction types (Credit/Debit) and payment methods.
- Ensures a sufficient number of transactions are generated, matching or exceeding the number of payments.
- Saves the generated transaction data to a CSV file.

Returns:
- A pandas DataFrame containing the transaction data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_transaction_table(payments, output_filename="transactions.csv", total_transactions=None):
    try:
        if payments.empty or "PaymentID" not in payments.columns:
            raise ValueError("Payments DataFrame must include a non-empty 'PaymentID' column.")

        total_transactions = total_transactions or len(payments)
        if total_transactions < len(payments):
            raise ValueError("Total transactions must be at least equal to the number of unique payments.")

        payment_methods = ['Credit Card', 'Debit Card', 'Bank Transfer', 'PayPal', 'Cryptocurrency']
        transactions = []
        transaction_id = 1

        print(f"Generating {total_transactions} transactions for {len(payments)} payments...")

        for _ in range(total_transactions):
            payment = payments.sample(1).iloc[0] 
            payment_id = payment["PaymentID"]
            transaction_date = fake.date_this_year().isoformat()
            transaction_type = random.choice(['Credit', 'Debit'])
            amount = round(payment["Amount"], 2)
            payment_method = random.choice(payment_methods)

            transactions.append({
                "TransactionID": transaction_id,
                "PaymentID": payment_id,
                "TransactionDate": transaction_date,
                "TransactionType": transaction_type,
                "Amount": amount,
                "PaymentMethod": payment_method
            })
            transaction_id += 1

        df_transactions = pd.DataFrame(transactions)

        missing_payments = set(df_transactions["PaymentID"]) - set(payments["PaymentID"])
        if missing_payments:
            raise ValueError(f"Transactions generated for non-existent PaymentIDs: {missing_payments}")

        file_path = os.path.join(output_directory, output_filename)
        df_transactions.to_csv(file_path, index=False)
        print(f"Transaction table successfully saved to: {file_path}")

        return df_transactions  

    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["TransactionID", "PaymentID", "TransactionDate", "TransactionType", "Amount", "PaymentMethod"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["TransactionID", "PaymentID", "TransactionDate", "TransactionType", "Amount", "PaymentMethod"])



"""
Function: populate_notification_table

Purpose:
Generates a dataset for a "notifications" table, creating notifications for users. Each notification includes 
a user ID, a notification message, and a timestamp. The function ensures a minimum number of notifications 
and scales the total based on the number of users. The data is saved to a CSV file.

Parameters:
- users (DataFrame): DataFrame containing user data, used to assign notifications to users.
- output_filename (str): The name of the output CSV file (default: "notifications.csv").
- min_notifications (int): The minimum number of notifications to generate (default: 20).

Key Features:
- Dynamically scales the total number of notifications based on the number of users.
- Distributes notifications evenly across users, ensuring fairness.
- Generates realistic notification messages and timestamps.
- Saves the generated notification data to a CSV file.

Returns:
- A pandas DataFrame containing the notification data.
- Returns an empty DataFrame with appropriate columns in case of validation or unexpected errors.
"""
def populate_notification_table(users, output_filename="notifications.csv", min_notifications=20):
    try:
        if users.empty or "UserID" not in users.columns:
            raise ValueError("Users DataFrame must include a non-empty 'UserID' column.")

        notifications = []

        user_count = len(users)
        if user_count == 0:
            raise ValueError("No users available to assign notifications.")

        total_notifications = max(min_notifications, user_count * 5)

        print(f"Generating at least {min_notifications} notifications, scaling to {total_notifications}.")

        notifications_per_user = total_notifications // user_count
        remaining_notifications = total_notifications % user_count

        for i, user in users.iterrows():
            user_notifications = notifications_per_user + (1 if i < remaining_notifications else 0)

            for _ in range(user_notifications):
                notification_message = fake.text()
                notification_date = fake.date_this_year().isoformat()

                notifications.append({
                    "UserID": user["UserID"],
                    "NotificationMessage": notification_message,
                    "NotificationDate": notification_date
                })

        df_notifications = pd.DataFrame(notifications)

        file_path = os.path.join(output_directory, output_filename)
        df_notifications.to_csv(file_path, index=False)
        print(f"Notification table successfully saved to: {file_path}")

        return df_notifications  

    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return pd.DataFrame(columns=["UserID", "NotificationMessage", "NotificationDate"])
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return pd.DataFrame(columns=["UserID", "NotificationMessage", "NotificationDate"])


"""
Function: validate_tables

Purpose:
Validates the integrity and consistency of the Users, Admins, and Accommodations tables. It checks for 
minimum entry counts, invalid references, and logical dependencies between the tables.

Parameters:
- users (DataFrame): DataFrame containing user data.
- admins (DataFrame): DataFrame containing admin data, linked to the Users table.
- accommodations (DataFrame): DataFrame containing accommodation data, linked to the Users table through hosts.

Key Features:
- Ensures the Users, Admins, and Accommodations tables each have at least 20 entries.
- Checks that all UserIDs in the Admins table exist in the Users table.
- Verifies that all HostIDs in the Accommodations table are valid hosts in the Users table.
- Returns a summary of issues if any validation checks fail.

Returns:
- A list of validation issues if errors are found.
- A success message if all tables and dependencies are validated successfully.
"""
def validate_tables(users, admins, accommodations):
    issues = []

    if len(users) < 20:
        issues.append("User table has fewer than 20 entries.")

    if len(admins) < 20:
        issues.append("Admin table has fewer than 20 entries.")
    invalid_admin_users = set(admins["UserID"]) - set(users["UserID"])
    if invalid_admin_users:
        issues.append(f"Admin table has UserIDs that do not exist in Users table: {invalid_admin_users}.")

    if len(accommodations) < 20:
        issues.append("Accommodation table has fewer than 20 entries.")
    invalid_accommodation_hosts = set(accommodations["HostID"]) - set(users[users["UserType"] == "host"]["UserID"])
    if invalid_accommodation_hosts:
        issues.append(f"Accommodation table has HostIDs that are not valid Hosts in Users table: {invalid_accommodation_hosts}.")

    if not issues:
        return "All tables and dependencies validated successfully."
    else:
        return issues
    

"""
Function: verify_data_integrity

Purpose:
Validates the integrity of relationships between users, accommodations, and bookings by checking:
1. All accommodations have valid hosts.
2. All bookings have valid guests.
3. All bookings reference valid accommodations.
4. Sufficient hosts exist for accommodations.
5. Sufficient guests exist for bookings.

Parameters:
- users (DataFrame): Contains user data with `UserID` and `UserType` (host/guest).
- accommodations (DataFrame): Contains accommodation data with `AccommodationID` and `HostID`.
- bookings (DataFrame): Contains booking data with `BookingID`, `GuestID`, and `AccommodationID`.

Output:
Prints validation results and highlights any errors or warnings in data consistency.
"""
def verify_data_integrity(users, accommodations, bookings):
    try:
        hosts = users[users["UserType"] == "host"]["UserID"].tolist()
        accommodations_hosts = accommodations["HostID"].tolist()
        invalid_hosts = [host for host in accommodations_hosts if host not in hosts]
        if invalid_hosts:
            print(f"Error: Accommodations have invalid hosts: {invalid_hosts}")
        else:
            print("All accommodations have valid hosts.")

        guests = users[users["UserType"] == "guest"]["UserID"].tolist()
        bookings_guests = bookings["GuestID"].tolist()
        invalid_guests = [guest for guest in bookings_guests if guest not in guests]
        if invalid_guests:
            print(f"Error: Bookings have invalid guests: {invalid_guests}")
        else:
            print("All bookings have valid guests.")

        accommodations_ids = accommodations["AccommodationID"].tolist()
        bookings_accommodations = bookings["AccommodationID"].tolist()
        invalid_accommodations = [
            acc for acc in bookings_accommodations if acc not in accommodations_ids
        ]
        if invalid_accommodations:
            print(f"Error: Bookings have invalid accommodations: {invalid_accommodations}")
        else:
            print("All bookings reference valid accommodations.")

        if len(accommodations) > len(hosts):
            print(f"Warning: More accommodations ({len(accommodations)}) than hosts ({len(hosts)}).")
        else:
            print("Hosts are sufficient for accommodations.")

        if len(bookings) > len(guests):
            print(f"Warning: More bookings ({len(bookings)}) than guests ({len(guests)}).")
        else:
            print("Guests are sufficient for bookings.")

        print("Data integrity verification complete.")
    except Exception as e:
        print(f"Error during verification: {e}")

"""
Function: main

Purpose:
Generates a complete dataset for a system that manages users, accommodations, bookings, and related entities.
The function sequentially calls specialized table-population functions to create and export data to CSV files 
for various entities, including users, accommodations, bookings, payments, and reviews. It also validates 
data integrity and ensures consistency across the generated datasets.

Outputs:
- Saves each generated dataset to a CSV file.
- Returns a dictionary (`data`) containing all generated datasets as DataFrames.
- Prints the status and results of data generation, validation, and consistency checks.

Use Case:
Useful for initializing a database or generating synthetic data for testing and development purposes.
"""
def main():
    data = {}

    print("Generating country data...")
    data["countries"] = populate_country_table(output_filename="countries.csv")

    print("Generating house rule data...")
    data["house_rules"] = populate_house_rule_table(output_filename="house_rules.csv")

    print("Generating amenity data...")
    data["amenities"] = populate_amenity_table(output_filename="amenities.csv")

    print("Generating city data...")
    data["cities"] = populate_city_table(data["countries"], output_filename="cities.csv")

    print("Generating user data...")
    data["users"] = populate_user_table(output_filename="users.csv")

    print("Generating accommodation data...")
    data["accommodations"] = populate_accommodation_table(data["users"], 
                                                          data["cities"], data["countries"], output_filename="accommodations.csv")

    print("Generating accommodation photos...")
    data["photos"] = populate_photo_table(data["accommodations"], output_filename="photos.csv")

    print("Generating accommodation-house rule mappings...")
    data["accommodation_house_rules"] = populate_accommodation_house_rule_table(
        data["accommodations"], data["house_rules"], output_filename="accommodation_house_rules.csv"
    )

    print("Generating accommodation-amenity mappings...")
    data["accommodation_amenities"] = populate_accommodation_amenity_table(
        data["accommodations"], data["amenities"], output_filename="accommodation_amenities.csv"
    )

    print("Generating booking data...")
    data["bookings"] = populate_booking_table(
        data["users"], data["accommodations"], output_filename="bookings.csv"
    )

    print("Generating payment data...")
    data["payments"] = populate_payment_table(data["bookings"], output_filename="payments.csv")

    print("Generating cancellation data...")
    data["cancellations"] = populate_cancellation_table(data["bookings"], output_filename="cancellations.csv")

    print("Generating availability data...")
    data["availability"] = populate_availability_table(
        data["accommodations"], data["bookings"], output_filename="availability.csv"
    )

    print("Generating price data...")
    data["prices"] = populate_price_table(data["accommodations"], output_filename="prices.csv")

    print("Generating social network data...")
    data["social_networks"] = populate_social_network_table(data["users"], output_filename="social_networks.csv")

    print("Generating profile data...")
    data["profiles"] = populate_profile_table(data["users"], output_filename="profiles.csv")

    print("Generating user messages...")
    data["messages"] = populate_message_table(data["users"], output_filename="messages.csv")

    print("Generating review data...")
    data["reviews"] = populate_review_table(
        data["accommodations"], data["bookings"], data["users"], output_filename="reviews.csv"
    )

    if not data["reviews"].empty:
        print("Generating host responses...")
        data["host_responses"] = populate_host_response_table(data["reviews"], output_filename="host_responses.csv")
    else:
        print("No reviews generated. Skipping host responses.")
        data["host_responses"] = pd.DataFrame()

    print("Generating commission data...")
    data["commissions"] = populate_commission_table(data["bookings"], output_filename="commissions.csv")

    print("Generating admin data...")
    data["admins"] = populate_admin_table(data["users"], output_filename="admins.csv")

    print("Generating admin actions...")
    data["admin_actions"] = populate_admin_action_table(data["admins"], output_filename="admin_actions.csv")

    print("Generating transaction data...")
    data["transactions"] = populate_transaction_table(data["payments"], output_filename="transactions.csv")

    print("Generating notifications...")
    data["notifications"] = populate_notification_table(data["users"], output_filename="notifications.csv")

    print("All data generation complete!")

    verify_data_integrity(data["users"], data["accommodations"], data["bookings"])

    print(f"Data Types Before Validation:")
    print(f"Users: {type(data['users'])}")
    print(f"Admins: {type(data['admins'])}")
    print(f"Accommodations: {type(data['accommodations'])}")

    print("Validating generated data...")
    validation_result = validate_tables(data["users"], data["admins"], data["accommodations"])
    if isinstance(validation_result, str):
        print(validation_result)
    else:
        print("Issues found during validation:")
        for issue in validation_result:
            print(f"- {issue}")

if __name__ == "__main__":
    main()