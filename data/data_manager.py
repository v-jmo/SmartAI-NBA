# ============================================================
# FILE: data/data_manager.py
# PURPOSE: Load, save, and manage all CSV data files for the app.
#          Handles player stats, prop lines, and team data.
# CONNECTS TO: All pages use this to load data
# CONCEPTS COVERED: CSV reading/writing, file paths, caching
# ============================================================

# Standard library imports only
import csv        # Built-in CSV reader/writer
import os         # File path operations
import json       # For session state persistence
from pathlib import Path  # Modern file path handling


# ============================================================
# SECTION: File Path Constants
# Define paths to all data files relative to the project root.
# Using pathlib.Path makes this work on Windows, Mac, and Linux.
# ============================================================

# Get the directory where this file lives (the 'data' folder)
DATA_DIRECTORY = Path(__file__).parent

# Build full paths to each CSV file
PLAYERS_CSV_PATH = DATA_DIRECTORY / "sample_players.csv"
PROPS_CSV_PATH = DATA_DIRECTORY / "sample_props.csv"
TEAMS_CSV_PATH = DATA_DIRECTORY / "teams.csv"
DEFENSIVE_RATINGS_CSV_PATH = DATA_DIRECTORY / "defensive_ratings.csv"

# ============================================================
# END SECTION: File Path Constants
# ============================================================


# ============================================================
# SECTION: CSV Loading Functions
# ============================================================

def load_players_data():
    """
    Load all player data from the sample_players.csv file.

    Returns a list of dictionaries, where each dictionary
    represents one player with all their stats as keys.

    Returns:
        list of dict: Player rows, e.g.:
            [{'name': 'LeBron James', 'team': 'LAL', ...}, ...]

    Example:
        players = load_players_data()
        lebron = players[0]
        print(lebron['points_avg'])  # → '24.8'
    """
    return _load_csv_file(PLAYERS_CSV_PATH)


def load_props_data():
    """
    Load all prop lines from the sample_props.csv file.

    Returns:
        list of dict: Prop rows, e.g.:
            [{'player_name': 'LeBron James', 'stat_type': 'points',
              'line': '24.5', 'platform': 'PrizePicks', ...}, ...]
    """
    return _load_csv_file(PROPS_CSV_PATH)


def load_teams_data():
    """
    Load all 30 NBA teams from teams.csv.

    Returns:
        list of dict: Team rows with pace, ortg, drtg, etc.
    """
    return _load_csv_file(TEAMS_CSV_PATH)


def load_defensive_ratings_data():
    """
    Load team defensive ratings by position from defensive_ratings.csv.

    Returns:
        list of dict: Defensive rating rows with vs_PG_pts, etc.
    """
    return _load_csv_file(DEFENSIVE_RATINGS_CSV_PATH)


def _load_csv_file(file_path):
    """
    Internal helper: load any CSV file and return list of dicts.

    Each row becomes a dictionary mapping column name → value.
    CSV headers become the dictionary keys.

    Args:
        file_path (Path or str): Path to the CSV file

    Returns:
        list of dict: Rows as dictionaries, or empty list if error
    """
    # Convert to Path object if it's a string
    file_path = Path(file_path)

    # Check if the file exists before trying to open it
    if not file_path.exists():
        # Return empty list instead of crashing
        return []

    rows = []  # Will hold all the row dictionaries

    try:
        # Open the file for reading
        # encoding='utf-8' handles special characters
        # newline='' is required by Python's csv module
        with open(file_path, encoding="utf-8", newline="") as csv_file:
            # DictReader automatically uses the first row as column names
            # BEGINNER NOTE: csv.DictReader is like a spreadsheet reader —
            # it maps each row's values to its column header names
            reader = csv.DictReader(csv_file)

            for row in reader:
                # Strip whitespace from all values
                # BEGINNER NOTE: dict comprehension builds a new dict
                # by looping over key-value pairs and stripping spaces
                cleaned_row = {
                    key.strip(): value.strip()
                    for key, value in row.items()
                    if key is not None  # Skip None keys (empty columns)
                }
                rows.append(cleaned_row)

    except Exception as error:
        # If anything goes wrong, return empty list
        # The app will show a message asking user to check the file
        print(f"Error loading {file_path}: {error}")
        return []

    return rows


# ============================================================
# END SECTION: CSV Loading Functions
# ============================================================


# ============================================================
# SECTION: Player Lookup Functions
# ============================================================

def find_player_by_name(players_list, player_name):
    """
    Find a player by their name in the players list.

    Args:
        players_list (list of dict): Loaded player data
        player_name (str): Player name to search for

    Returns:
        dict or None: Player data dict, or None if not found

    Example:
        player = find_player_by_name(players, "LeBron James")
        print(player['points_avg'])  # → '24.8'
    """
    # Search through all players for a name match
    # Use lower() for case-insensitive comparison
    player_name_lower = player_name.lower().strip()

    for player in players_list:
        stored_name = player.get("name", "").lower().strip()
        if stored_name == player_name_lower:
            return player

    # Also try partial match if exact match not found
    for player in players_list:
        stored_name = player.get("name", "").lower().strip()
        if player_name_lower in stored_name or stored_name in player_name_lower:
            return player

    return None  # Player not found


