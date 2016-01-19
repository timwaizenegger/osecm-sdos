#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: tim

This module contains SDOS-frontends, i.e. the classes that offer access to SDOS
the frontends will then use methods from the SDOS core and finally use a backend to store/retrieve data
'''
from tim.sdos.swift import SwiftBackend
from tim.sdos.crypto.DataCrypt import DataCrypt
from tim.sdos.crypto import CryptoLib
from tim.sdos.core.KeyCascade import Cascade
from tim.sdos.core import Mapping, CascadePersistence, MappingPersistence

class DirectFrontend(object):
	'''
	This frontend directly sotes files in the backend without modification/additional stuff 
	'''


	def __init__(self, containerName):
		'''
		Constructor
		'''
		self.si = SwiftBackend.SwiftBackend()
		self.containerName = containerName
	
	def finish(self):
		pass	
		
	def putObject(self, o, name):
		self.si.putObject(container=self.containerName, name=name, dataObject=o)
		
	def getObject(self, name):
		return self.si.getObject(container=self.containerName, name=name)
	
	def deleteObject(self, name):
		self.si.deleteObject(container=self.containerName, name=name)
		
		
###############################################################################
###############################################################################


class CryptoFrontend(object):
	'''
	This frontend encrypts the objects with a predefined key before storing them.
	When retrieving objects, the same key is used to decrypt the data again.
	No key management/SDOS mgmt is performed
	'''


	def __init__(self, containerName):
		'''
		Constructor
		'''
		self.si = SwiftBackend.SwiftBackend()
		self.containerName = containerName
		
	def finish(self):
		pass
		
	def putObject(self, o, name):
		key = CryptoLib.digestKeyString('keeey')
		c = DataCrypt(key).encryptBytesIO(plaintext=o)
		self.si.putObject(self.containerName, name, c)
	
	def getObject(self, name):
		key = CryptoLib.digestKeyString('keeey')
		c = self.si.getObject(container=self.containerName, name=name)
		return DataCrypt(key).decryptBytesIO(ciphertext=c)
	
	def deleteObject(self, name):
		self.si.deleteObject(container=self.containerName, name=name)
		
###############################################################################
###############################################################################


class SdosFrontend(object):
	'''
	This frontend implements the SDOS functionality
	'''


	def __init__(self, containerName):
		'''
		Constructor
		'''
		self.si = SwiftBackend.SwiftBackend()
		self.containerName = containerName
		
		containerNameSdosMgmt = '{}.sdos'.format(containerName)
		
		#mappingStore = MappingPersistence.LocalFileMappingStore()
		mappingStore = MappingPersistence.SwiftMappingStore(containerNameSdosMgmt=containerNameSdosMgmt, swiftBackend=self.si)
		keySlotMapper = Mapping.KeySlotMapper(mappingStore=mappingStore)
		
		#partitionStore = CascadePersistence.LocalFilePartitionStore()
		partitionStore = CascadePersistence.SwiftPartitionStore(containerNameSdosMgmt=containerNameSdosMgmt, swiftBackend=self.si)
		self.cascade = Cascade(partitionStore=partitionStore, keySlotMapper=keySlotMapper)
		
	def finish(self):
		self.cascade.finish()
		pass
		
	def putObject(self, o, name):
		key = self.cascade.getKeyForNewObject(name)
		
		c = DataCrypt(key).encryptBytesIO(plaintext=o)
		self.si.putObject(self.containerName, name, c)
	
	def getObject(self, name):
		key = self.cascade.getKeyForStoredObject(name)
				
		c = self.si.getObject(container=self.containerName, name=name)
		return DataCrypt(key).decryptBytesIO(ciphertext=c)
	
	def deleteObject(self, name):
		# self.cascade.deleteObjectKey(name)
		self.cascade.secureDeleteObjectKey(name)
		self.si.deleteObject(container=self.containerName, name=name)
		
###############################################################################
###############################################################################
		
		
		
		
		
		
		
		
