import time

current_time = int(time.time())
block_size = 4096
File_path = "/Users/Tammy/Documents/Operating System/FS/fusedata." 
maxBlocks = 10000

def csefsck():
	check_dev_ID()
	check_time()
	check_free_block_list()
	check_directory()
	check_directory_linkcount()
	check_indirect()


def get_block(block_num):
	block = open(File_path + str(block_num), 'r')
	content = block.read()
	content = initilize_string(content)
	block.close()
	return content	

	#initialize the file name to an appropriate string
def initilize_string(str):
	# remove all the { and }
	str = str.lstrip('{')
	str = str.rstrip('}')
	if 'filename_to_inode_dict' in str:
		str = str.replace('{',' ')
		str = str.replace('}',' ')
	if 'indirect' in str:
		str = str.replace('location',',location')
	# remove the useless whitespace
	str = str.strip()
	str = str.replace(' ','')
	str = str.replace(':',',')
	str = str.split(',')
	return str


#check the devID
def check_dev_ID():
	super_block = get_block(0)
	sb_dev_id = int(super_block[super_block.index('devId')+1])
	if sb_dev_id != 20:
		print('devId is wrong')
		index = int(super_block.index('devId') /2)
		correct_devId = 'devId:' + str(20)
		modify_value(0, index, correct_devId)
		print('devId has been updated')
	else:
		print('devId is right')


#check the creation time,mtime and ctime, they must less than current time
def check_time ():
	for i in range(26,maxBlocks+1):
		current_block = get_block(i)
		if 'ctime' in current_block:
			b_ctime = int(current_block[current_block.index('ctime')+1])
			b_mtime = int(current_block[current_block.index('mtime')+1])
			if b_ctime <=current_time:
				print('The ctime of block',i,' is',b_ctime)
			elif b_ctime > current_time:
				print('ERROR: ctime of block',i,'  is invalid') 
			if b_mtime <=current_time:
				print('The mtime of block',i,'is',b_mtime)
			elif b_mtime > current_time:
				print('ERROR: The mtime of block',i,'  is invalid') 
	super_block = get_block(0)
	sb_creationTime = int(super_block[super_block.index('creationTime')+1])
	if sb_creationTime > current_time:
		print('FALSE: creationTime is invalid') 



def check_free_block_list():
	def add_free_block(i):
		obj = get_block(freeEnd)
		obj.append(i)
		temp = ''
		for k in obj:
			temp += str(k) + ","
		f = open(File_path + str(freeEnd), 'w')
		f.write(temp[:-1])
		f.close()
		return f

	def kick_out_block(m):
		#at first we need to find the block, used to contains free block list, contains the usd block number
		for i in range (freeStart, freeEnd+1):
			this_free_block_list = get_block(i)
			if str(m) in this_free_block_list:
				index=int(this_free_block_list.index(str(m)))
				temp1 = this_free_block_list[0: (index)]
				temp2 = this_free_block_list[(index+1):]
				temp3 = temp1 + temp2
				temp = ''
				for k in temp3:
					temp += str(k) + ","
				this_free_block_list = open(File_path +str(i),'w')
				this_free_block_list.write(temp[:-1])
				this_free_block_list.close()
		return this_free_block_list

	super_block = get_block(0)
	freeStart = int(super_block[super_block.index('freeStart')+1])
	freeEnd = int(super_block[super_block.index('freeEnd')+1])
	# build two lists to save the blocks used and free blocks
	free_block_list = set()
	used_block_list = set()
	used_block_list.add(0) # add superblock to the used block list
	# build the free block list
	# add the free block list into used block list
	for i in range (freeStart, freeEnd + 1):
		free_block_list_block = get_block(i)
		used_block_list.add(i)
		for j in free_block_list_block:
			free_block_list.add(j)
	#add other used block into the used block list
	for i in range (freeEnd+1,maxBlocks+1):
		current_block = get_block(i)
		#add root directory block and the files refered in root directory to the used list
		if 'filename_to_inode_dict' in current_block:
			used_block_list.add(i)
			if ('f' in current_block):
				used_block_f = int(current_block[current_block.index('f')+2])
				used_block_list.add(used_block_f)
			if ('d' in current_block):
				used_block_d = int(current_block[current_block.index('d')+2])
				used_block_list.add(used_block_d)
		#add the used filr into the used block list
		if 'location' in current_block:
			used_block_f_location = int(current_block[len(current_block) - 1])
			used_block_list.add(used_block_f_location)
			content_block = get_block(used_block_f_location)
			content_block_number = int(content_block[len(content_block) -1])
			used_block_list.add(content_block_number)
	no_modify = 1 #use this parameter to mark if something need to be modified in free block list
	for m in range (0,maxBlocks+1):
		# 3)a: check if the free block list contains all the free blocks
		if m not in used_block_list:
			if str(m) not in free_block_list:
				print('ERROR:',(m),' is a free block and is not list in the free block list')
				add_free_block(m)
				print('This free block has been add to the free block list')
				no_modify = 0
		# 3)b: check if it has any used block listed in free block list
		if str(m) in free_block_list:
			if m in used_block_list:
				print('ERROR:',m,' has been used and should not list in free block list')
				kick_out_block(m)
				print('This block has been kicked out of the free block list')
				no_modify = 0
	if no_modify == 1:
		print('Congratulation! The free block list is correct.')

