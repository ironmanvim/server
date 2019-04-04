#!/usr/bin/python

import socket
import time
import sys
import os
import threading
import xml.etree.ElementTree as ET
import subprocess


# check no further docs needed
class RunParallel(threading.Thread):
    """
    Run Processes in Parallel
    """

    def __init__(self, func, args=()):
        """
        :param func: Specify Function to run in Parallel
        :param args: Arguments to pass to the specified function
        """
        threading.Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        """
        :return: Get the specified Function to run in Parallel
        """
        self.func(*self.args)


def write_log(log_file: str, *args):

    logs = open(log_file, 'a')
    if write_log.count == 1:
        log_str = "\n" + "#"*100
        log_str += "\n\nServer Running Started at " + c_time() + "\n"
    else:
        log_str = ""
    log_str += "[" + str(write_log.count) + "]\n"
    write_log.count += 1
    log_str += "-"*100 + "\n"
    log_str += c_time()
    for i in args:
        log_str += str(i) + " "
    log_str += "\n" + "-"*100 + '\n'
    print(log_str)
    logs.write(log_str)
    logs.close()


write_log.count = 1


# check no further docs needed
class VHttpServer:
    """
    VHttp Server is a Python Http Server
    """

    # check no further docs needed
    def __init__(self, name: str, host: str='', port: int=80, working_dir: str='www'):
        """
        Initialize needed variables
        :param name: Name of the Server
        :param host: Host IP Address ('' - open on all hosts)
        :param port: Specify the port the server to listen (defaults to 80)
        :param working_dir: working directory
        """
        self.name = name
        self.socket = socket.socket()  # creating a socket
        self.host = host  # specify the host
        self.port = port  # port for server to listen
        self.www_dir = working_dir  # working folder

    # check no further docs needed
    def activate_server(self):
        """
        Activate the Server with the Specified Host and Port
        """
        self.log("activate_server is called")
        # noinspection PyBroadException
        try:
            self.log("Launching " + self.name + " HTTP server on '" + self.host + "': '" + str(self.port) + "'")
            self.socket.bind((self.host, self.port))  # bind the host with the given port
        except Exception:
            self.log("Warning: Could not acquire port: " + str(self.port))
            self.shutdown()  # shutdown the server if port not already in use
            sys.exit(1)

        self.log("Server successfully acquired the socket with port:" + str(self.port))
        self._wait_for_connections()

    # check no further docs needed
    def shutdown(self):
        """
        Shutdowns the Server
        """
        try:
            self.log("Shutting down the server " + self.name)
            self.socket.shutdown(socket.SHUT_RDWR)

        except Exception as e:
            self.log("Warning: could not shut down the socket. Maybe it was already closed!\n" + str(e))

    # check no further docs needed
    # noinspection PyMethodMayBeStatic
    def _gen_headers(self, code):
        """
        :param code: select the specified code (200 or 400)
        :return: Header for requested Header code
        """
        h = ''
        if code == 200:
            h = 'HTTP/1.1 200 OK\n'
        elif code == 404:
            h = 'HTTP/1.1 404 Not Found\n'

        current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        h += 'Date: ' + current_date + '\n'
        h += 'Server: Simple-Python-HTTP-Server\n'
        h += 'Connection: close\n\n'

        return h

    # check no further docs needed
    def _wait_for_connections(self):
        """
        Start Listening to the Clients
        """
        response_content = 0
        while True:
            self.log(self.name + " : Awaiting New connection")
            self.socket.listen(5)  # listening for new connections
            conn, address = self.socket.accept()  # accepting the new connection
            self.log("Connection Accepted for IP Address: [", address, "]")
            thread = RunParallel(self._decode, (response_content, conn, address))  # when connection succeed create a
            # parallel process
            thread.start()  # start the process

    # check no further docs needed
    def _decode(self, response_content, conn, address):
        """
        Get the connection and process the content
        :param response_content: The result
        :param conn: connection of the socket
        :param address: address of the client
        """

        data = conn.recv(1024)  # get the data from client
        string = bytes.decode(data)  # decode the data from the client
        local_parameters = {"address": address}
        request_method = string.split(' ')[0]  # response method is data before first space
        self.log(address, "\nMethod: ", request_method)
        self.log(address, "\nRequest body: ", string)
        local = iter(string.split('\r\n'))
        next(local)
        for i in local:
            try:
                x, y = list(map(str.strip, i.split(': ')))
                local_parameters[x] = y
            except ValueError:
                pass
        try:
            res = local_parameters['Host'].split(':')
            local_parameters['Host'] = res[0]
            local_parameters['Port'] = res[1]
        except IndexError:
            pass
        except KeyError:
            pass

        post_parameters = ""
        try:  # get post_parameters from the content
            temp = string.split('\r\n')
            if '' == temp[len(temp) - 2]:
                post_parameters = temp[len(temp) - 1]
            else:
                post_parameters = ""
        except IndexError:
            pass
        # try:
        #     res = b''
        #     file_length = int(local_parameters['Content-Length'])  # size of the files
        #
        #     # retrieving all files into res
        #     megabyte = 1024
        #     remote = 1
        #     while file_length > 0:
        #         if file_length > remote*megabyte:
        #             dat = conn.recv(remote*megabyte)
        #         else:
        #             dat = conn.recv(file_length)
        #         print(bytes.decode(dat, 'utf-8', 'replace'), end='')
        #         res = res + dat
        #         file_length -= remote*megabyte
        #
        #     # dividing files retrieved
        #     # spliter = local_parameters['Content-Type']
        #     # split_index = spliter.index('boundary=') + len('boundary=')
        #     # spliter = spliter[split_index:]
        #     # res = res.split(spliter.encode())
        #     # res = iter(res)
        #     # next(res)
        #     # for i in res:
        #     #     if i == b'--\r\n':
        #     #         break
        #     #     i = i.split(b'\r\n')
        #     #     filename = i[1].split(b';')[2].split(b'=')[1][1:-1]
        #     #     new_file = open("temp/" + filename.decode(), 'wb')
        #     #     data = b"\r\n".join(i[4:-1])
        #     #     new_file.write(data)
        #     #     print(filename)
        #
        # except KeyError:
        #     pass

        if (request_method == 'GET') | (request_method == 'HEAD') | (request_method == 'POST'):
            # accepted request method

            file_requested = string.split(' ')
            file_requested = file_requested[1]  # get the requested url
            if len(file_requested.split('?')) == 2:  # get get_parameters from the content
                get_parameters = file_requested.split('?')[1]
            else:
                get_parameters = ""
            file_requested = file_requested.split('?')[0]  # get the requested filename

            try:  # try to analyze the file requested
                if file_requested[len(file_requested) - 1] == '/':  # if no file requested add the index.vhtml file
                    file_requested += 'index.vhtml'
                file_requested = self.www_dir + file_requested

                file_handler = open(file_requested, 'rb')  # get requested file object

                # if file requested found
                self.log(address, "\nServing web page [", file_requested, "]")

                folder, file_name = os.path.split(file_requested)
                if request_method == 'GET' or request_method == 'POST':
                    response_content = file_handler.read()
                    if file_name.split('.')[1] == 'vhtml':  # if vhtml file, process the vhtml file else do nothing
                        response_content = self.process_content(response_content.decode('utf-8'),
                                                                get_parameters, post_parameters, local_parameters,
                                                                file_name)
                file_handler.close()

                response_headers = self._gen_headers(200)  # get 200 header on successful processing
            except IOError:  # if previously requested file not found, search for index.html file
                try:
                    file_requested = file_requested[:len(file_requested) - 6] + ".html"

                    file_handler = open(file_requested, 'rb')

                    # if file requested found
                    self.log(address, "\nServing web page [", file_requested, "]")

                    # folder, file_name = os.path.split(file_requested)
                    if request_method == 'GET' or request_method == 'POST':
                        response_content = file_handler.read()
                    file_handler.close()

                    response_headers = self._gen_headers(200)  # get 200 header on successful getting the file
                except IOError as e:  # if no requested file found return file not found error
                    self.log(address, "\nWarning, file not found. Serving response code 404\n", e)
                    response_headers = self._gen_headers(404)  # get 404 header on failure to fetch file

                    if request_method == 'GET' or request_method == 'POST':
                        response_content = b'''\
<html>
    <body>
        <h1>Error 404: File not found</h1>
        <p><b>V</b> HTTP server</p>
    </body>
</html>\
'''
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                result = str(exc_type) + fname + str(exc_tb.tb_lineno)
                self.log(address, "\nWarning, file found. Error in executing\n", e)
                response_headers = self._gen_headers(404)  # get ___ header on failure to execute the file
                if request_method == 'GET' or request_method == 'POST':
                    response_content = b'''\
<html>
    <body>
        <h1>Error in executing: File found</h1>
        <p>''' + str(type(e).__name__).encode() + ': '.encode() + str(e).encode() + b'''</p>
        <p>''' + result.encode() + b'''\
        <p><b>V</b> HTTP server</p>
    </body>
</html>\
'''
            finally:
                file_handler.close()

            server_response = response_headers.encode()  # append all the headers
            if request_method == 'GET' or request_method == 'POST':  # append all the content
                server_response += response_content

            conn.send(server_response)  # send the response to the client
            self.log(address, "\nClosing connection with client")

        else:  # rejected request method
            self.log(address, "\nUnknown HTTP request method:", request_method)
        conn.close()

    # check no further docs needed
    @staticmethod
    def process_content(content, get_params, post_params, local_params, file_name):
        """
        Process the Python Content in the content
        :param file_name:
        :param local_params: Local Parameters
        :param content: Processable Content
        :param get_params: Get Parameters
        :param post_params: Post Parameters
        """

        # making dictionaries of Get parameters and Post parameters
        from urllib import parse
        get_params, post_params = parse.unquote_plus(get_params), parse.unquote_plus(post_params)
        get_params, post_params = get_params.split('&'), post_params.split('&')

        # previous code
        temp = {}
        try:
            for i in get_params:
                key = i.split('=')[0]
                value = i.split('=')[1]
                if '[]' in key:
                    key = key.split('[]')[0]
                    if key in temp:
                        temp[key].append(value)
                    else:
                        temp[key] = [value]
                else:
                    temp[key] = value
        except IndexError:
            pass
        finally:
            get_params = temp

        # previous code
        temp = {}
        try:
            for i in post_params:
                key = i.split('=')[0]
                value = i.split('=')[1]
                if '[]' in key:
                    key = key.split('[]')[0]
                    if key in temp:
                        temp[key].append(value)
                    else:
                        temp[key] = [value]
                else:
                    temp[key] = value
        except IndexError:
            pass
        finally:
            post_params = temp

        # adding the parameters to decoding string
        decoded_string = "GET_PARAMS = " + str(get_params) + "\n"
        decoded_string += "POST_PARAMS = " + str(post_params) + "\n"
        decoded_string += "LOCAL_PARAMS = " + str(local_params) + "\n"

        # new code
        split = content.split('\r\n')
        result = []
        python_code = 0
        for i in split:
            if '<?' == i.strip():
                python_code = 1
            elif '?>' == i.strip():
                python_code = 0
            elif '<=' in i and '=>' in i:
                try:
                    while True:
                        start = i.index('<=')
                        end = i.index('=>')
                        normal_code1 = i[:start]
                        py_code = i[start + 2:end]
                        normal_code2 = i[end + 2:]
                        py_code = list(map(str.strip, py_code.split(' or ')))
                        print(py_code)
                        for j in py_code:
                            result.append("try {")
                            result.append("print('''" + normal_code1 + "''', " + j + ", sep='', end='')")
                            result.append("}")
                            result.append("except NameError {")
                        result.append("print('''" + normal_code1 + "''', sep='', end='')")
                        for _ in range(len(py_code)):
                            result.append('}')

                        i = normal_code2
                except ValueError:
                    result.append("print('''" + i + "''')")
            elif python_code == 0:
                result.append("print('''" + i + "''')")
            elif python_code == 1:
                result.append(i.strip())
        decoded_string += "\n".join(result)

        print("Decoded String: ")
        print(decoded_string)
        file = open("temp/" + file_name[:-6] + ".vpy", "w")
        file.write(decoded_string)
        file.close()
        output = execute(file_name[:-6])
        print(output)
        return output.encode()

    def log(self, *args):
        string = "[Server Name: " + self.name + "] [Port: " + str(self.port) + "]\n"
        write_log("logs/server.log", string, *args)


