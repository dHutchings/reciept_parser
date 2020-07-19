import argparse

from os import listdir
from os.path import isfile, join

import re

import warnings

def list_filenames(folder_location):
	return listdir(folder_location)

import csv







if __name__ == "__main__":
	print("Welcome to Doug's overintelligent file parser!")
	""" Creating the argparse """
	parser = argparse.ArgumentParser(description = 'Location of a folder to generate list csv formmated files.  \n\r Generates a CSV that can by copied-pasted into the expenses spreadsheet.  \n\r Files are supposed to be named like: "[2018.06.04] CompanyNameOneWord Purchase Description $XX.YY"')
	parser.add_argument("folder_location", type = str, help = 'set the input folder location' )
	parser.add_argument("out", type = str, help = 'set the output CSV name / location')
	parsed = parser.parse_args()

	print(parsed)
	#print(str(parsed.in))
	
	all_files = list_filenames(parsed.folder_location)
	
	
	myfile = open('myfile.csv','wb')
	wrtr = csv.writer(myfile,delimiter=',', quotechar='"')
	
	reciepts = []
	
	dates_search= re.compile("\[\d\d\d\d\-\d\d\-\d\d\]")
	cost_search = re.compile("\$\d*.\d\d\.")
	
	spaces_search = re.compile("\ ")
	
	for f in all_files:
		print(f)
		results = dates_search.search(f)
		if results is None:
			warnings.warn("Filename is not formatted correctly (No Date):" + str(f))
			continue
		date = results.group()[1:-1]
		date = date.replace(".","/") #replace dots with slashes to keep sheets happy
		print(date)
		
		results = cost_search.search(f)
		if results is None:
			warnings.warn("Filename is not formatted correctly (No Cost):" + str(f))
			continue
		cost = results.group()[0:-1]
		print(cost)
		
		
		#ok, now, I need to find the supplier and the annotations.  This can be done destructively.
		f_stripped = f[f.find("]")+1:]
		
		if(f_stripped[0] == " "): #remove the space after the bracket, which should but doesn't always exist
			f_stripped = f_stripped[1:]
		
		company = f_stripped[0:f_stripped.find(" ")]
		print(company)
		
		f_stripped = f_stripped[f_stripped.find(" ")+1:]
		description = f_stripped[0:f_stripped.find("$")].strip() #to trim any white space
		print(description)
		
		wrtr.writerow([date,company,description,cost])
		myfile.flush()
	
	myfile.close()
	print("Done")