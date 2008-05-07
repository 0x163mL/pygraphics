#import unittest
#import os.path
from TestExecute import *
from picture import *
import nose
#from media import *

###############################################################################
# Setup/Teardown Functions
##############################################################################
def setup_function():
	'''A setup function to be called by nose at the beginning of every test.
	Creates global variables used in most tests.'''
	global pict, image_types, blessed_save_loc_prefix, save_loc_prefix
	pict = Picture()
	image_types = ['bmp', 'gif', 'jpg']
	blessed_save_loc_prefix = resi('saved.')
	save_loc_prefix = resi('saved.tmp.')


def teardown_function():
	'''A teardown function to be called by nose at the end of every test.
	Destroys global variables created in setup.'''
	global pict, image_types, blessed_save_loc_prefix, save_loc_prefix
	del pict, image_types, blessed_save_loc_prefix, save_loc_prefix


###############################################################################
# Helper functions
##############################################################################

def ensure_images_equal(filename1, filename2):
	# helper function to ensure that two image files are identical
	p1 = Picture(); p1.load_image(filename1)
	p2 = Picture(); p2.load_image(filename2)
	ensure_pictures_equal(p1, p2)
	
def ensure_pictures_equal(p1, p2):
	# helper function to ensure that all the pixels are identical
	pixels1 = p1.get_pixels()
	pixels2 = p2.get_pixels()
	if not len(pixels1) == len(pixels2):
		raise ValueError('Improper dimensions)')
	for idx in range(len(pixels1)):
		px1 = pixels1[idx]
		px2 = pixels2[idx]
		if not (px1.get_red() == px2.get_red() and
			px1.get_green() == px2.get_green() and
			px1.get_blue() == px2.get_blue()):
			raise ValueError('Pictures not equal')
		
def ensure_pictures_not_equal(p1, p2):
	# helper function to ensure that all the pixels are identical
	pixels1 = p1.get_pixels()
	pixels2 = p2.get_pixels()
	if not len(pixels1) == len(pixels2):
		raise ValueError('Improper dimensions)')
	for idx in range(len(pixels1)):
		px1 = pixels1[idx]
		px2 = pixels2[idx]
		if not (px1.get_red() == px2.get_red() and
			px1.get_green() == px2.get_green() and
			px1.get_blue() == px2.get_blue()):
			return
	raise ValueError('Pictures equal for')	
	
def ensure_picture_has_color(picture, color):
	pixels = picture.get_pixels()
	for pixel in pixels:
		if not ((pixel.get_red() == color.get_red())
			and (pixel.get_green() == color.get_green())
			and (pixel.get_blue() == color.get_blue())):
			raise ValueError('Picture does not have solid color')

###############################################################################
# Test functions
##############################################################################

@nose.with_setup(setup_function, teardown_function)		
def test_empty_constructor():
	# empty constructor builds new picture
	assert pict.disp_image == None, 'New Picture contains display image'
	assert pict.win_active == 0, 'New Picture is active'

@nose.with_setup(setup_function, teardown_function)	
def test_create_image_zero_dimensions():
	# create empty image with zero dimensions
	pict.create_image(0, 0)
	assert pict.surf.size == (0, 0), "Wrong Picture dimensions"
	assert pict.get_width() == 0, "Wrong number of Picture pixels"
	assert pict.filename == '', "Non-empty filename for empty image"
	assert pict.title == 'None', "Pict title was, " + str(pict.title)

@nose.with_setup(setup_function, teardown_function)	
def test_create_image_questionable_dimensions():
	# create empty image with questionable dimensions
	# TODO: should we even be creating the surface if one of the sides <= 0?
	pict.create_image(0, 1) # what is a zero by 1 image?
	assert pict.surf.size == (0, 1), "Wrong Picture dimensions"
	assert pict.get_width() == 0, "Wrong number of Picture pixels"
	assert pict.filename == '', "Non-empty filename for empty image"
	assert pict.title == 'None', "Pict title was, " + str(pict.title)

