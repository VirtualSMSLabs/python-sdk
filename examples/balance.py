from virtualsms import VirtualSMSClient
from virtualsms.exceptions import VirtualSMSException

client = VirtualSMSClient("YOUR_API_KEY", "https://api.virtualsms.de")

try:
    balance = client.get_balance()
    print(f"Current balance: ${balance.balance:.2f}")
except VirtualSMSException as e:
    print(f"Error: {e} (code: {e.error_code})")
