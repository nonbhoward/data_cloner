# Test objects in the google drive cloner module

# imports, project
from src.cloners.google_drive_cloner import GoogleDriveCloner


def test_google_drive_cloner():
    gdc = GoogleDriveCloner()
    assert gdc, f"Class {gdc.__class__.__name__} failed to initialize"