@nose.with_setup(setup_function, teardown_function)	
def test_create_image_invalid_dimensions():
	# create empty image with invalid dimensions
	for x in range(-1, 1, -1):
		for y in range(-1, 1, -1):
			if y != 0 and x != 0:
				nose.tools.assert_raises(ValueError, pict.create_image, x, y)

@nose.with_setup(setup_function, teardown_function)	
def test_load_image_non_existant_file():
	# load a non-existant file
	nose.tools.assert_raises(ValueError, pict.load_image, resi("nosuchfile"))
	
@nose.with_setup(setup_function, teardown_function)	
def test_load_image():
	# load a normal image file (absolute, relative)
	# absolute files 
	filename_prefix = 'white.'
	failed = False
	error_res = ''
	# for each of the supported file types
	for suffix in image_types:
		filename = filename_prefix + suffix
		file = resi(filename)
		# try and load the test file of that type
		try:
			pict.load_image(file)
			assert pict.filename == file, "Improper filename (%s) for loaded image" % pict.filename
			assert pict.title == os.path.join('images', filename), "Improper title (%s) for loaded image" & pict.title
			# ensure correct dimensions and depth
			assert pict.surf.size == (50, 50), "Invalid Picture dimensions"
			assert pict.get_width()*pict.get_height()*len(pict.pixels[0,0]) == (50*50*3)
		except ValueError, e:
			error_res += 'Error loading images of type: ' + suffix + " (" + str(e) + ")\n"
			failed = True
	# there was at least one error loading the test files
	if failed:
		assert False, error_res
	# TODO: to test relative files, we need to be able to set the global default media directory

@nose.with_setup(setup_function, teardown_function)	
def test_to_string_invalid_image():	
	# test toString
	nose.tools.assert_raises(AttributeError, str, pict)
	nose.tools.assert_raises(ValueError, pict.create_image, -1, -1)
	nose.tools.assert_raises(AttributeError, str, pict)

@nose.with_setup(setup_function, teardown_function) 
def test_to_string_dimensionless_image():	
	# test toString
	pict.create_image(0, 0)
	assert str(pict) == 'Picture, filename  height 0 width 0', "Invalid str for dimensionless image"

@nose.with_setup(setup_function, teardown_function)
def test_to_string():
	# test that toString is printing correct values
	filename_prefix = 'white.'
	failed = False
	error_res = ''
	# for each of the supported file types
	for suffix in image_types:
		filename = filename_prefix + suffix
		file = resi(filename)
		# try and load the test file of that type
		try:
			pict.load_image(file)
			assert str(pict) == "Picture, filename " + file + " height 50 width 50", "Invalid str conversion, str was " + str(pict)
		except ValueError, e:
			error_res += 'Error loading images of type: ' + suffix + " (" + str(e) + ")"
			failed = True
	# there was at least one error loading the test files
	if failed:
		assert False, error_res

@nose.with_setup(setup_function, teardown_function)
def test_title():
	# test title setters/getters
	# setting after initial load
	assert pict.get_title() == 'Unnamed', "Improper initial title"
	pict.set_title('')
	assert pict.get_title() == '', "Improper title " + pict.get_title()
	pict.set_title('asdf')
	assert pict.get_title() == 'asdf', "Improper title " + pict.get_title()
	# setting after creating a new image
	pict.create_image(0, 0)
	assert pict.get_title() == 'None', "Improper title " + pict.get_title()
	pict.set_title('asdf')
	assert pict.get_title() == 'asdf', "Improper title " + pict.get_title()
	# setting after loading an image
	pict.load_image(resi('white.bmp'))
	assert pict.get_title() == os.path.join('images', 'white.bmp'), "Improper title " + pict.get_title()
	pict.set_title('asdf')
	assert pict.get_title() == 'asdf', "Improper title " + pict.get_title()
	
