import os,sqlite3

#################################################
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
			raise FileExistsError(f'{database_file} already exists but overwrite set to false')
	
	#now, create the database
	with sqlite3.connect(database_file) as connection:
		cursor=connection.cursor()
		
		#create the necessary tables
		print('Creating tables...')
		
		#first, the family table
		cursor.execute('''CREATE TABLE family
		(id INT UNSIGNED AUTO_INCREMENT,
		name VARCHAR(64),
		email VARCHAR(128),
		address_id INT UNSIGNED,
		constraint pk_family PRIMARY KEY (id),
		constraint fk_address FOREIGN KEY (address_id) REFERENCES id (address))''')
		
		#next, the significant_other table
		cursor.execute('''CREATE TABLE significant_other
		(id INT UNSIGNED,
		so_id INT UNSIGNED,
		constraint pk_significant_other PRIMARY KEY (id),
		constraint fk_id FOREIGN KEY (id) REFERENCES id (family))''')
		###initially had a constraint on the so_id column as well, but this value can
		###be null, have to think about that
		
		#next, the address table
		cursor.execute('''CREATE TABLE addresses
		(id INT UNSIGNED AUTO_INCREMENT,
		address TEXT,
		constraint pk_address PRIMARY KEY (id))''')
		
		#finally, the exchange table
		#will start with just one year
		current_year=f'Year_{time.localtime().tm_year}'
		cursor.execute(f'''CREATE TABLE exchange
		(id INT UNSIGNED,
		{current_year} INT UNSIGNED,
		constraint pk_exchange PRIMARY KEY (id),
		constraint fk_id FOREIGN KEY (id) REFERENCES id (family))''')
		
		connection.commit()
		print('...finished.')
	
	return