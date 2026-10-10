fsvis is a file system visualization tool

This tool analyzes disk usuage on your machine and outputs a table with mountpoint, used space, total space, free space, and percent used space.

## Requirements: 
- You must run this tool on a linux server. 
- Python 3.10 or later should be used as well
- Need to install tabulate library (instructions below)

## Steps to run
1. cd into the project directory: cd 'dhruv_patel_project
2. You may have to cd into that same directory twice depending how submission works with the Zip
2. In terminal run: 
    - sudo apt update
    - sudo apt install python3-tabulate
3. Now the tool should be ready to use


## Testing the tool

### Displaying default table:
1. To display the table, run this in terminal: 
    - python3 -m fsvis

### To sort table:
2. To sort the table, run this in terminal: 
    - python3 -m fsvis sort Column_Name asc
    - Where Column_Name can be: Mountpoint, Free, Used, PercentUsed, or Total
    - Use asc for ascending order and desc for descending order
    - Ex: python3 -m fsvis sort PercentUsed desc
    
### To filter table by mountpoint:
3. To filter the table by mount point run: 
    - python3 -m fsvis filter mountpoint
    - Where mountpoint should be a specific mountpoint such as / or /home
    - Ex: python3 -m fsvis filter /

### To filter table by values:
4. To filter the table by values, specify the column, whether you want values greater than or less than, and the specified value, please use the quotes around '>' or '<' in terminal: 
    - python3 -m fsvis filter PercentUsed '>' 50

### To drill down into a specific directory:
5. To drill down into a specific directory run:
    - python3 -m fsvis drill_down mountpoint
    - Where mountpoint can be any mountpoint in the original displayed table
    - Ex: python3 -m fsvis drill_down /
    
### Bonus Feature: Output top 10 largest directories or files on machine:
6. To output the largest directories or files on the system run:
    - python3 -m fsvis global

### Bonus Feature: Export CSV file of data:
7. To export a csv file of the data:
    - python3 -m fsvis csv

### For additional help:
8. Run: python3 -m fsvis help
    
