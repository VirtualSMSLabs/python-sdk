import time

from virtualsms import VirtualSMSClient, ActivationStatus
from virtualsms.exceptions import VirtualSMSException

client = VirtualSMSClient("YOUR_API_KEY", "https://api.virtualsms.de")

try:
    print("=== Step 1: Check Balance ===")
    balance = client.get_balance()
    print(f"Balance: ${balance.balance:.2f}\n")

    print("=== Step 2: Check Prices ===")
    prices = client.get_prices("wa", 73)
    if "73" in prices and "wa" in prices["73"]:
        price = prices["73"]["wa"]
        print(f"WhatsApp in Brazil: ${price['cost']} ({price['count']} available)\n")

    print("=== Step 3: Order Number ===")
    number = client.get_number("wa", 73, max_price=2.00)
    print(f"Got number: {number.phone_number} (activation #{number.activation_id})\n")

    print("=== Step 4: Set Status Ready ===")
    client.set_status(number.activation_id, ActivationStatus.READY)
    print("Status set to READY (waiting for SMS)\n")

    print("=== Step 5: Poll for SMS Code ===")
    max_attempts = 30
    code = None
    for i in range(max_attempts):
        time.sleep(5)
        status = client.get_status(number.activation_id)
        print(f"Attempt {i + 1}: {status.status}")
        if status.code is not None:
            code = status.code
            break
        if status.status == "STATUS_CANCEL":
            print("Activation was cancelled.")
            exit(1)

    if code is not None:
        print(f"\n=== SMS Code Received: {code} ===\n")
        print("=== Step 6: Complete Activation ===")
        client.set_status(number.activation_id, ActivationStatus.COMPLETE)
        print("Activation completed.")
    else:
        print(f"\nNo SMS received after {max_attempts} attempts.")
        client.set_status(number.activation_id, ActivationStatus.CANCEL)
        print("Activation cancelled.")

except VirtualSMSException as e:
    print(f"Error: {e} (code: {e.error_code}, http: {e.http_status})")
    exit(1)
