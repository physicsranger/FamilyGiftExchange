import sqlite3
import numpy as np
import time,os
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

############################################################
#functions to manage the gift exchange random draw
############################################################

def generate_exchange(database_file,skip_names=None,num_previous_exclude=3,
overwrite=False,new_year=None):
	#first, get the value of new_year if it wasn't supplied
	#otherwise check validity
	if new_year is None:
		new_year=time.localtime().tm_year
	else:
		if not valid_year(str(new_year)):
			print(f'Year {new_year} has an invalid format, should be the four-digit year, e.g., 2023.\nNot doing anything.')
			return
	
	with sqlite3.connect(database_file) as con:
		cur=con.cursor()
		
		#add a new column for this year if it doesn't exist already
		add_new_year(None,new_year,cur)
		
		#now, we're going to check if info for this year exists
		cur.execute('''SELECT COUNT(*)
		FROM exchange
		WHERE ? IS NOT NULL''',(f'Year_{new_year}',))
		if cur.execute.fetchone() is not None:
			if overwrite:
				print(f'Exchange info exists for {new_year}, overwrite flag set to True, will generate new gift exchange assignments.')
			else:
				print(f'Exchange info exists for {new_year}, overwrite flag set to false, will not do anything.')
				return
		#commit the changes
		con.commit()
		
		#get a tuple of names to be in the exchange
		#excluding anyone in skip_names, if that is not empty
		query="SELECT name FROM family"
		if skip_names:
			query+=" WHERE name NOT IN ("
			for _ in range(len(skip_names)-1):
				query+="?,"
			query+="?)"
			cur.execute(query,tuple(skip_names))
		else:
			cur.execute(query)
		names=[name[0] for name in cur.fetchall()]
		
		#make sure we have at least 2 names
		if len(names)<2:
			print(f'Whoops! We ended up with {len(names)} names.')
			print('Make sure you have populated your family table and that you did not accidentally skip too many family members.')
			print(f'Not generating gift exchange assignments for {new_year}')
			return
		
		#get the columns from the exchange table to be used in building
		#lists of members to exclude for each member
		#(based on significant other and if they had them in the last few exchanges)
		#this way we only do this step once
		exclude_years=get_exclusion_years(None,new_year,num_previous_exclude,cur)
		
		#change the row_factory to allow for working with results
		#like dictionaries, make sure to make a new cursor
		con.row_factory=sqlite3.Row
		cur=con.cursor()

		#now, we need to get the family member information
		query='SELECT * FROM family WHERE name in ('
		for _ in range(len(names)-1):
			query+='?,'
		query+='?)'
		rows=cur.execute(query,tuple(names)).fetchall()
		
		#now let's build a members dictionary
		member_info={}
		for row in rows:
			if row is not None:
				member_info[row['name']]={'email':row['email'],'id':row['id'],
			'address_id':row['address_id']}
		
		#now add in the exclude info
		query='SELECT f.name, s.so_id'
		if exclude_years:
			for year in exclude_years:
				query+=f', e.{year}'
		query+=' FROM family as f JOIN significant_other as s ON f.id=s.id'
		if exclude_years:
			query+=' JOIN exchange as e ON e.id=f.id'
		query+=' WHERE name IS IN ('
		for _ in range(len(names)-1):
			query+='?,'
		query+='?)'
		rows=cur.execute(query,tuple(names)).fetchall()
		for row in rows:
			if row is not None:
				#by default, will exclude yourself
				member_info[row['name']]['excludes']=[row['name']]
				#if you have a significant other, add them to the exclude
				if row['s.so_id'] is not None:
					member_info[row['name']]['excludes'].append(row['s.so_id'])
				#now, if exclude_years isn't empty,
				#add your recent giftees to your current exclude list
				for year in exclude_years:
					member_info[row['name']]['excludes'].append(row[f'e.{year}'])
		
		#before we proceed to making the draws, let's check that the excludes
		#haven't resulted in a situation where someone has no valid options
		BAIL=False
		for name in names:
			if len(member_info[name]['excludes'])>=len(names):
				#two possibilities, some duplicates or num_previous_excludes too large
				if len(member_info[name]['excludes'])==len(names):
					print(f'ERROR:exclude list for {name} excludes all family members.')
					print('Consider excluding fewer previous year giftees.')
					BAIL=True
				
				if max([member_info[name]['excludes'].count(exclude) for exclude in member_info['name']['excludes']])>1:
					#have a duplicate
					new_excludes=member_info[name]['excludes'][0]
					for exclude in member_info[name]['excludes'][1:]:
						if exclude not in new_excludes:
							new_excludes.append(exclude)
					if len(new_excludes)==len(names):
						print(f'ERROR: exclude list for {name} excludes all family members, even after removing duplicates.')
						print('Consider excluding fewer previous year giftees.')
						BAIL=True
					else:
						member_info[name]['excludes']=new_excludes
		if BAIL:
			print('Will not generate new gift exchange assignments, see output messages.')
			return
		
		#now we need to actually do the random draws
		#taking into account the exclusion info
		exchange_draws=get_draws(member_info)
		
		#if we get a None-type object returned, something went wrong
		if exchange_draws is None:
			print('Was unable to produce gift exchange draws satisfying all exclusion requirements.')
			print('Please check output messages, database tables, and choice of number of previous giftees to exclude and try again.')
			return
		
		#now we need to add the giftee assignments to the exchange table in the
		#column for the new year
		query=f'''UPDATE exchange
		SET Year_{new_year}=?
		WHERE id=?'''
		
		for name in names:
			cur.execute(query,
			(member_info[exchange_draws[name]]['id'],member_info[name]['id']))
		
		#commit the change, print a success statement, and return
		con.commit()
	
	print(f'Successfully generated gift exchange assignments for {new_year}')
	return

