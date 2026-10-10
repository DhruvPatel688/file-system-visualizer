#!/usr/bin/python3
import os
import sys
import csv
from tabulate import tabulate
import argparse

BLOCK_SIZE = 512 #A set block size of 512 makes the drill_down function more efficient


#This function uses trap instructions to obtain file system stats from the kernel to use in other functions
def data():
    d = []
    mountpoint_data = []
    with open('/proc/mounts', 'r') as raw_data:# Must read through the mountpoints
        read_data = raw_data.readlines()
        for i in read_data:
            current = i.split(" ")
            #No need to parse through virtual file systems it would be inefficient
            if current[2] not in ['proc', 'sysfs', 'devtmpsf', 'squashfs', 'cgroup*', 'ramfs', 'overlay', 'ramfs', 'autofs']:
                d.append(current[0:3])
    for i in range(len(d)):
        try:
            mountpoint = os.statvfs(d[i][1]) #Make a system call to obtain stats on specific file systems
            total = (mountpoint.f_blocks * mountpoint.f_frsize)/1048576 #convert to MiB
            free = (mountpoint.f_bavail * mountpoint.f_frsize)/1048576
            used = total - free
            name = d[i][1]
            if total == 0:
                continue
            else:
                percent_used = (used/total) * 100
                percent_used = round(percent_used, 2)
            mountpoint_data.append([name, round(total, 2), round(used, 2), round(free, 2), percent_used, d[i][0]])
        except OSError:
            pass
    return mountpoint_data

#This function applies the proper ANSI codes to the data values, for Flagging specific values above a certain threshold.
def color_code(data):
    new_data = []
    if len(data[0]) > 2:
        for i in data:
            new_row = []
            for j in i:
                
                if i[4] >= 90 and i[4] <= 100: #Critical threshold must make space
                    j = f"\033[31m{j}\033[0m"
                elif i[4] > 70 and i[4] < 90: #Warning threshold file system is filling up
                    j = f"\033[33m{j}\033[0m"
                else:
                    j = f"\033[32m{j}\033[0m"
                new_row.append(j)
            new_data.append(new_row)
        return new_data
    else:
        return data

    
#This function uses the data from data() and outputs it in a proper table.
def display_table(data, filt = 'none'):
    if len(data) == 0:
        return None
    else:
        if len(data[0]) == 6:
            data = color_code(data) #color code the data for flagging
            headers = ["Mountpoint", "Total(MiB)", "Used(MiB)", "Free(MiB)", "PercentUsed", "Filesystem"]
        else:
            headers = ["Type", "Name", 'Size in MiB']
        return tabulate(data, headers, tablefmt="simple-grid") #Call tabulate to format table correctly

#This function is used to filter through the data from data() and output the proper file system
def filter_data(filt, data, sign, percent = 0):
    num = 0
    row = None
        
    if filt == 'used' or filt == 'Used':
        num = 2
    elif filt == 'total' or filt == 'Total':
        num = 1
    elif filt == 'free' or filt =='Free':
        num = 3
    elif filt == 'PercentUsed' or filt == 'percentused' or filt == 'percent used' or filt == 'Percent Used':
        num = 4
    else:
        row = filt #filtering by row
    filtered_data = []
    
    #if filtering by row quickly output result
    for i in data:
        if row != None and i[0] == row or i[5] == row:
            filtered_data.append(i)
            return filtered_data
            
    #if filtering by value iterate through data
    percent_data = []
    for i in data:
        if sign == ">":
            if i[num] > float(percent):
                percent_data.append(i)
        elif sign == "<":
            if i[num] < float(percent):
                percent_data.append(i)
        else:
            percent_data.append(i)
    return percent_data
                
 
    
#This function sorts the data in data() based on user input
def sort_data(data, filt, sort = None):
    if filt == 'used' or filt == 'Used':
        num = 2
    elif filt == 'total' or filt == 'Total':
        num = 1
    elif filt == 'free' or filt =='Free':
        num = 3
    elif filt == 'PercentUsed' or filt == 'percentused' or filt == 'percent used' or filt == 'Percent Used' or filt =="Percent_Used":
        num = 4
    elif filt == 'Mountpoint' or filt == 'Mount Point' or filt == 'mountpoint' or filt == 'mount point':
        num = 0
    elif filt == 'Filesystem' or filt == 'File System' or filt == "file_system" or filt == "FileSystem" or filt == "file_system" or filt == 'File_System':
        num = 5
    else:
        return None
    
    #simple insertion sort used to sort data
    for i in range(1, len(data)):
        now = data[i]
        j = i - 1
        if sort == 'asc':
            while j >= 0 and now[num] < data[j][num]: #used to sort in ascending order
                data[j+1] = data[j]
                j -= 1
        elif sort == 'desc':
            while j >= 0 and now[num] > data[j][num]: #used to sort in descending order
                data[j+1] = data[j]
                j -= 1
        data[j+1] = now
    return data
    
    
