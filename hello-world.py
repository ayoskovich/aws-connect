import requests
ip = requests.get('http://ifconfig.me').content
print(f'my ip is: {ip}')
