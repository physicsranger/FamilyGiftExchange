import sqlite3
import numpy as np
import time,os
from shutil import copyfile

#a function to create a new database file
#arguments are:
#database_file - (string or pathlike object) full path for database file
#overwrite - (bool, optional) flag to overwrite file if it exists
def create_database(database_file,overwrite=False):
	#first check if the file already exists
	#if it does, either make a backup and delete the existing file
	#or throw an error if overwrite is set to False
	if os.path.exists(database_file):
		if overwrite:
			print(f'NOTE: {database_file} exists but overwrite set to True.')
			if os.path.isdir(os.path.join(os.sep,'tmp')):
				backup_file=os.path.join(os.sep,'tmp',database_file.split(os.sep)[-1])
			else:
				backup_file=os.path.join(os.sep,
				*database_file.split(os.sep)[1:-1],
				'bkup_'+database_file.split(os.sep)[-1])
			#need some logic to catch windows systems
			copyfile(database_file,backup_file)
			os.remove(database_file)
			print(f'A backup of the existing database has been moved to {backup_file} and the original removed.')
			print('NOTE: If using the GUI, the backup file will be deleted upon exit with the "Quit" button.')
		else:
			raise FileExistsError
	
	#now, create the database
	with sqlite3.connect(database_file) as connection:
		cursor=connection.cursor()
		
		#create the necessary tables
		print('Creating tables...')
		
		#first, the family table
		cursor.execute('''CREATE TABLE family
		(id TINYINT UNSIGNED,
		name VARCHAR(32),
		email VARCHAR(64),
		address_id TINYINT UNSIGNED,
		constraint pk_family PRIMARY KEY (id),
		constraint fk_address FOREIGN KEY (address_id) REFERENCE id (address))''')
		
		#next, the significant_other table
		cursor.execute('''CREATE TABLE significant_other
		(id TINYINT UNSIGNED,
		so_id TINYINT UNSIGNED,
		constraint pk_significant_other PRIMARY KEY (id),
		constraint fk_id FOREIGN KEY (id) REFERENCE id (family))''')
		###initially had a constraint on the so_id column as well, but this value can
		###be null, have to think about that
		
		#next, the address table
		cursor.execute('''CREATE TABLE address
		(id TINYINT UNSIGNED,
		address VARCHAR(128),
		constraint pk_address PRIMARY KEY (id))''')
		
		#finally, the exchange table
		#will start with just one year
		cursor.execute('''CREATE TABLE exchange
		(id TINYINT UNSIGNED,
		? YEAR,
		constraint pk_exchange PRIMARY KEY (id),
		constraint fk_id FOREIGN KEY (id) REFERENCE id (family),
		constraint fk_giftee FOREIGN KEY (?) REFERENCE id (family))''',
		(time.localtime().tm_year,time.localtime().tm_year))
		
		connection.commit()
		print('...finished.')
	
	return

#function to add a new year column to the exchange table


#function to add/update the address table


#function to add/update significant other information
	
	
#function to add/update family table


#function to create new gift exchange assignments
	
	
	