#I'll get the skeleton in place for this, but will depend on if
#I'm able to figure out the directory structure stuff within the repo or not
def output_giftee_assignments(database_file,year=None):
	#if no year was provided, assume it is the current year
	if year is None:
		year=time.localtime().tm_year
	#otherwise, check the input year to make sure it is a valid format
	elif not valid_year(str(new_year)):
			print(f'Year {year} has an invalid format, should be the four-digit year, e.g., 2023.\nNot doing anything.')
			return
	
	with sqlite3.connect(database_file) as con:
		con.row_factory=sqlite3.Row
		cur=con.cursor()
		
		rows=cur.execute(f'''SELECT id,Year_{year}
		FROM exchange''').fetchall()
		
		if rows is None:
			print(f'Uh oh! Gift exchange does not appear to have been generated for {year}.\nWill not produce assignment files.')
			return
		
		for row in rows:
			produce_assignment_files(database_file,
			row['id'],row[f'Year_{year}'],year,cur)
					
def get_draws(members):
	#set the random seed, to avoid deterministic behavior
	#use integer version of whatever current unix time is
	np.random.seed(int(time.time()))
	
	#now we need to enter a loop where we try to assign a giftee
	#to each family member, taking into account the exclusion info
	#and allowing for getting unlucky and starting over
			
	#randomize the order of drawing
	drawers=np.choice(list(members.keys()),size=len(members.keys()),replace=False)
	
	#now let's do the draws
	while (redo_draws:=True) and (counter:=0)<1000:
			available_names=list(members.keys())
			exchange_draws={}
			for drawer in drawers:
				#get the list of available names to draw
				giftees=[name for name in available_names if name not in members[drawer]['excludes']]
				
				#if the list is empty, then we've run into an issue
				#where there are no valid names for this person to draw
				#so we need to pop out of the for loop
				#which will make us try again
				if not giftees:
					break
				
				#randomly pick someone from the available giftees
				exchange_draws[drawer]=np.random.choice(giftees,size=1,
				replace=False)
				
				#update the list of available names for the next person to draw
				available_names.remove(exchange_draws[drawer])
			
			#if the exchange_draws dictionary has the same number of
			#entries, then we were successful
			#otherwise, redo_draws remains True and we try again
			if len(exchange_draws.keys())==len(members.keys()):
				redo_draws=False
				
			#we will update the counter just in case I missed some situation
			#where we would get into an infinite loop
			else:
				counter+=1
				if counter==1000:
					print('Whoops! Got stuck in a loop while drawing names')
		
	#check length of exchange_draws dictionary
	if len(exchange_draws.keys())!=len(members.keys()):
		return None
	else:
		return exchange_draws

