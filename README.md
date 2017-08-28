## Start the Service

1. Setup Virtual Machine
 a. Install VirtualBox and Vagrant (you can find links on Internet by searching)
 b. Clone [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm)
 c. Replace content of folder `vagrant/catalog` with content of the zip, so you should have `project.py` under folder `catalog`
 d. Change your directory to `vagrant` and run `vagrant up` to start the virtual machine
 e. Run `vagrant ssh` to ssh into the machine
 f. Run `cd /vagrant/catalog` to change your directory to the correct folder
2. Setup the Database, a .db file comes with the zip, however you can follow those steps to generate a new one if this one deleted.
 a. Make sure you are in the `/vagrant/catalog` directory of the VM
 a. Run `python database_setup.py` to create the database
 b. Run `python lots_of_items.py` to create some items
3. Start the service
 a. Run `python project.py` from the same directory as in step 2
 b. Go to `http://localhost:5000/` in any of your browser, i.e., outside the VM.
 c. Start browsing, creating and editing your own items.


## Using the Service
1. You need a google account to use the service, you can get one free [here](https://accounts.google.com/SignUp)
2. Whenever you are lost, you can click the "Show All Categories" button to go back to home screen, or go to `http://localhost:5000/`