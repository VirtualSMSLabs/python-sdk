from virtualsms import VirtualSMSClient
from virtualsms.exceptions import (
    InsufficientBalanceException,
    NoNumbersException,
    VirtualSMSException,
)

client = VirtualSMSClient("YOUR_API_KEY", "https://api.virtualsms.de")

try:
    number = client.get_number("wa", 73, max_price=2.00)
    print(f"Activation ID: {number.activation_id}")
    print(f"Phone Number: {number.phone_number}")
except InsufficientBalanceException:
    print("Not enough balance.")
except NoNumbersException:
    print("No numbers available.")
except VirtualSMSException as e:
    print(f"Error: {e}")
