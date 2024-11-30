from langchain.tools import tool
from dateutil import parser
import re

# BookAppointment Tool
@tool("BookAppointment", return_direct=True)
def book_appointment_tool(date_hint: str) -> str:
    """
    Parses a natural language date hint and converts it to YYYY-MM-DD format.
    If parsing succeeds, books an appointment (database update commented).

    Args:
        date_hint (str): A natural language date description (e.g., "next Friday", "tomorrow").

    Returns:
        str: Confirmation message with the formatted date or an error message if parsing fails.

    Example:
        Input: "next Friday"
        Output: "Your appointment has been successfully scheduled for 2024-11-29."

        Input: "invalid date"
        Output: "I couldn't understand the date hint 'invalid date'. Please provide a specific date."
    """
    try:
        # Parse the natural language date
        parsed_date = parser.parse(date_hint, fuzzy=True)
        
        # Format to YYYY-MM-DD
        formatted_date = parsed_date.strftime("%Y-%m-%d")
        
        # Database update logic (commented out)
        # db_connection = sqlite3.connect("appointments.db")
        # cursor = db_connection.cursor()
        # cursor.execute("INSERT INTO appointments (appointment_date) VALUES (?)", (formatted_date,))
        # db_connection.commit()
        # db_connection.close()
        
        return f"Your appointment has been successfully scheduled for {formatted_date}."
    except Exception as e:
        return f"Failed to parse the date hint '{date_hint}'. Please try again with a more specific date."


# Email Validation Tool
@tool("ValidateEmail", return_direct=True)
def validate_email_tool(email: str) -> str:
    """
    Validates the format of an email address.

    Args:
        email (str): The email address provided by the user.

    Returns:
        str: "valid" if the email is in the correct format, "invalid" otherwise.

    Example:
        Input: "john.doe@example.com"
        Output: "valid"

        Input: "invalid-email"
        Output: "invalid"
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(pattern, email):
        return "valid"
    else:
        return "invalid"

# Phone Number Validation Tool
@tool("ValidatePhone", return_direct=True)
def validate_phone_tool(phone: str) -> str:
    """
    Validates the format of a phone number.

    Args:
        phone (str): The phone number provided by the user.

    Returns:
        str: "valid" if the phone number matches the expected format, "invalid" otherwise.

    Example:
        Input: "+123-456-7890"
        Output: "valid"

        Input: "12345"
        Output: "invalid"
    """
    pattern = r"^\+?[0-9\s()-]{7,15}$"
    if re.match(pattern, phone):
        return "valid"
    else:
        return "invalid"