import csv
import json
import os

class PassportIndexVisaScraper:
    def __init__(self):
        self.data_files = {
            'iso2': 'data/passport-index-tidy-iso2.csv',
            'full': 'data/passport-index-tidy.csv'
        }

    def fetch(self, nationality, destination, code_type='iso2'):
        """
        Fetch visa requirements between two countries.
        Parameters:
            nationality (str): ISO 2-letter code or full country name.
            destination (str): ISO 2-letter code or full country name.
            code_type (str): 'iso2' for ISO codes, 'full' for full country names.
        """
        data_file = self.data_files.get(code_type)
        if not data_file or not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file {data_file} not found.")

        with open(data_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['passport'].strip().lower() == nationality.strip().lower() and \
                   row['destination'].strip().lower() == destination.strip().lower():
                    result = {
                        "nationality": nationality,
                        "destination": destination,
                        "visa_requirement": row['requirement']
                    }
                    self._save_to_json(result)
                    return result

        raise ValueError(f"No visa requirement data found for {nationality} to {destination}.")

    def _save_to_json(self, data, filename="visa_data.json"):
        path = os.path.join("db", filename)
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