#note, will always need database_file
#since we need to know where to write out the files
def produce_assignment_file(database_file,gifter_id,giftee_id,year,cur=None):
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	
	#get the directory
	gift_exchange_dir=os.path.join(os.path.abspath(database_file),str(year))
	if not os.path.exists(gift_exchange):
		os.mkdir(gift_exchange)
	
	#look up the names and the giftee address info
	###I need to experiment with this, can I always be sure
	###that the gifter will be first, simply because they were listed first
	###in the input values?
	rows=cur.execute('''SELECT name,address_id
	FROM family
	WHERE id IS IN (?,?)''',(gifter_id,giftee_id)).fetchall()
	
	gifter=rows[0][0]
	giftee=rows[1][0]
	giftee_address_id=rows[1][1]
	
	assignment_file_name=f'{gifter}_{year}.txt'
	
	if giftee_address_id is not None:
		giftee_address=cur.execute('''SELECT address
		FROM addresses
		WHERE id=?''',(giftee_address_id,)).fetchone()[0]
	
	else:
		giftee_address="No address indicated in database.\nConsult family member in charge of the exchange."
	
	with open(os.path.join(gift_exchange_dir,assignment_file_name),'w') as assign_file:
		assign_file.write(f'{gifter} has {giftee}\nUse address:\n{giftee_address}')
	
	if con is not None:
		con.close()
	
	return

#function to add a new year column to the exchange table
def add_new_year(database_file,year,cur=None):
	if valid_year(str(year)):
		new_column=f'Year_{year}'
	else:
		raise ValueError(f'{year} is not a valid 4-digit year value.')
		
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=sqlite3.cursor()
	else:
		con=None
	
	columns=[descr[0] for descr in cur.execute('SELECT * FROM exchange').description]
	if new_column not in columns:
		cur.execute(f'''ALTER TABLE exchange
		ADD {new_column} INT UNISIGNED''')
		print(f'Column for {year} successfully added.')
	else:
		print(f'Year {year} already in exchange table.')
	
	if con is not None:
		con.commit()
		con.close()
	return

def get_excludes(database_file,member_id,years,cur=None):
	#if we didn't pass in a valid cursor, connect to the database
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	
	excludes=[]
	
	#first, check the significant other table
	significant_other=cur.execute('''SELECT so_id
	FROM significant_other
	WHERE id=?''',(member_id,)).fetchone()
	
	if significant_other is not None:
		excludes.append(significant_other)
	
	query=f'SELECT {years[0]}'
	if len(years)>1:
		for year in years[1:]:
			query+=f', {year}'
	query+=' FROM exchange WHERE id=?'
	
	for row in cur.execute(query,(member_id)).fetchall():
		if row is not None:
			excludes.append(row[0])
	
	if con is not None:
		con.close()
	
	return excludes

#function to get the column names of years for generating exclusions
#this way we only do it once
def get_exclusion_years(database_file,this_year,num_exclude,cur=None):
	#check the input year
	if not valid_year(string(this_year)):
		raise ValueError(f'{this_year} is not a valid 4 digit year')
	
	#if we didn't pass in a valid cursor, connect to the database
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	
	#now, check the previous years, may need to account for non-consecutive years
	years=[descr[0] for descr in cur.execute('SELECT * FROM exchange').description if descr[0]!='id']
	years=[[year,this_year-int(year.split('_')[1])] for year in years].sort(reverse=True)
	if len(years)<num_exclude:
		print(f'Requested to exclude possible giftees for each family member from {num_exclude} previous years, but there are only {len(years)} years in the exchange.')
		print('We will only exclude giftees for each family member using {len(years)} years.')
		num_exclude=len(years)
	years_to_exclue=[year[0] for year in years[:num_exclude]]
	
	if con is not None:
		con.close()
	
	return years_to_exclude
	
	

#function to check if a valid year has been specified
#done as a separate function so the 'check' variable exists
#only in this temporary scope
def valid_year(year_string):
	if not isinstance(year_string,str):
		raise TypeError(f'Input value should be str type, not {type(year_string)}')
	try:
		check=time.strptime(year_string,'%Y')
		return True
	except ValueError:
		return False

