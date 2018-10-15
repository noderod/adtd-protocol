## Automated Docker Task Distribution Protocol  

ADTD-P is a fast, reliable way to obtain result files from docker containers.  


**Requirements**  
* Docker
* Nvidia-Docker (For GPU jobs only)
* Python3

**Setup**  
* Clone this repository  
* Make sure that all requirements are met, if not, the setup file will refuse to continue the installation
* Run the setup file
```bash
	git clone https://github.com/noderod/adtd-protocol
	cd adtd-protocol
	sudo bash setter.sh
```

**Processing Instructions**  
The following instructions must be done in order and with sudo access if needed. This instructions can also be set up as a cron job for periodicity.
1. Update the local client with information about run jobs
2. Run local jobs and upload results to the server
3. Eliminate local images (images older than 4 h, may delete other user images): *idir.py*

```bash
	sudo ./work_checker.py
	sudo ./work_processor.py
	sudo ./idir.py
```

**Local History**  
It is possible to recover the data for all run jobs locally using the following script:  
```bash
	./history.py
```


**Successful execution**  
ADTD-P is not a testing or CI framework, it will not check if the output of a code is correct. it will only notify if the command failed.
Failed commands are those with an exit code different than 0.
