import argparse

from os import listdir
from os.path import isfile, join, isdir, relpath
import csv
import re
import warnings

def list_filenames(folder_location): #will filter out folders.
	dir_list = listdir(folder_location)
	dir_list = [x for x in dir_list if not isdir(join(folder_location,x))] #remove anything that's a folder
	return dir_list

def list_files_recursive(folder_location):
	files_to_return = []
	paths_to_return = []
	for entry in listdir(folder_location):
		full_path = join(folder_location, entry)
		if isdir(full_path):
			deep_files, deep_paths = list_files_recursive(full_path)
			files_to_return.extend(deep_files)
			paths_to_return.extend(deep_paths)
		else:
			files_to_return.append(entry)
			paths_to_return.append(folder_location)

	return files_to_return, paths_to_return



if __name__ == "__main__":
	print("Welcome to Doug's overintelligent file parser!")
	""" Creating the argparse """
	parser = argparse.ArgumentParser(description = 'Location of a folder to generate list csv formmated files.  \n\r Generates a CSV that can by copied-pasted into the expenses spreadsheet.  \n\r Files are supposed to be named like: "[2018.06.04] CompanyNameOneWord Purchase Description $XX.YY"')
	parser.add_argument("-r","--recursive",action='store_true',help = "resursively search (default false, pass argument to set true)",required=False)
	parser.add_argument("folder_location", type = str, help = 'set the input folder location' )
	parser.add_argument("out", type = str, help = 'set the output CSV name / location')
	parsed = parser.parse_args()

	#print(parsed)
	#print(str(parsed.in))
	
	if not parsed.recursive:
		all_files = list_filenames(parsed.folder_location)
		all_paths = ["parsed.folder_location" for file in all_files]
	else:
		all_files, all_paths = list_files_recursive(parsed.folder_location)

	all_paths = [relpath(p,parsed.folder_location) for p in all_paths] #let's strip away the base folder location, just to make things prettier....

	#print(all_files)
	#print(all_paths) 
	
	
	myfile = open('myfile.csv','w')
	wrtr = csv.writer(myfile,delimiter=',', quotechar='"')
	
	reciepts = []
	
	dates_search= re.compile("\[\d\d\d\d\-\d\d\-\d\d\]")
	cost_search = re.compile("\$\d*.\d\d\.")
	
	spaces_search = re.compile("\ ")
	
	for f,p in zip(all_files,all_paths):
		#print(f)
		#print(p)
		results = dates_search.search(f)
		if results is None:
			warnings.warn("Filename is not formatted correctly (No Date):" + str(f))
			continue
		date = results.group()[1:-1]
		date = date.replace(".","/") #replace dots with slashes to keep sheets happy
		#print(date)
		
		results = cost_search.search(f)
		if results is None:
			warnings.warn("Filename is not formatted correctly (No Cost):" + str(f))
			continue
		cost = results.group()[0:-1]
		#print(cost)
		
		
		#ok, now, I need to find the supplier and the annotations.  This can be done destructively.
		f_stripped = f[f.find("]")+1:]
		
		if(f_stripped[0] == " "): #remove the space after the bracket, which should but doesn't always exist
			f_stripped = f_stripped[1:]
		
		company = f_stripped[0:f_stripped.find(" ")]
		#print(company)
		
		f_stripped = f_stripped[f_stripped.find(" ")+1:]
		description = f_stripped[0:f_stripped.find("$")].strip() #to trim any white space
		#print(description)

		if parsed.recursive:
			wrtr.writerow([p,date,company,description,cost])
		else:
			wrtr.writerow([date,company,description,cost])
		
		myfile.flush()
	
	myfile.close()
	print("Done")