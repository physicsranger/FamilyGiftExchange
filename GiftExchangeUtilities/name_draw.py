import os,sqlite3,time
import numpy as np
from functools import reduce
from GiftExchangeUtilities.management import get_member_id

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
			print(f'Year {new_year} has an invalid format, should be\
			 the four-digit year, e.g., 2023.\nNot doing anything.')
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
				print(f'Exchange info exists for {new_year}, overwrite flag\
				 set to True, will generate new gift exchange assignments.')
				 
			else:
				print(f'Exchange info exists for {new_year}, overwrite flag\
				 set to false, will not do anything.')
				 
				return False
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
			print('Make sure you have populated your family table and\
			 that you did not accidentally skip too many family members.')
			print(f'Not generating gift exchange assignments for {new_year}')
			return None
		
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
				
				if max([member_info[name]['excludes'].count(exclude)\
				 for exclude in member_info['name']['excludes']])>1:
					#have a duplicate
					new_excludes=member_info[name]['excludes'][0]
					for exclude in member_info[name]['excludes'][1:]:
						if exclude not in new_excludes:
							new_excludes.append(exclude)
					if len(new_excludes)==len(names):
						print(f'ERROR: exclude list for {name} excludes\
						 all family members, even after removing duplicates.')
						 
						print('Consider excluding fewer previous year giftees.')
						BAIL=True
					else:
						member_info[name]['excludes']=new_excludes
		if BAIL:
			print('Will not generate new gift exchange assignments, see output messages.')
			return False
		
		#now we need to actually do the random draws
		#taking into account the exclusion info
		exchange_draws=get_draws(member_info)
		
		#if we get a None-type object returned, something went wrong
		if exchange_draws is None:
			print('Was unable to produce gift exchange draws\
			 satisfying all exclusion requirements.')
			 
			print('Please check output messages, database tables,\
			 and choice of number of previous giftees to exclude and try again.')
			 
			return False
		
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
	return True

def output_giftee_assignments(database_file,year=None):
	#if no year was provided, assume it is the current year
	if year is None:
		year=time.localtime().tm_year
	#otherwise, check the input year to make sure it is a valid format
	elif not valid_year(str(new_year)):
			print(f'Year {year} has an invalid format,\
			 should be the four-digit year, e.g., 2023.\nNot doing anything.')
			return
	
	with sqlite3.connect(database_file) as con:
		con.row_factory=sqlite3.Row
		cur=con.cursor()
		
		rows=cur.execute(f'''SELECT id,Year_{year}
		FROM exchange''').fetchall()
		
		if rows is None:
			print(f'Uh oh! Gift exchange does not appear to have\
			 been generated for {year}.\nWill not produce assignment files.')
			return
		
		for row in rows:
			if row[f'Year_{year}'] is not None:
				produce_assignment_files(database_file,row['id'],
				    row[f'Year_{year}'],year,cur)
		
		print(f'Gift exchange assignment files successfully generated for {year}')
		print(f'Files can be found in\
		{os.path.join(os.path.dirname(database_file),"Year_"+str(year))}.')
		
	return
					
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
		con.row_factor=sqlite3.Row
		cur=con.cursor()
	else:
		con=None
	
	#get the directory
	gift_exchange_dir=os.path.join(os.path.dirname(database_file),str(year))
	if not os.path.exists(gift_exchange):
		os.mkdir(gift_exchange)
	
	#look up the names and the giftee address info
	###I need to experiment with this, can I always be sure
	###that the gifter will be first, simply because they were listed first
	###in the input values?
	rows=cur.execute('''SELECT name,address_id
	FROM family
	WHERE id IS IN (?,?)''',(gifter_id,giftee_id)).fetchall()
	
	gifter=rows[0]['name']
	giftee=rows[1]['name']
	giftee_address_id=rows[1]['address_id']
	
	assignment_file_name=f'{gifter}_{year}.txt'
	
	if giftee_address_id is not None:
		giftee_address=cur.execute('''SELECT address
		FROM addresses
		WHERE id=?''',(giftee_address_id,)).fetchone()[0]['address']
	
	else:
		giftee_address="No address indicated in database.\nConsult family\
		 member in charge of the exchange."
	
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
		print(f'Requested to exclude possible giftees for each family member from\
		{num_exclude} previous years, but there are only {len(years)} years in the\
		exchange.')
		print('We will only exclude giftees for each family member using {len(years)}\
		years.')
		num_exclude=len(years)
	years_to_exclude=[year[0] for year in years[:num_exclude]]
	
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