@nose.with_setup(setup_function, teardown_function)
def test_get_image_invalid_image():
	# test get_image on an invalid image
	# fails when no/invalid image created
	nose.tools.assert_raises(AttributeError, pict.get_image)
	nose.tools.assert_raises(ValueError, pict.create_image, -1, -1)
	nose.tools.assert_raises(AttributeError, pict.get_image)
	pict.create_image(0, 0)
	nose.tools.assert_raises(ValueError, pict.get_image)

@nose.with_setup(setup_function, teardown_function)
def test_get_image():
	# ensure that the Image has the same properties as the Picture		
	# test created blank image and loaded image
	expected_color = [(0, 0, 0), (255, 255, 255)]
	for idx in range(len(expected_color)):
		# create/load picture
		tester_pict = Picture()
		if idx == 0:
			tester_pict.create_image(50, 50)
		elif idx == 1:
			tester_pict.load_image(resi('white.bmp'))
		# convert to PIL image and ensure properties are the same
		image = tester_pict.get_image()
		assert image.mode == 'RGB', "Improper image color bands"
		assert image.size == (50, 50), "Improper image size"
		# ensure all the pixels are of the correct color
		correct_color = True
		image_pixels = list(image.getdata())
		for pixel in image_pixels:
			if not pixel == expected_color[idx]:
				correct_color = False
		if not correct_color:
			assert False, 'Invalid image colors (' + str(idx) + ')'
		del tester_pict, image, image_pixels	

@nose.with_setup(setup_function, teardown_function)
def test_get_width_height_invalid_image():
	# test get_width/get_height for an invalid image
	nose.tools.assert_raises(AttributeError, pict.get_width)
	nose.tools.assert_raises(AttributeError, pict.get_height)
	#test after invalid construction
	nose.tools.assert_raises(ValueError, pict.create_image, -1, -1)
	nose.tools.assert_raises(AttributeError, pict.get_width)
	nose.tools.assert_raises(AttributeError, pict.get_height)

@nose.with_setup(setup_function, teardown_function)
def test_get_width_height():
	# test get_width/get_height for normal images
	# create image
	dimension = [(0,0), (50, 50), (0, 5), (10, 0)]
	for idx in range(len(dimension)):
		tester_pict = Picture()
		w = dimension[idx][0]
		h = dimension[idx][1]
		tester_pict.create_image(w, h)
		assert tester_pict.get_width() == w, 'Invalid image width'
		assert tester_pict.get_height() == h, 'Invalid image height'
		del tester_pict

@nose.with_setup(setup_function, teardown_function)
def test_get_width_height_loaded_image():
	pict.load_image(resi('white.bmp'))
	assert pict.get_width() == 50, 'Invalid image width'
	assert pict.get_height() == 50, 'Invalid image height'

@nose.with_setup(setup_function, teardown_function)	
def test_get_pixel_invalid_image():
	# test get_pixel on an invalid image
	nose.tools.assert_raises(AttributeError, pict.get_pixel, 0, 0)
	nose.tools.assert_raises(AttributeError, pict.get_pixel, -1, -1)
	nose.tools.assert_raises(AttributeError, pict.get_pixel, 50, 50)
	# test after invalid construction
	nose.tools.assert_raises(ValueError, pict.create_image, -1, -1)
	nose.tools.assert_raises(AttributeError, pict.get_pixel, 0, 0)
	nose.tools.assert_raises(AttributeError, pict.get_pixel, -1, -1)
	nose.tools.assert_raises(AttributeError, pict.get_pixel, 50, 50)

@nose.with_setup(setup_function, teardown_function)
def test_get_pixel():
	# test get_pixel on a normal image
	# NOTE: indices are ONE based. Indices are now ZERO based.
	# out of bounds indices
	# IMAGE SIZE: 0
	tester_pict = Picture()
	tester_pict.create_image(0, 0)
	nose.tools.assert_raises(IndexError, tester_pict.get_pixel, 0, 0)	
	nose.tools.assert_raises(IndexError, tester_pict.get_pixel, -1, 0)	
	nose.tools.assert_raises(IndexError, tester_pict.get_pixel, -1, -1)	
	nose.tools.assert_raises(IndexError, tester_pict.get_pixel, 50, 50)	

