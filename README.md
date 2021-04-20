# TTM4115_Project
This project is a part of the course TM4115 at NTNU Spring 2021. 

## How to set up a venv environment (inside the project folder)

For reference:
https://docs.python.org/3/library/venv.html

* Clone the project to you computer. 
* Navigate to your project in terminal.
* Run the following command to create a new environment called "venv". It's going to create a folder for your environment inside the project folder. This is already added to the gitignore file, so it's not going to be pushed to a remote repo. Note that your venv environment will be based on your "python3" version. 
```
python3 -m venv ./venv
```
* Activate the enviroment using one of the following commands. 

Posixs/unix (max and linux):
```
source venv/bin/activate
```
Windows cmd: 
```
C:\> venv\Scripts\activate.bat
```
Windows powershell:
```
PS C:\> venv\Scripts\Activate.ps1
```

If sucessful, you should see you environment in your teminal, like this (mac):
```
$ (venv) computername:TTM4115_Project username$ 
```
* Install required packages specified in the "requirements.txt" file using the following command. 
```
pip install -r requirements.txt
```


* If you install any additional packages that your teammates also will need, then add them to the "requirements.txt" file by using the following command. 
```
pip freeze > requirements.txt
```