############################################################
#functions for family management purposes
############################################################

#function to add/update family table
#the input should be a nested dictionary with info for the member
#top dictionary should have keys for each table
#then each dictionary there should have the relevant info
def add_or_update_family_member(database_file,member):
	try:
		name=member['family']['name']
	except KeyError:
		print('No name supplied for family member, nothing to do.')
		return
	
	if 'address' in member['family'].keys():
		address_id=get_address_id(database_file,address)
		if address_id is None:
			#first, we need to check if this family member already has an address
			#in the table
			with sqlite3.connect(database_file) as con:
				cur=con.cursor()
				address_id=cur.execute('''SELECT address_id
				FROM family
				WHERE name=?''',(name,)).fetchone()
				
				#if the current_address is None, then they aren't in
				#the database yet so we need to add an address for them
				#alternatively, they may have moved but someone else still 
				#needs that address so we'll check that and add a new entry still
				if address_id is None or count_at_address(None,address_id,cur)>1:
					add_address(None,address,cur)
					address_id=get_address_id(None,address,cur)
				
				#if they do have an address_id, then we can assume that they
				#have moved and no one else still lives there so
				#we can simply update the address
				else:
					update_address(None,address_id,address,cur)
				#either way, we need to commit the changes before
				#exiting the with statement
				con.commit()
		elif address_changed(database_file,address_id,name):
			#check if multiple people have that address
			if count_at_address(database_file,address_id)>1:
				add_address(database_fil,address)
				address_id=get_address_id(database_file,address)
			#if not, then just update the address
			else:
				update_address(database_file,address_id,address)		
		member['family']['address_id']=address_id
	
	#check if the email has been provided
	if 'email' not in member['family'].keys():
		member['family']['email']=get_email(database_file,name)
	
	#now we need to decide if we're adding someone or updating information
	if member_in_database(database_file,name):
		update_family_member(database_file,member['family'])
	else:
		add_family_member(database_file,member['family'])
	
	#now check if info is provided for significant other
	if 'significant_other' in member.keys():
		significant_other=member['significant_other']
		significant_other_id=get_member_id(database_file,significant_other)
		#check if the significant_other is in the family
		if member_in_database(database_file,significant_other):
			#check if the this member already has a significant other
			#and if it is different than what has been provided
			current_so_id=get_significant_other_id(database_file,name)
			
			#we only need to do something if they don't match
			if current_so_id!=significant_other_id:
				update_significant_other(database_file,
				get_member_id(database_file,name),
				significant_other_id)
		
		else:
			print(f'Significant other {significant_other} for {name} is not in the database.')
			print(f'Adding entry for {significant_other}, will need to update email and address manually.')
			
			so_member={'name':significant_other,'email':None,
			'address_id'=None}
			add_family_member(database_file,significant_other)
			
			#now add the significant other info for both
			add_significant_other(database_file,
			get_member_id(database_file,name),
			get_member_id(database_file,significant_other))
			
			add_significant_other(database_file,
			get_member_id(database_file,significant_other),
			get_member_id(database_file,name))
	
	print(f'Information added/updated for family member {name}')
	return

#function to remove a family member from the database
def remove_family_member(database_file,name):
	with sqlite3.connect(database_file) as con:
	    #use sqlite3.Row so that we can get all the info about
	    #the member as an easy to work with dictionary
		con.row_factor=sqlite3.Row
		cur=con.cursor()
		member=cur.execute('''SELECT *
		FROM family
		WHERE name=?''',(name,)).fetchone()
		
		if member is None:
			print(f'{name} is not in database, nothing to do.')
			return
		
		#if this family member is the only one at the address in the
		#addresses table, remove that from the table
		if count_at_address(None,member['address_id'],cur)<1:
			cur.execute('''DELETE *
			FROM addresses
			WHERE id=?''',(member['address_id'],))
		
		#now remove the member from the family and significant_other tables
		cur.execute('''DELETE *
		FROM family
		WHERE id=?''',(member['id'],))
		cur.execute('''DELETE *
		FROM significant_other
		WHERE id=?''',(member['id'],))
		
		#and update the info for whoever might have had this
		#member as their significant_other
		cur.execute('''UPDATE significant_other
		SET so_id=NULL
		WHERE so_id=?''',(member['id'],))
		
		#commit the changes
		con.commit()
	return