def get_all_player_names(players_list):
    """
    Get a sorted list of all player names.

    Args:
        players_list (list of dict): Loaded player data

    Returns:
        list of str: Sorted player names

    Example:
        names = get_all_player_names(players)
        # → ['Anthony Davis', 'Bam Adebayo', ...]
    """
    # Extract the 'name' field from each player dictionary
    # BEGINNER NOTE: List comprehension = compact way to build a list
    names = [player.get("name", "") for player in players_list if player.get("name")]
    return sorted(names)  # Sort alphabetically


def get_all_team_abbreviations(teams_list):
    """
    Get all 30 NBA team abbreviations.

    Args:
        teams_list (list of dict): Loaded teams data

    Returns:
        list of str: Team abbreviations like ['ATL', 'BOS', ...]
    """
    abbreviations = [
        team.get("abbreviation", "") for team in teams_list
        if team.get("abbreviation")
    ]
    return sorted(abbreviations)


def get_team_by_abbreviation(teams_list, abbreviation):
    """
    Find a team by its abbreviation (e.g., 'LAL', 'BOS').

    Args:
        teams_list (list of dict): Loaded teams data
        abbreviation (str): 3-letter team code

    Returns:
        dict or None: Team data, or None if not found
    """
    for team in teams_list:
        if team.get("abbreviation", "").upper() == abbreviation.upper():
            return team
    return None

# ============================================================
# END SECTION: Player Lookup Functions
# ============================================================


# ============================================================
# SECTION: Props Management
# ============================================================

def save_props_to_session(props_list, session_state):
    """
    Save a list of props to Streamlit's session state.

    Streamlit session state persists data between page interactions.
    This lets us keep the prop list as the user navigates pages.

    Args:
        props_list (list of dict): The props to save
        session_state: Streamlit's st.session_state object
    """
    # Store the list under a known key in session state
    session_state["current_props"] = props_list


def load_props_from_session(session_state):
    """
    Load props from Streamlit's session state.

    Returns sample props if no props have been entered yet,
    so the user sees something immediately.

    Args:
        session_state: Streamlit's st.session_state object

    Returns:
        list of dict: Current props (entered or sample)
    """
    # Check if user has entered their own props
    if "current_props" in session_state and session_state["current_props"]:
        return session_state["current_props"]

    # Fall back to sample props from the CSV
    return load_props_data()


def parse_props_from_csv_text(csv_text):
    """
    Parse prop lines from CSV text (uploaded by user).

    Handles files uploaded via Streamlit's file uploader.
    Expected columns: player_name, team, stat_type, line, platform

    Args:
        csv_text (str): Raw CSV text content

    Returns:
        tuple: (list of valid prop dicts, list of error messages)

    Example:
        text = "LeBron James,LAL,points,24.5,PrizePicks"
        props, errors = parse_props_from_csv_text(text)
    """
    parsed_props = []   # Successfully parsed props
    error_messages = []  # Any parsing errors

    # Required columns that must be present
    required_columns = {"player_name", "stat_type", "line", "platform"}

    try:
        # Use csv.DictReader to parse the text
        # io.StringIO lets us treat a string as a file
        import io
        reader = csv.DictReader(io.StringIO(csv_text))

        for row_number, row in enumerate(reader, start=2):  # Start at 2 (row 1 = header)
            # Check that required columns are present
            row_lower = {k.lower().strip(): v.strip() for k, v in row.items()}

            missing_columns = required_columns - set(row_lower.keys())
            if missing_columns:
                error_messages.append(
                    f"Row {row_number}: Missing columns: {missing_columns}"
                )
                continue

            # Validate the line value is a number
            try:
                line_value = float(row_lower["line"])
            except ValueError:
                error_messages.append(
                    f"Row {row_number}: 'line' must be a number, got '{row_lower['line']}'"
                )
                continue

            # Build a clean prop dictionary
            prop = {
                "player_name": row_lower.get("player_name", ""),
                "team": row_lower.get("team", ""),
                "stat_type": row_lower.get("stat_type", "points").lower(),
                "line": line_value,
                "platform": row_lower.get("platform", "PrizePicks"),
                "game_date": row_lower.get("game_date", ""),
            }
            parsed_props.append(prop)

    except Exception as error:
        error_messages.append(f"CSV parsing error: {error}")

    return parsed_props, error_messages


def get_csv_template():
    """
    Return a CSV template string for users to download.

    Returns:
        str: CSV content with headers and one example row
    """
    # Template with headers and one example row
    template_lines = [
        "player_name,team,stat_type,line,platform,game_date",
        "LeBron James,LAL,points,24.5,PrizePicks,2026-03-05",
        "Stephen Curry,GSW,threes,3.5,Underdog,2026-03-05",
    ]
    return "\n".join(template_lines)

# ============================================================
# END SECTION: Props Management
# ============================================================
