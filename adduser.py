import getpass
import hashlib

def hash(target):
	return hashlib.md5(target.encode('utf-8')).hexdigest()

print("Rahmish Imperial User Management\nAdd User")
username = input("User: ")
password = hash(getpass.getpass("Password: ") + username)

print("%s added with password hash %s"%(username,password))

with open('users.csv','a') as users:
	users.write('\n%s,%s'%(username,password))
