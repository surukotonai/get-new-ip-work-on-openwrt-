import paramiko
import re  
import time 

hostname = '192.168.1.1' #ip
port = 22  #port
username = 'SSH USER NAME (default = root)'
password = 'SSH PASSWORD'
down_up_command = 'ifdown pppoe && ifup pppoe' 
ifconfig_command = 'ifconfig'


try:

    client = paramiko.SSHClient()

    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # SSH connet
    client.connect(hostname=hostname, port=port, username=username, password=password)


    stdin, stdout, stderr = client.exec_command(ifconfig_command)
    ifconfig_exit_status = stdout.channel.recv_exit_status()
    if ifconfig_exit_status != 0:
        print("ifconfig Error")
        print("-------------------")
        print(stderr.read().decode())
        print("-------------------")
        raise Exception("ifconfig Error x2")

    # decode 
    output = stdout.read().decode('utf-8', errors='ignore')
    output_lines_iterator = iter(output.splitlines()) 
    addr1 = None 
    for line in output_lines_iterator: 
        if line.strip().startswith('pppoe-pppoe'):

            try:
                next_line = next(output_lines_iterator) 
            except StopIteration:
                print("Error: pppoe-pppoe bad requests")
                continue # nt

            match = re.search(r'inet\s+addr:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', next_line)
            if match:
                addr1 = match.group(1)
                break

    if addr1:
        print("Fist addr (addr1):"+addr1)

    else:
        print("Faild Get Fist IP")
        addr1 = "IPGetFaild"



    print("Reconeting PPPoE")
    stdin, stdout, stderr = client.exec_command(down_up_command)

    down_up_exit_status = stdout.channel.recv_exit_status()
    if down_up_exit_status == 0:
        print("Success")

    else:
        print("Error")
 
        print(stderr.read().decode())


 
    print("Waiting for 5 seconds")
    time.sleep(5) 
    print("Done")



    stdin, stdout, stderr = client.exec_command(ifconfig_command)
    ifconfig_exit_status = stdout.channel.recv_exit_status()
    if ifconfig_exit_status != 0:
        print("ifconfig Error")
        print("-------------------")
        print(stderr.read().decode())
        print("-------------------")
        raise Exception("ifconfig Error x2") 


    output = stdout.read().decode('utf-8', errors='ignore')
    output_lines_iterator = iter(output.splitlines()) 
    addr2 = None 
    for line in output_lines_iterator: 
        if line.strip().startswith('pppoe-pppoe'):
         
            try:
                next_line = next(output_lines_iterator) 
            except StopIteration:
                print("Error: pppoe-pppoe bad requests")
                continue 

           
            match = re.search(r'inet\s+addr:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', next_line)
            if match:
                addr2 = match.group(1)
                break

    if addr2:
        print("new addr (addr2):"+addr2)
      
    else:
        print("Faild Get last IP")
        addr2 = "IPGetFaild" 
    print("--------- Done ----------")



    print(f"Old: {addr1}")
    print(f"New: {addr2}")
    if addr1 != "IPGetFaild" and addr2 != "IPGetFaild": 
        if addr1 == addr2:
            print("Nothing")
    else:
        print("Faild")


except paramiko.AuthenticationException:
    print("Faild SSH Auth")
except paramiko.SSHException as e:
    print(f"SSH Error: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if client:
        client.close()
