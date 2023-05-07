import os,sqlite3,time
from shutil import copyfile

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
			backup_file=os.path.join(os.sep,*database_file.split(os.sep)[1:-1],
				'bkup_'+database_file.split(os.sep)[-1])
			#need some logic to catch windows systems
			copyfile(database_file,backup_file)
			os.remove(database_file)
			print(f'A backup of the existing database has been moved to\
			 {backup_file} and the original removed.')
			print('NOTE: Currently, you will need to manually rename this file\
			 to recover the previous database, which will be overwritten if you\
			  try to create the database again with overwrite set to True.')
		else:
			raise FileExistsError(f'{database_file} already exists but overwrite\
			 set to False')
	
	#now, create the database
	con=sqlite3.connect(database_file)
	cur=con.cursor()
	
	#create the necessary tables
	print('Creating tables',end='...')
	
	#first, the family table
	cur.execute('''CREATE TABLE family
	(id INTEGER PRIMARY KEY AUTOINCREMENT,
	name VARCHAR(64),
	email VARCHAR(128),
	address_id INTEGER,
	constraint fk_address FOREIGN KEY (address_id) REFERENCES id (address))''')
	
	print('',end='...')
	
	#next, the significant_other table
	cur.execute('''CREATE TABLE significant_other
	(id INTEGER,
	so_id INTEGER,
	constraint pk_significant_other PRIMARY KEY (id),
	constraint fk_id FOREIGN KEY (id) REFERENCES id (family))''')
	###initially had a constraint on the so_id column as well, but this value can
	###be null, have to think about that
	
	print('',end='...')
	
	#next, the address table
	cur.execute('''CREATE TABLE addresses
	(id INTEGER PRIMARY KEY AUTOINCREMENT,
	address TEXT)''')
	
	print('',end='...')
	
	#finally, the exchange table
	#will start with just one year
	current_year=f'Year_{time.localtime().tm_year}'
	cur.execute(f'''CREATE TABLE exchange
	(id INTEGER,
	{current_year} INTEGER,
	constraint pk_exchange PRIMARY KEY (id),
	constraint fk_id FOREIGN KEY (id) REFERENCES id (family))''')
	
	con.commit()
	con.close()
	
	print('finished.')
	
	return