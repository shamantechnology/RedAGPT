"""
ReadAGPT main
Using the menu select which test to run
"""
from dotenv import load_dotenv
import validators
from tools.login_checker import LoginChecker
import multiprocessing
import time
import os
from datetime import datetime
import pprint

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

    options_open = [1]

    print(
        f"{textformat.RED}%%-------------------------------------------%%{textformat.END}",
        f"\n{textformat.RED}%%-------%% RED AutoGPT Tool v0.1 %%---------%%{textformat.END}",
        f"\n{textformat.RED}%%-------------------------------------------%%{textformat.END}",
        "\nSelect which tool to run by number",
        "\n\n[1] Login Test",
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

        seek_pos = None
        while process.is_alive:
            if os.path.exists(lgcheck.logging_file_path):
                with open(lgcheck.logging_file_path, "r") as runtxt:
                    if seek_pos:
                        runtxt.seek(seek_pos)

                    log_lines = runtxt.readlines()
                    if len(log_lines) > 0:
                        log_line = ''.join(log_lines).replace('\n', '')
                        pprint.pprint(f"log_line: {log_line}")
                    
                    seek_pos = runtxt.tell()
                    print("sleep 10")
                    time.sleep(10)

            process.join()
            if process.exitcode is not None:
                break
        
        print("Tool completed run")
        print(lgcheck.autogpt_resp)
        

        

if __name__ == "__main__":
    main()