"""
ReadAGPT main
Using the menu select which test to run
"""
from tools.login_checker import LoginChecker

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

def main():
    options_open = [1]
    tools_names = ["Login Checker"]
    tools = [LoginChecker().run()]

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

    


if __name__ == "__main__":
    

    main()