#requirement4
def check_directory():
	#this initialize_dir func is used to help pick up the filename_to inode_dict information
	def initialize_dir(i):
		current_dir = open(File_path + str(i), 'r')
		obj_dir = current_dir.read()
		obj_dir = obj_dir.lstrip('{')
		obj_dir = obj_dir.rstrip('}')
		obj_dir = obj_dir.replace(' ','')
		obj_dir = obj_dir.split(':')
		return obj_dir
	super_block = get_block(0)
	root = int(super_block[super_block.index('root')+1])
	for i in range (root,maxBlocks+1):
		current_block = get_block(i)
		if 'filename_to_inode_dict' in current_block:
			#check if the current value is correct
			if '.' in current_block:
				index1 =int(current_block.index('.')) + 1
				if (current_block[index1] != str(i)):
					print ('ERROR:The current block number in directory',i,' is wrong')
					current_dir = initialize_dir(i)
					if '{d' in current_dir:
						correct_cur_num = 'filename_to_inode_dict: {d:.:' + str(i)
						index3 = int(current_block.index('linkcount') / 2) + 1
					else :
						correct_cur_num = 'd:.:' + str(i)
						index3 = int(current_block.index('linkcount') / 2) + 3
					modify_value(i,index3, correct_cur_num)
					print ('The current block number in this directory has been update')
			if '..' in current_block:
				index2=int(current_block.index('..')) + 1
				if (current_block[index2] != str(root)):
					print ('ERROR:The parent block number in directory ',i,' is wrong')
					index4 = int(current_block.index('linkcount') / 2) + 3
					correct_cur_num = 'd:..:' + str(root)
					modify_value(i,index4, correct_cur_num)
					print('The parent block number in this directory has been update')
	return

#requirement5
def check_directory_linkcount():
	for i in range(26,maxBlocks + 1):
		current_block = get_block(i)
		if 'filename_to_inode_dict' in current_block:
			index = int(current_block.index('linkcount')) +1
			linkcount = current_block[index]
			# get the number of actual link count in this directory
			index1 = int (current_block.index('filename_to_inode_dict'))
			num = len(current_block) - index1 - 1
			actual_linkcount =int(num/3)
			if str(actual_linkcount) != linkcount:
				print('ERROR:The value of linkcount in directory',i,' is wrong')
				index2 = int(index/2)
				correct_linkcount = 'linkcount:' + str(actual_linkcount)
				modify_value(i,index2, correct_linkcount)
				print('The actual linkcount has been set to linkcount')
			else:
				print('The linkcount of directory',i, 'is correct')


#requirement6
#requirement7
def check_indirect():
	for i in range(26,maxBlocks + 1):
		current_block = get_block(i)
		if 'indirect' in current_block:
			indirect_val = int (current_block[current_block.index('indirect')+1])
			if int(current_block[1]) <= block_size:
				if indirect_val == 0:
					continue
				else:
					print('ERROR:The indirect of file ',i,'is wrong, because the size is smaller than block size')
					index = int(current_block.index('indirect') /2)
					correct_indirect = 'indirect:' + str(0)
					modify_value(i, index, correct_indirect)
					print('Indirect has been updated to 0.')
			else:
				if indirect_val == 1:
					continue
				else:
					print('ERROR:The indirect of file ',i,'is wrong')
					index = int(current_block.index('indirect') /2)
					correct_indirect = 'indirect:' + str(1)
					modify_value(i, index, correct_indirect)
					print('Indirect has been updated to 1.')

def modify_value(block_num, index, correct_val):
	block = open(File_path + str(block_num), 'r')
	obj1 = block.read()
	if 'indirect' in obj1:
		obj1 = obj1.replace('location',',location')
	obj1 = obj1.split(',')
	block.close()
	temp1 = obj1[0: (index)]
	temp2 = obj1[(index+1):]
	temp1.append(correct_val)
	temp4 = temp1 + temp2
	temp =str() 
	for k in temp4:
		temp += str(k) + ","
	obj1 = open(File_path + str(block_num),'w')
	obj1.write(temp[:-1])
	obj1.close()
	return obj1


if __name__ == '__main__':
	csefsck()
