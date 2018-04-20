import csv # library for reading and writing csv file
import paramiko # library for ssh
import os

OUTPUT_FILE = 'output.csv'

HOSTS_FILE = "hosts.txt"

PRIVATE_KEY_FILE = "key1"
NEW_PUBLIC_KEY_FILE = "key2.pub"

def sshRunCmd(ssh, cmd):
	stdin, stdout, stderr = ssh.exec_command(cmd)
	return stdout.readlines()[0].strip()

def doYourThing():
	try:
		os.remove(OUTPUT_FILE)
	except OSError:
		pass

	with open(HOSTS_FILE) as f:
		for line in f:
			hosts = line.split()
			uname = hosts[0]
			ip = hosts[1]
			
			# SSH into the host
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(ip, username=uname, key_filename=PRIVATE_KEY_FILE)
			
			# Get Host Name
			hostname = sshRunCmd(ssh, 'hostname')
			
			# Get Host IP Address
			getIPCmd = "ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'"
			hostip = sshRunCmd(ssh, getIPCmd)
			
			# Get authorized_key file's metadata
			getMetaDataCmd = 'stat --format=mtime=%y\|ctime=%z\|atime=%x ~/.ssh/authorized_keys'
			stats = sshRunCmd(ssh, getMetaDataCmd)
			
			# Change Key 
			sftp = ssh.open_sftp()
			path='/home/'+uname+'/.ssh/authorized_keys'
			sftp.put(NEW_PUBLIC_KEY_FILE, path)
			
			# Get the output of the authorized_key file after the update
			content = sshRunCmd(ssh, 'cat ' + path)
			
			#Output is generated in output.csv file
			with open(OUTPUT_FILE, 'a') as f1:
				writer=csv.writer(f1)
				writer.writerow([hostname,hostip,stats,content])
				
	return
			
if __name__ == "__main__":
	print "Working please wait ...."
	doYourThing()