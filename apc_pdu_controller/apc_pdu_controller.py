import paramiko
import re
from collections import namedtuple

APC_SHELL_PROMPT = 'apc>'
SUCCESS = 'Success'

Connection = namedtuple('Connection', 'host user psw')
Response = namedtuple('Response', 'output result')    


class SSH(object):
    """ SSH Connection Object
    Defines a ssh client to be used by other applications
    
    ssh connection is closed in destructor

	input(s):
		Connection Object defined by namedtuple('Connection', 'host user psw')
    """

    def __init__(self, conn):
        self._connection = paramiko.SSHClient()
        self._connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._connection.connect(conn.host, 
				 username=conn.user,
				 password=conn.psw,
				 port=22,
				 look_for_keys=False)
        channel = self._connection.invoke_shell()
        self.stdin = channel.makefile('wb')
        self.stdout = channel.makefile('r')

    def __del__(self):
        self._connection.close()


class APCBase(object):
    """ Defines Base functionality for APC PDU
	input(s):
		Connection Object defined by namedtuple('Connection', 'host user psw')
	"""

    def __init__(self, conn):
        self.ssh = SSH(conn)
    
    def execute(self, cmd):
        """ Execute a command on the PDU using SSH 
        input(s):
            cmd (str): Command to send to the PDU
        output(s):
            Response(namedtuple): Response object contains stdout and result members
                where stdout is raw output from the command and 
                result is a boolean of whether the command returned succesful
        """

        cmd = cmd.strip('\n')
        self.ssh.stdin.write(cmd + '\r\n')  # send command to PDU
        self.ssh.stdin.flush()
        
        return self._get_output(cmd)
        
        
    def _get_output(self, cmd):
        """ Collect output from STDOUT and identify the result
        input(s):
            cmd (str): Command to sent to the PDU
        output(s):
            Response(namedtuple): Response object contains stdout and result members
                where stdout is raw output from the command and 
                result is a boolean of whether the command returned succesful
        """

        stdout = []
        start_reading = False
        result = False

        for line in self.ssh.stdout:  # read response from PDU
            if line.startswith(APC_SHELL_PROMPT + cmd):  # start collecting output once cmd is in stdout
                start_reading = True
            
            if start_reading:
                stdout.append(line)  # append output

                if 'E000' in line:
                    result = self._get_result(line)  # get the result of the command sent 

                if line == '\r\n':  # break loop if we reach a line break ... hangs without this logic
                    break

        return Response(stdout, result)  # return a Response namedtuple

    def _get_result(self, line):
        """ Checks that output for a command is succesful 
        input(s):
            line(str): line from stdout that contains result
        output(s)
        """
        try:
            return line.split(':')[1].strip() == SUCCESS
        except:
            return False


class APCController(APCBase):
    """Common commands for PDU Control"""

    def on(self, outlet):
        return self.execute('olOn %s' %(outlet,))
    
    def off(self, outlet):
        return self.execute('olOff %s' %(outlet,))
    
    def reboot(self, outlet):
        return self.execute('olReboot %s' %(outlet,))

    def dlyreboot(self, outlet):
        return self.execute('olDlyReboot %s' %(outlet,))

    def set_reboot_delay(self, outlet, delay):
        return self.execute('olRbootTime %s %s' %(outlet, delay))

    def status(self, outlet):
        return self.execute('olStatus %s' %(outlet,))


if __name__ == "__main__":
	apc_connection = Connection(host='localhost', user='user', psw='psw')  # create a connection namedtuple
	apc_pdu = APCController(apc_connection)  # pass connection details into APCController
	response = apc_pdu.reboot(1)  # Have fun and reboot outlet 1 on your PDU
	print(''.join(response.output))  # print output if you want 
