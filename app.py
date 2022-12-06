# pylint: disable=no-member
"""Simple python lightning switch"""
from time import sleep

import os
import sys
import requests
import RPi.GPIO as GPIO


LNBITS_URL = "<YOUR_LNBITS_URL>/api/v1/wallet"
INVOICE_KEY = "<YOUR_INVOICE_KEY>"
PRICE = 1000

def setup_pins():
    """Initialises the trigger pin"""
   # Defining GPIO BCM Mode
    GPIO.setmode(GPIO.BCM)

    # Setup GPIO Pin for Relais
    GPIO.setwarnings(False)
    GPIO.setup(13, GPIO.IN)


def activate_pin():
    """Activate pin"""
    print("activate")
    GPIO.setup(13, GPIO.OUT)
    GPIO.output(13, GPIO.HIGH)


def deactivate_pin():
    """Deactivate pin"""
    print("deactivate")
    GPIO.setup(13, GPIO.IN)


def get_balance():
    """Returns a dict with balance"""
    url = LNBITS_URL
    headers = {
            "X-Api-Key": INVOICE_KEY
    }
    response = requests.request("GET", url, headers=headers).json()
    balance = response["balance"]
    return balance


def was_payed(balance, old_balance):
    """Check if a payment occured"""
    #global OLD_BALANCE
    if old_balance + PRICE >= balance:
        return False
    return True


def main():
    """Main method"""
    setup_pins()
    old_balance = get_balance()
    balance = old_balance

    while True:
        try:
            balance = get_balance()
        except Exception as error:
            raise Exception(f"get_balance failed with: {error}") from error
        if was_payed(balance, old_balance):
            activate_pin()
            sleep(1)
            deactivate_pin()
            old_balance = balance
            print("payed")
        else:
            print("nope")
        sleep(2)

if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            GPIO.cleanup()
            sys.exit("Manually Interrupted")
        except Exception:
            GPIO.cleanup()
            os.execv("/home/pi/repos/candygrabber/app.py", [""])
