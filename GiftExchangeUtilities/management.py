import sqlite3

############################################################
#functions for family management purposes
############################################################

#function to add/update family member info
#the input should be a nested dictionary with info for the member
#top dictionary should have keys for each table
#(family and significant_other)
#then each dictionary there should have the relevant info
def add_or_update_family_member(database_file,member):
	try:
		name=member['family']['name']
	except KeyError:
		print('No name supplied for family member, nothing to do.')
		return
	
	if 'address' in member['family'].keys():
		address_id=get_address_id(database_file,member['family']['address'])
		if address_id is None:
			#first, we need to check if this family member already has an address
			#in the table
			con=sqlite3.connect(database_file)
			cur=con.cursor()
			address_id=cur.execute('''SELECT address_id
			FROM family
			WHERE name=?''',(name,)).fetchone()[0]
			
			#if the current_address is None, then they aren't in
			#the database yet or had no address assigned
			#so we need to add an address for them
			#alternatively, they may have moved but someone else still 
			#needs that address so we'll check that and add a new entry still
			if address_id is None or count_at_address(None,address_id,cur)>1:
				add_address(None,member['family']['address'],cur)
				address_id=get_address_id(None,member['family']['address'],cur)
			
			#if they do have an address_id, then we can assume that they
			#have moved and no one else still lives there so
			#we can simply update the address
			else:
				update_address(None,address_id,member['family']['address'],cur)
			#either way, we need to commit the changes before
			#exiting the with statement
			con.commit()
			con.close()
		
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
			print(f'Significant other {significant_other} for {name}\
			 is not in the database.')
			print(f'Adding entry for {significant_other}, will need to update\
			 email and address manually.')
			
			so_member={'name':significant_other,'email':None,
			'address_id':None}
			add_family_member(database_file,so_member)
			
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
	con=sqlite3.connect(database_file)
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
	
	#now remove the member from the significant_other and family tables
	#(need to think about it, but I believe that is the correct order)
	cur.execute('''DELETE *
	FROM significant_other
	WHERE id=?''',(member['id'],))
	
	cur.execute('''DELETE *
	FROM family
	WHERE id=?''',(member['id'],))
	
	#and update the info for whoever might have had this
	#member as their significant_other
	cur.execute('''UPDATE significant_other
	SET so_id=NULL
	WHERE so_id=?''',(member['id'],))
	
	#commit the changes
	con.commit()
	con.close()
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
	#omitting the 'id' column so it will be automatically autoincremented
	cur.execute('''INSERT INTO family
	(name,email,address_id)
	VALUES (?,?,?)''',(member['name'],member['email'],member['address_id']))
	
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
	WHERE name=?''',(name,)).fetchone()[0]
	return member>0

def get_member_id(database_file,name,cur=None):
	if not isinstance(cur,sqlite3.Cursor):
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
	if not isinstance(cur,sqlite3.Cursor):
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
	address_id=cur.execute(f'''SELECT id
	FROM addresses
	WHERE address LIKE ? ''',(address,)).fetchone()
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
	(address)
	VALUES (?)''',(address,))
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

def query_member(database_file,name,cur=None):
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		con.row_factory=sqlite3.Row
		cur=con.cursor()
	else:
		con=None
	
	if member_in_database(None,name,cur):
		row=cur.execute('''SELECT s.so_id, f.email, a.address
		FROM family AS f
		JOIN significant_other as s
		ON f.id=s.id
		JOIN addresses as a
		ON f.address_id=a.id
		WHERE f.name=?''',(name,)).fetchone()
		
		#if a cursor was passed in, we don't know what row_factory was
		#used, check if it has a dict-like structure or not
		if row is not None:
			if not hasattr(row,'keys'):
				if len(row)==1:
					row=row[0]
				row={'so_id':row[0],
				'email':row[1],
				'address':row[2]}
			
			if row['so_id'] is not None:
				row['significant_other']=cur.execute('''SELECT name
					FROM family WHERE id=?''',(row['so_id'],)).fetchone()['name']
			else:
				row['significant_other']=''
		
		if con is not None:
			con.close()
		
		return row
				
	else:
		#just return default values
		return {'significant_other':'','email':'','address':'\n\n\n\n\n'}
		
		
		
		
		