#This is a helper function used in drill_down to find the appropriate sizes of subdirectories and files.
def drill_down_data(directory, depth = 0):
    size = 0
    if depth >= 4: #For quick retrieval must cap the depth at 4
        return size
    try:
        with os.scandir(directory) as d:
        # Use os.scandir to scan top level
            for i in d:# Find all item in top level
                i_stat = i.stat()
                if i.is_dir():
                    t = 'Directory'
                    depth += 1
                    size += drill_down_data(i.path, depth) #make a recursive call to walk through subdirectory
                else:
                    t = 'File'
                    size += i_stat.st_blocks * BLOCK_SIZE # Calculate size of file
    except OSError:
        pass
        
    return size

#This function drills down into a specific directory to find the largest subdirectories and files.
def drill_down(directory):
    # Start search of directory
    sizes = {}
    top_ten =[]
    try:
        with os.scandir(directory) as d:
        # Use os.scandir to scan top level
            for i in d:# Find all item in top level
                i_stat = i.stat()
                if i.is_dir():
                    t = 'Directory'
                    depth = 0
                    size = drill_down_data(i, depth) #use helper function to find subdirectory size
                else:
                    t = 'File'
                    size = i_stat.st_blocks * BLOCK_SIZE
                sizes[i.name] = [size, t] # Append each sub directories totals to a dictionary
            
        sorted_sizes = dict(sorted(sizes.items(), key = lambda item:item[1][0])) #Sort dictionary in ascending order
        num = 10
        for key, value in reversed(sorted_sizes.items()): # Rank and give the top 10 sub directories
            if num == 0:
                break
            top_ten.append([value[1], key, round((value[0]/1048576), 2)])
            num -= 1
    except OSError:
            pass
    return top_ten
 
#This function essentially drills down into every file system to find the largest subdirectories and files on the machine.
def globe_data(data):
    global_data = []
    for i in data:
        new_data = drill_down(i[0]) #drill_down into every file system in data()
        for j in new_data:
            global_data.append(j)
            
    #Use insertion sort to sort subdirectory and file size in descending order
    for i in range(1, len(global_data)):
        now = global_data[i]
        j = i - 1
        while j >= 0 and now[2] > global_data[j][2]:
            global_data[j+1] = global_data[j]
            j -= 1
        global_data[j+1] = now
        
    return global_data[:10]

#This function exports the data from the data() function into a csv file for external use.
def export(data):
    if data == None:
        print("No data found")
        return
    else:
        try:
            fieldnames = ["Mountpoint", "Total(MiB)", "Used(MiB)", "Free(MiB)", "PercentUsed"]
            with open('fsvis_data.csv', 'w', newline = '') as csvfile: #Write a new csv file

                writer = csv.writer(csvfile)
                writer.writerow(fieldnames)
                writer.writerows(data)
            print("Your data is now in file: fsvis_data.csv")
        except Exception as e:
            print(f"Error {e} has occured")
    
        
    
#This function is used to parse through user input and call the proper function from above
def run_program(operation = None, specification1 = None, specification2 = None, specification3 = None, specification4 = None):

    datas = data() #call the data function to get the data to use below
    
    if operation  == 'sort' and specification2 == 'asc' or specification2 == 'desc':
        sorted_data = sort_data(datas, specification1, specification2)
        print(display_table(sorted_data))
        
    elif operation == 'filter' and specification1 != None:
        filt_data = filter_data(specification1, datas, specification2, specification3)
        print(display_table(filt_data, specification1))

    elif operation == 'drill_down' and specification1 != None:
        print(display_table(drill_down(specification1)))

    elif operation == 'global':
        print(display_table(globe_data(datas)))

    elif operation == 'csv':
        export(datas)
        
    elif operation == 'help':
        print("Please write commands in the below form")
        print("For Display table: python3 -m fsvis")
        print("For Sorting the table either (asc or desc): python3 -m fsvis sort Used asc")
        print("For Filtering the table by values: python3 -m fsvis filter PercentUsed '>' 50")
        print("For Filtering the table by mountpoint: python3 -m fsvis filter /")
        print("For Drill Down: python3 -m fsvis drill_down /")
        print("For Largest Directories and files: python3 -m fsvis global")
        print("For exporting data table: python3 -m fsvis csv")
        
    elif operation == None:
        print(display_table(datas))

#This function is used to obtain the proper input from the user and run the program
def main():
    parser = argparse.ArgumentParser(description = "A simple CLI for filesystem storage")
    parser.add_argument('operation', nargs = "?", default = None,  help = 'The function to run')
    parser.add_argument('specification1', nargs = "?", default = None, help = 'The function to run')
    parser.add_argument('specification2', nargs = "?", default = None, help = 'The function to run')
    parser.add_argument('specification3', nargs = "?", default = None, help = 'The function to run')
    parser.add_argument('specification4', nargs = "?", default = None, help = 'The function to run')

    args = parser.parse_args()
    result = run_program(args.operation, args.specification1, args.specification2, args.specification3, args.specification4)