@nose.with_setup(setup_function, teardown_function)
def test_get_pixel_image_size_one():
	pict.create_image(1, 1)		
	try:
		# should not fail
		#since zero based, pic of size 1 does not wrap around
		#tester_pict.get_pixel(-1, -1) # in python, this wraps to -1 from the left/right
		pict.get_pixel(0, 0) # zero based index for the first pixel
	except IndexError:
		assert False, 'Failed accessing expected pixel'
	nose.tools.assert_raises(IndexError, pict.get_pixel, 2, 2)

@nose.with_setup(setup_function, teardown_function)
def test_get_pixel_image_larger():
	pict.create_image(10, 10)
	try:
		# should not fail
		pict.get_pixel(-9, -9) # last wrap around value
		pict.get_pixel(-1, -1) # wrap around
		pict.get_pixel(0, 0) # first index
		pict.get_pixel(0, 9) 
		pict.get_pixel(9, 0)
		pict.get_pixel(9, 9) # bounds
	except IndexError:
		assert False, 'Failed accessing expected pixel'
	nose.tools.assert_raises(IndexError, pict.get_pixel, 10, 10) # should fail

@nose.with_setup(setup_function, teardown_function)	
def test_get_pixels_invalid_image():		
	# test get_pixels on invalid image
	nose.tools.assert_raises(AttributeError, pict.get_pixels)
	# after invalid image creation attempt
	nose.tools.assert_raises(ValueError, pict.create_image, -1, -1)	# try creating invalid
	nose.tools.assert_raises(AttributeError, pict.get_pixels)

@nose.with_setup(setup_function, teardown_function)
def test_get_pixels():
	# test get_pixels on a normal image
	dimensions = [(0,0), (10, 0), (0, 10), (1, 1), (10, 10)]
	expected_len = [0, 0, 0, 1, 100]
	assert len(dimensions) == len(expected_len), 'Test arrays are mapped 1:1'
	
	for idx in range(len(dimensions)):
		tester_pict = Picture()		
		tester_pict.create_image(dimensions[idx][0], dimensions[idx][1])
		assert len(tester_pict.get_pixels()) == expected_len[idx], \
			'Invalid number of pixels returned (' + str(idx) + ')'
		del tester_pict
	# loaded image
	pict.load_image(resi('white.bmp'))
	assert len(pict.get_pixels()) == 50*50, 'Invalid number of pixels returned'   	

@nose.with_setup(setup_function, teardown_function)	
def test_set_pixels():
	# test set_pixels on an image
	pict.create_image(44,44)
	colors = [Color(0,0,0), Color(255,0,0), Color(255,255,255)]
	try:
		for color in colors:
			pict.set_pixels(color)
			ensure_picture_has_color(pict, color)
	except Exception, e:
		assert False, str(e)
	
@nose.with_setup(setup_function, teardown_function)
def test_clear():
	# test clear
	pict.create_image(44,44)
	black = Color(0,0,0)
	colors = [Color(0,0,0), Color(255,0,0), Color(255,255,255)]
	try:
		for color in colors:
			pict.set_pixels(color)
			pict.clear()
			ensure_picture_has_color(pict, black)
			pict.clear(color)
			ensure_picture_has_color(pict, color)
	except Exception, e:
		assert False, str(e)

@nose.with_setup(setup_function, teardown_function)
def test_write_to_invalid_image():
	nose.tools.assert_raises(AttributeError, pict.write_to, save_loc_prefix + 'tmp')
	nose.tools.assert_raises(ValueError, pict.create_image, -1, -1)
	nose.tools.assert_raises(AttributeError, pict.write_to, save_loc_prefix + 'tmp')

@nose.with_setup(setup_function, teardown_function)
def test_write_to_empty_image():
	pict.create_image(0, 0)
	nose.tools.assert_raises(KeyError, pict.write_to, save_loc_prefix + 'tmp')

