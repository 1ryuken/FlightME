import csv
import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PassportIndexVisaScraper:
    def __init__(self):
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_files = {
            'full': os.path.join(script_dir, 'data', 'passport-index-tidy.csv'),
            'iso2': os.path.join(script_dir, 'data', 'passport-index-tidy-iso2.csv')
        }
        logger.info(f"Data files initialized: {self.data_files}")

    def fetch(self, nationality, destination, code_type='full'):
        """
        Fetch visa requirements between two countries.
        Parameters:
            nationality (str): Full country name (default) or ISO 2-letter code.
            destination (str): Full country name (default) or ISO 2-letter code.
            code_type (str): 'full' for full country names (default), 'iso2' for ISO codes.
        """
        data_file = self.data_files.get(code_type)
        if not data_file or not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file {data_file} not found.")

        nationality = nationality.strip()
        destination = destination.strip()
        logger.info(f"Searching for visa requirements from {nationality} to {destination}")

        with open(data_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # First, verify these countries exist in our dataset
            countries = set()
            passports = set()
            destinations = set()
            csvfile.seek(0)
            next(reader)  # Skip header
            for row in reader:
                countries.add(row['Passport'])
                countries.add(row['Destination'])
                passports.add(row['Passport'])
                destinations.add(row['Destination'])
            
            logger.info(f"Found {len(passports)} passport countries and {len(destinations)} destination countries")
            
            if nationality not in passports:
                logger.error(f"Nationality '{nationality}' not found in dataset")
                similar = [c for c in passports if nationality.lower() in c.lower()]
                if similar:
                    raise ValueError(f"Nationality '{nationality}' not found. Did you mean one of these? {similar}")
                raise ValueError(f"Nationality '{nationality}' not found. Available passports include: {sorted(list(passports))[:5]}...")
            
            if destination not in destinations:
                logger.error(f"Destination '{destination}' not found in dataset")
                similar = [c for c in destinations if destination.lower() in c.lower()]
                if similar:
                    raise ValueError(f"Destination '{destination}' not found. Did you mean one of these? {similar}")
                raise ValueError(f"Destination '{destination}' not found. Available destinations include: {sorted(list(destinations))[:5]}...")
            
            # Reset file pointer and skip header
            csvfile.seek(0)
            next(reader)
            
            # Search for the specific combination
            found_nationality = False
            found_destination = False
            for row in reader:
                if row['Passport'] == nationality:
                    found_nationality = True
                    if row['Destination'] == destination:
                        found_destination = True
                        result = {
                            "nationality": nationality,
                            "destination": destination,
                            "visa_requirement": row['Requirement']
                        }
                        logger.info(f"Found match: {result}")
                        self._save_to_json(result)
                        return result

            if not found_nationality:
                logger.error(f"No entries found for nationality: {nationality}")
            elif not found_destination:
                logger.error(f"Found entries for {nationality} but none for destination: {destination}")
                # Let's find what destinations are available for this nationality
                csvfile.seek(0)
                next(reader)
                available_destinations = set()
                for row in reader:
                    if row['Passport'] == nationality:
                        available_destinations.add(row['Destination'])
                if available_destinations:
                    raise ValueError(f"Destination '{destination}' not found for {nationality}. Available destinations include: {sorted(list(available_destinations))[:5]}...")
            
        raise ValueError(f"No visa requirement data found for {nationality} to {destination}.")

    def _save_to_json(self, data, filename="visa_data.json"):
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(script_dir, "db", filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            with open(path, "r+", encoding="utf-8") as f:
                content = json.load(f)
                content.append(data)
                f.seek(0)
                json.dump(content, f, indent=2)
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump([data], f, indent=2) 