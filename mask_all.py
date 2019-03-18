# Code from https://github.com/hoffmannjordan/size-and-shape-of-insect-wings
# A version of this code is available at: https://github.com/hoffmannjordan/insect-wing-venation-patterns
# The main image segmentation code can be found at: https://github.com/hoffmannjordan/Fast-Marching-Image-Segmentation

import numpy as np
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from mpi4py import MPI
from scipy import ndimage as ndi
from skimage.morphology import watershed
from skimage.feature import peak_local_max
import scipy.ndimage
from scipy import ndimage
from skimage import measure
import scipy as sp
import time
import glob
import os

def rgb2gray(rgb):
	'''
	Function to convert images from RGB to grayscale
	'''
	r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
	gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
	return gray

	
def import_data(name,cutoff):
	'''
	Function to import a file based on the name and then binarize it based on the cutoff variable.
	Input: file path and cutoff
	Output: binarized matrix of images
	'''
	im = Image.open(name)
	imarray = np.array(im)
	print np.shape(imarray)
	#exit()
	imarray = rgb2gray(imarray)
	imarray = scipy.ndimage.filters.gaussian_filter(imarray,1.0)
	print np.shape(imarray)
	dim1,dim2 = np.shape(imarray)
	data = np.zeros((dim1,dim2))
	for i in xrange(dim1):
		for j in xrange(dim2):
			data[i][j] = 1-imarray[i][j]
	data += np.abs(np.amin(data))
	data = data/np.amax(data)
	tmp = np.zeros(np.shape(data))
	for i in xrange(dim1):
		for j in xrange(dim2):
			if data[i][j] > cutoff:
				tmp[i][j] = 1.0
	return tmp

def import_data2(orig):
	'''
	Second function to import a file based on the name and then binarize it based on the cutoff variable.
	'''
	im = Image.open(orig)
	imarray = np.array(im)
	#imarray = rgb2gray(imarray)
	imarray = scipy.ndimage.filters.gaussian_filter(imarray,1.25)

	print np.amax(imarray)
	print np.amin(imarray)

	imarray = imarray/float(np.amax(imarray))

	print np.amax(imarray)
	print np.amin(imarray)

	'''plt.imshow(imarray)
	plt.title('grayscale')
	plt.show()'''
	#print imarray[500]
	dim1,dim2 = np.shape(imarray)
	tmp = np.ones(np.shape(imarray))

	for i in xrange(dim1):
		for j in xrange(dim2):
			if imarray[i][j] > .9:
				tmp[i][j] = 0

	print tmp[0]
	print np.shape(imarray)

	'''plt.imshow(tmp)
	plt.title('grayscale after thresholding')
	plt.show()'''
	return tmp #imarray

def breadth_search(start_positionx, start_positiony):
	'''
	Perform a BFS to remove improperly removed data.
	'''
	a,b = np.shape(tmp)
	checked = {}
	to_check = []

	to_check.append([start_positionx, start_positiony])

	while len(to_check) != 0:

		next_to_checkx, next_to_checky = to_check.pop(0)

		if not (checked.get(tuple([next_to_checkx, next_to_checky]), None)) and (tmp[next_to_checkx, next_to_checky] == 0):
		#if [next_to_checkx, next_to_checky] not in checked:

			if next_to_checkx+1 < a:
				to_check.append([next_to_checkx+1, next_to_checky])
			if next_to_checky+1 < b:
				to_check.append([next_to_checkx, next_to_checky+1])
			if next_to_checkx-1 >= 0:
				to_check.append([next_to_checkx-1, next_to_checky])
			if next_to_checky-1 >= 0:
				to_check.append([next_to_checkx, next_to_checky-1])

			checked[tuple([next_to_checkx, next_to_checky])] = True
			#checked.append([next_to_checkx, next_to_checky])

			tmp2[next_to_checkx, next_to_checky] = 0

			print "length of to check:", len(to_check)
			print "length of checked:", len(checked)

	return tmp2

def refine_mask(data, mask):
	'''
	Do the refinement of the mask.
	'''
	mask2 = np.copy(mask)
	#not the most efficient way
	xs,ys = np.where(mask == 0)
	print 'STARTED WITH '+str(len(xs))
	'''plt.imshow(mask2)
	plt.title('original mask')
	plt.show()'''

	tocheck = []
	for i in xrange(len(xs)):
		tocheck.append(data[xs[i]][ys[i]])
	tocheck = np.unique(tocheck)

	print 'to check is: \n'
	print 'tocheck ids:', tocheck

	dim1 , dim2 = np.shape(data)
	for i in xrange(dim1):
		for j in xrange(dim2):
			if data[i][j] in tocheck:
				mask2[i][j] = 0
	xs,ys = np.where(mask2 == 0)
	print 'ENDED WITH '+str(len(xs))
	return mask2

if __name__=='__main__':
	'''
	Import all segmented files and refine them as needed. 
	'''
	file_list_seg = glob.glob("./*_FMM_seg2.csv")
	#file_list_orig = glob.glob("./*.tiff")

	for filetodo in file_list_seg:
		#spec = filetodo.split('/')[1].split('.')[0]
		#spec2 = filetodo.split('/')[1].split('_')[0]

		orig_data_scan = np.genfromtxt(filetodo, delimiter=',')
		orig_data_scan = np.asarray(orig_data_scan)
		orig_data_scan = orig_data_scan.astype(int)

		grayscale_data_scan = import_data('./lw.png',0.03)
		#grayscale_data_scan = import_data2('./LIBELLULIDAE-erythemis-simplicicollis-RF.tiff')
		#tmp = create_tmp_mask(orig_data_real)
		tmp = grayscale_data_scan

		tmp2 = np.ones(np.shape(orig_data_scan))

		mask = breadth_search(0, 0)
		print "DID MASK"
		mask = refine_mask(orig_data_scan,mask)

		new_file = np.multiply(mask, orig_data_scan)

		'''plt.imshow(new_file)
		plt.title('final')
		plt.show()'''

		np.savetxt('./LWw.csv', new_file.astype(int), fmt='%i', delimiter=',')
		#os.remove(filetodo)