@nose.with_setup(setup_function, teardown_function)
def test_write_to_large_image():
	# invalid file types
	pict.create_image(10, 10)
	nose.tools.assert_raises(KeyError, pict.write_to, save_loc_prefix + 'tmp')
	# ensure all of our types hold
	for suffix in image_types:
		try:				
			pict.write_to(save_loc_prefix + suffix)
			# compare with saved copies
#				print "\n"+blessed_save_loc_prefix +'.'+ suffix, save_loc_prefix +'.'+ suffix+"\n"
			ensure_images_equal(blessed_save_loc_prefix + suffix, save_loc_prefix + suffix)
		except KeyError:
			assert False, 'Failed saving created image to (' + suffix + ') files'

@nose.with_setup(setup_function, teardown_function)
def test_write_to_loaded_image():
	# test loaded image		
	tester_save_loc_prefix = resi('white.tmp.')
	blessed_tester_save_loc_prefix = resi('white.')
	for suffix in image_types:
		tester_pict = Picture()
		tester_pict.load_image(blessed_tester_save_loc_prefix + suffix)
		try:
			tester_pict.write_to(tester_save_loc_prefix + suffix)
			# compare with saved copies
			ensure_images_equal(blessed_tester_save_loc_prefix + suffix, tester_save_loc_prefix + suffix)
		except KeyError:
			assert False, 'Failed saving loaded image to (' + suffix + ') files'
		del tester_pict
				
def test_get_picture_with_height():
	# TODO
	print "TBD"

def test_load_and_show_picture():
	# TODO
	print "TBD"

def test_get_transform_enclosing_rect():
	# TODO
	print "TBD"	

@nose.with_setup(setup_function, teardown_function)
def test_make_picture_invalid_file():
	# test invalid case
	image_loc = resi('doesNotExist.img')
	nose.tools.assert_raises(ValueError, make_picture, image_loc)

@nose.with_setup(setup_function, teardown_function)	
def test_make_picture():
	# ensure that this returns an identical picture from one created manually
	image_loc = resi('white.bmp')
	tester_pict = make_picture(image_loc)
	manual_tester_pict = Picture(); manual_tester_pict.load_image(image_loc)
	ensure_pictures_equal(tester_pict, manual_tester_pict)

@nose.with_setup(setup_function, teardown_function)			
def test_non_picture_object_call():
	# ensuring that all the picture global convenience functions fail on non-Picture objects
	nose.tools.assert_raises(ValueError, get_pixel, DummyClass(), 0, 0)
	nose.tools.assert_raises(ValueError, get_pixels, DummyClass())
	nose.tools.assert_raises(ValueError, get_width, DummyClass())
	nose.tools.assert_raises(ValueError, get_height, DummyClass())
	nose.tools.assert_raises(ValueError, show, DummyClass())
	nose.tools.assert_raises(ValueError, add_line, DummyClass(), 0, 0, 0, 0, None)
	nose.tools.assert_raises(ValueError, add_text, DummyClass(), 0, 0, '', None)
	nose.tools.assert_raises(ValueError, add_rect, DummyClass(), 0, 0, 0, 0, None)
	nose.tools.assert_raises(ValueError, add_rect_filled, DummyClass(), 0, 0, 0, 0, None)
	nose.tools.assert_raises(ValueError, write_picture_to, DummyClass(), '')
	nose.tools.assert_raises(ValueError, set_pixels, DummyClass(), None)
	nose.tools.assert_raises(ValueError, set_pixels, Picture(), DummyClass())

@nose.with_setup(setup_function, teardown_function)
def test_get_short_path():
	# ensure that the short path is returned correctly
	assert get_short_path('') == '', 'Invalid short path'
	assert get_short_path('a.img') == 'a.img', 'Invalid short path'
	assert get_short_path(os.path.join('b', 'a.img')) == os.path.join('b', 'a.img'), 'Invalid short path'
	assert get_short_path(os.path.join('c', os.path.join('b', 'a.img'))) == os.path.join('b', 'a.img'), 'Invalid short path'

if __name__ == '__main__':
	nose.runmodule()