#############################################################
#helper functions for family management, called by the
#functions above but could be invoked on their own as well
#############################################################

def add_family_member(database_file,member,cur=None):
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	
	#first, we add the new family member to the family table
	cur.execute('''INSERT INTO family
	(id,name,email,address_id)
	VALUES (NULL,?,?,?)''',(member['name'],member['email'],member['address_id']))
	
	new_id=get_member_id(None,member['name'],cur)
	
	#next, we add them to the exchange table
	#for existing years, they will have a NULL value
	cur.execute('''INSERT INTO exchange
	(id)
	VALUES (?)''',(new_id,))
		
	if con is not None:
		con.commit()
		con.close()
	return

def update_family_member(database_file,member,cur=None):
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	
	cur.execute('''UPDATE family
	SET email=?,
	address_id=?
	WHERE name=?''',(member['email'],member['address_id'],member['name']))
	
	if con is not None:
		con.commit()
		con.close()
	return

def member_in_database(database_file,name,cur=None):
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	member=cur.execute('''SELECT COUNT(*)
	FROM family
	WHERE name=?''',(name,)).fetchone()
	return member is not None

def get_member_id(database_file,name,cur=None):
	if not is instance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	
	member_id=cur.execute('''SELECT id
	FROM family
	WHERE name=?''',(name,)).fetchone()
	
	if con is not None:
		con.close()
	
	member_id=(member_id if member_id is None else member_id[0])
	return member_id

def get_email(database_file,name,cur=None):
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	email=cur.execute('''SELECT email
	FROM family
	WHERE name=?''',(name,)).fetchone()
	if con is not None:
		con.close()
	email=(email if email is None else email[0])
	return email

def get_significant_other_id(database_file,name,cur=None):
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	
	significant_other_id=cur.execute('''SELECT so_id
	FROM significant_other as s
	JOIN family as f
	ON f.id=s.id
	WHERE f.name=?''',(name,)).fetchone()
	
	if con is not None:
		con.close()
	
	significant_other_id=(significant_other_id if significant_other_id is None else significant_other_id[0])
	return significant_other_id

def update_significant_other(database_file,member_id,significant_other_id,cur=None):
	if not is instance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	
	cur.execute('''UPDATE significant_other
	SET so_id=?
	WHERE id=?''',(significant_other_id,member_id))
	
	if con is not None:
		con.commit()
		con.close()
	return

#function to get the id from the addresses table for a given address
#if the address is not in the table, it will return a None type
def get_address_id(database_file,address,cur=None):
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	address_id=cur.execute(f'''SELECT id FROM addresses
	WHERE address LIKE "?" ''',(address,)).fetchone()
	if con is not None:
		con.close()
	address_id=(address_id if address_id is None else address_id[0])
	return address_id

#a quick helper function to get the number of family members
#at a given address, simple query but don't want to clutter other functions
def count_at_address(database_file,address_id,cur=None):
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	address_count=cur.execute('''SELECT COUNT(*)
		FROM family
		WHERE address_id=?''',(address_id,)).fetchone()[0]
	if con is not None:
		con.close()
	return address_count

def add_address(database_file,address,cur=None):
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor
	else:
		con=None
	cur.execute('''INSERT INTO addresses
	(id,address)=(NULL,?)''',(address,))
	if con is not None:
		con.commit()
		con.close()
	return

def update_address(database_file,adress_id,address,cur=None):
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
	else:
		con=None
	cur.execute('''UPDATE addresses
	SET address=?
	WHERE id=?''',(address,adress_id))
	if con is not None:
		con.commit()
		con.close()
	return

def address_changed(database_file,address_id,name,cur=None):
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	current_address_id=cur.execute('''SELECT address_id
	FROM family
	WHERE name=?''',(name,)).fetchone()
	if con is not None:
		con.close()
	if current_address_id is None:
		return False
	else:
		return address_id==current_address_id[0]


	
	
	