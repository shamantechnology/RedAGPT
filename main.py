"""
ReadAGPT main
Using the menu select which test to run
"""
from dotenv import load_dotenv
import validators
import multiprocessing
import sys

from tools.login_checker import LoginChecker
from tools.wifi import WIFI

class textformat:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

log_dict = {
    "lfp": None
}

def main():
    load_dotenv()

    options_open = [1,2]

    print(
        f"{textformat.RED}%%-------------------------------------------%%{textformat.END}",
        f"\n{textformat.RED}%%-------%% RED AutoGPT Tool v0.1 %%---------%%{textformat.END}",
        f"\n{textformat.RED}%%-------------------------------------------%%{textformat.END}",
        "\nSelect which tool to run by number",
        "\n\n[1] Login Test",
        "\n\n[2] WIFI",
        "\n"
    )

    number_choice = 0

    while True:
        choice = input("")
        try:
            number_choice = int(choice)
            if number_choice in options_open:
                break
            else:
                print(f"{choice} is not a choice, please try again")
        except ValueError:
            print(f"{choice} is not a choice, please try again")

    # login Checker
    if number_choice == 1:
        while True:
            http_type = input("\nLocal or Remote\n")
            if http_type == "Local":
                break
            elif http_type == "Remote":
                print(f"\n{textformat.RED}REMOTE SHOULD ONLY BE DONE ON IPs YOU OWN{textformat.END}")
                break
            else:
                print("Please enter \"Local\" or \"Remote\", without the quotes, to answer")

        while True:
            http_url = input("\nEnter the url of the form to test\n")
            if validators.url(http_url):
                break
            else:
                print(f"{http_url} is not a valid URL. Try again")

        lgcheck = LoginChecker(http_url)
        process = multiprocessing.Process(target=lgcheck.run())
        process.start()
        process.join()

        # check if process is still alive
        while process.is_alive:
            process.join()
            if process.exitcode is not None:
                break
        
        print("Running \"Login Checker\" Tool...\n")
        # set sysout back to console
        sys.stdout = sys.__stdout__

        print("Tool \"Login Checker\" completed run")
        print(f"\n{textformat.YELLOW}[AI]{textformat.END} {lgcheck.autogpt_resp}")

    # WIFI
    elif number_choice == 2:
        wifi_obj = WIFI()
        process = multiprocessing.Process(target=wifi_obj.run())

        ## bad code repeat need to make this a function
        # it is for logging the stdout again
        process.start()
        process.join()

        # check if process is still alive
        while process.is_alive:
            process.join()
            if process.exitcode is not None:
                break
        
        print("Running \"WIFI\" Tool...\n")
        # set sysout back to console
        sys.stdout = sys.__stdout__

        # end
        print("Tool \"WIFI\" completed run")
        print(f"\n{textformat.YELLOW}[AI]{textformat.END} {wifi_obj.autogpt_resp}")

if __name__ == "__main__":
    main()