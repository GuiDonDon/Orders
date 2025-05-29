import os

def load(self):
    if os.path.isfile(self.source):
        self._load_from_file()
    elif self.source.startswith('http://') or self.source.startswith('https://'):
        self._load_from_url()
    else:
        raise FileNotFoundError(f"Source '{self.source}' not found as file and not recognized as valid URL.")