#################################################################################
##functions to query the exchange table to view previous and current name draws
##and to populate the exchange table with info from previous years before the
##database was used to manage name draws
#################################################################################

def get_previous_years(database_file,number_to_view=1,include_latest=False,cur=None):
	#do a few sanity checks on the number_to_view_parameter
	if number_to_view<=0:
		raise ValueError(f'Requested non-sensical {number_to_view} years to view.')
	if not isinstance(number_to_view,int):
		raise TypeError(f'"number_to_view" argument must be type integer,\
		 not {type(number_to_view)}')
	
	#allow for variation in how the function is called
	if not isinstance(cur,sqlite3.Cursor):
		con=sqlite3.connect(database_file)
		cur=con.cursor()
	else:
		con=None
	
	#get the years we have to work with
	years=[descr[0] for descr in\
	    cur.execute('SELECT * FROM exchange').description if descr[0]!='id']
	#sort the years in reverse order
	years.sort(reverse=True)
	
	#if we're not including the latest year, ditch it
	if not include_latest:
		years=years[1:]
	
	#get the years we want
	years=years[:number_to_view]
	
	#let's go ahead and sort them again to have a more normal viewing order
	years.sort()
	
	#build the query, we want the id column and the column for each year
	query='SELECT id'
	query+=reduce(lambda s1,s2:f'{s1}, Year_{s2}',years)
	qury+=' FROM exchange'
	
	#this should give me tuples with id,year_0,year_1,..
	exchange_rows=cur.execute(query).fetchall()
	
	#now we want a name lookup dictionary
	name_rows=cur.execute('''SELECT id, name
	FROM family''').fetchall()
	
	name_lookup=dict(name_rows)
	#get a list of the names to make things easier for calling functions
	names=list(name_lookup.values())
	
	#now, make a nested dictionary to contain the draw info for each year
	previous_draws={}
	
	#need to have a way to deal with ids in the previous exchange year
	#for family members who have been removed, so we can't be as succinct
	#using the .get will return None if id is not in the lookup, but we
	#don't want a None type for a key
	for year_idx,year in enumerate(years):
		previous_draws[year]={}
		for row in exchange_rows:
			if row[0] in name_lookup.keys():
				previous_draws[year][name_lookup.get(row[0])]=\
				name_lookup.get(row[year_idx+1])
			else:
				previous_draws[year]['UNKNOWN']=name_lookup.get(row[year_idx+1])
				if 'UNKNOWN' not in names:
					names.append('UNKOWN')
	
	if con is not None:
		con.close()
	
	return previous_draws,names


def add_previous_year(database_file,year,draws,cur=None):
	#check to make sure that the year input is valid
	if valid_year(str(year)):
		if not isinstance(cur,sqlite3.Cursor):
			con=sqlite3.connect(database_file)
			cur=con.cursor()
		else:
			con=None
		
		id_lookup=dict((name,get_member_id(None,name,cur)) for name in draws.keys())
		
		#add the new year to the exchange database
		add_new_year(None,year,cur)
		
		#now fill the database
		query=f'UPDATE exchange SET Year_{year}=? WHERE id=?'
		for name in draws.keys():
			cur.execute(query,(name,draws[name]))
		
		if con is not None:
			con.commit()
			con.close()
	
	else:
		print(f'{year} is not a valid 4-digit year value')
		    
	




