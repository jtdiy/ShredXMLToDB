import xml.etree.ElementTree

keys = dict()

def shredTables(schemaBranch, dataBranch):
	schemaTables = schemaBranch.findall("./table")
	for schemaTable in schemaTables:
		#for key in schemaTable.attrib.keys():
		#	print(key + ' = ' + schemaTable.attrib[key])

		tableName = schemaTable.attrib['name']
		tableXPath = schemaTable.attrib['xpath']
		
		Columns = schemaTable.findall("./column")

		Rows = dataBranch.findall(tableXPath)
		for Row in Rows:
			print('Table: ' + tableName)

			colDict = dict()

			for Column in Columns:
				
				columnName = Column.attrib['name']

				#A column may or may not have an keyname attribute.
				try:
					columnKeyName = Column.attrib['keyname']
					keys.setdefault(columnKeyName, 0)
					keys[columnKeyName]+=1
				except:
					columnKeyName = ''

				#A column may or may not have an keyvalue attribute.
				try:
					columnKeyValue = Column.attrib['keyvalue']
					keys.get(columnKeyValue)
					
				except:
					columnKeyValue = ''

				#A column may or may not have an XPath attribute.
				try:
					columnXPath = Column.attrib['xpath']
					try:
						columnData = Row.find(columnXPath)
					except:
						print('    Column xpath exception: ' + columnXPath)
						columnData=  Row.find('')
				except:
					columnXPath = ''


				#Determine whether the column value is coming via XPath or keyvalue or keyname.
				if columnKeyName > '':
					columnValue = str(keys.get(columnKeyName))
				elif columnKeyValue > '':
					columnValue = str(keys.get(columnKeyValue))
				else:
					try:
						columnValue = "'" + columnData.attrib['value'] + "'"
					except:
						columnValue = 'NULL'

				print('    Column:', columnName, ' = ', columnValue)

				colDict[columnName]= columnValue

			sql = genRowSQL('insert', tableName, colDict)
			print(sql)
			#print(keys)

			#Recurse.
			shredTables(schemaTable, Row)

def genRowSQL(genType, tableName, colDict):
	sql = genType + ' ' + tableName
	if genType == 'insert':
		sql = genType + ' into ' + tableName
		colList = ''
		valList = ''
		for key in colDict:
			colList += key + ', '
			valList += colDict[key] + ', '

		#Strip the last ', ' off the lists.
		colList = colList[0:len(colList)-2]
		valList = valList[0:len(valList)-2]

		sql += '(' + colList + ') values (' + valList + ')'

	elif genType == 'update':
		sql = genType + ' ' + tableName + ' set '
		for key in colDict:
			sql += key + ' = ' + colDict[key] + ', '

		#Strip the last ', ' off the sql.
		sql = sql[0:len(sql)-2] + ' where ...'
	
	return sql

datatree = xml.etree.ElementTree.parse('TSData.xml')
dataroot = datatree.getroot()

schematree = xml.etree.ElementTree.parse('ShredXmlToDb.xml')
schemaroot = schematree.getroot()

shredTables(schemaroot, dataroot)