class VConfigException(Exception):
    def __init__(self, arg):
        self.error = arg

    def __str__(self):
        return self.error


class VConfigHandler:

    def __init__(self, config_file="vconfig.xml"):
        self.config_file = config_file
        self.tree = ET.parse(config_file)
        self.vconfig = self.tree.getroot()
        self.m_id = int(self.vconfig.find('m-id').text)
        self.ids = [int(x.attrib['id']) for x in self.vconfig.find('servers')]
        self.used_ports = [int(x.text) for x in self.vconfig.iter('port')]
        self.servers = []
        for i in self.vconfig.find('servers'):
            b = {'id': int(i.attrib['id'])}
            for j in i:
                b[j.tag] = j.text
                if j.tag == 'port':
                    b[j.tag] = int(j.text)
            self.servers.append(b)

    def show_servers(self):
        count = 0
        for i in self.servers:
            count += 1
            print("Server", count, ":")
            print("\tID:", i['id'])
            print("\tName:", i['name'])
            print("\tPort:", i['port'])
            print("\tWorking Folder:", i['work-folder'])

    def create_server(self, name, port, working_folder):
        if port in self.used_ports:
            raise VConfigException("Port Already Used")
        server = ET.Element('server')
        self.m_id += 1
        server.set('id', str(self.m_id))
        self.vconfig[0].text = str(self.m_id)
        name1 = ET.SubElement(server, 'name')
        name1.text = name
        port1 = ET.SubElement(server, 'port')
        self.used_ports.append(port)
        port1.text = str(port)
        working_folder1 = ET.SubElement(server, 'work-folder')
        working_folder1.text = working_folder

        self.vconfig[1].append(server)
        self.tree.write(self.config_file)

    def delete_server(self, identify):
        for i in self.vconfig.find('servers'):
            if int(i.attrib['id']) == identify:
                self.vconfig.find('servers').remove(i)
                self.tree.write(self.config_file)
                break
        else:
            raise VConfigException("Given ID not found")

    def edit_server(self, identify, change, value):
        not_control = ['name', 'port', 'work-folder']
        if change == 'port':
            if int(value) in self.used_ports:
                raise VConfigException("Port already used")
        if change not in not_control:
            raise VConfigException("uni dentified change attribute")
        for i in self.vconfig.find('servers'):
            if int(i.attrib['id']) == identify:
                for j in i:
                    if j.tag == change:
                        j.text = value
                        self.tree.write(self.config_file)
                        break
                break


def c_time():
    return time.strftime("[%m/%d/%Y, %H:%M:%S] ", time.localtime())


# check no further docs needed
def execute(file_name):
    """
    Execute the code and returns the output of executed
    """
    output = subprocess.Popen(["vpython.exe", "z:/server/temp/" + file_name + ".vpy"], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, shell=True)
    output.communicate()
    output = subprocess.Popen(["python.exe", "z:/server/temp/" + file_name + ".py"], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, shell=True)
    out, error = output.communicate()
    print(out.decode())
    return out.decode()
