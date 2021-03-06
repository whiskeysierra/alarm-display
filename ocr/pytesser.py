import os
import subprocess

from PIL import Image

tesseract_exe_name = 'tesseract'
scratch_image_name = "temp.bmp"
scratch_text_name_root = "temp"
cleanup_scratch_flag = True


class Tesser_General_Exception(Exception):
    pass


class Tesser_Invalid_Filetype(Tesser_General_Exception):
    pass


def check_for_errors(logfile="tesseract.log"):
    if not os.path.exists(logfile):
        return
    inf = file(logfile)
    text = inf.read()
    inf.close()
    # All error conditions result in "Error" somewhere in logfile
    if text.find("Error") != -1:
        raise Tesser_General_Exception, text


def image_to_scratch(im, scratch_image_name):
    """
    Saves image in memory to scratch file.  .bmp format will be read correctly by Tesseract
    """
    im.save(scratch_image_name, dpi=(200, 200))


def retrieve_text(scratch_text_name_root):
    inf = file(scratch_text_name_root + '.txt')
    text = inf.read()
    inf.close()
    return text


def perform_cleanup(scratch_image_name, scratch_text_name_root):
    """
    Clean up temporary files from disk
    """
    for name in (scratch_image_name, scratch_text_name_root + '.txt', "tesseract.log"):
        try:
            os.remove(name)
        except OSError:
            pass


def call_tesseract(input_filename, output_filename):
    """
    Calls external tesseract.exe on input file (restrictions on types),
    outputting output_filename+'txt'
    """
    args = [tesseract_exe_name, input_filename, output_filename, '-l', 'deu']
    env = os.environ.copy()
    env['TESSDATA_PREFIX'] = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

    try:
        subprocess.check_output(args, stderr=subprocess.STDOUT, env=env)
    except subprocess.CalledProcessError, e:
        check_for_errors()
        raise Tesser_General_Exception(e.output)


def image_to_string(im, cleanup=cleanup_scratch_flag):
    """
    Converts im to file, applies tesseract, and fetches resulting text.
    If cleanup=True, delete scratch files after operation.
    """
    try:
        image_to_scratch(im, scratch_image_name)
        call_tesseract(scratch_image_name, scratch_text_name_root)
        text = retrieve_text(scratch_text_name_root)
    finally:
        if cleanup:
            perform_cleanup(scratch_image_name, scratch_text_name_root)
    return text


def image_file_to_string(filename, cleanup=cleanup_scratch_flag, graceful_errors=True):
    """
    Applies tesseract to filename; or, if image is incompatible and graceful_errors=True,
    converts to compatible format and then applies tesseract.  Fetches resulting text.
    If cleanup=True, delete scratch files after operation.
    """
    try:
        try:
            call_tesseract(filename, scratch_text_name_root)
            text = retrieve_text(scratch_text_name_root)
        except Tesser_General_Exception:
            if graceful_errors:
                im = Image.open(filename)
                text = image_to_string(im, cleanup)
            else:
                raise
    finally:
        if cleanup:
            perform_cleanup(scratch_image_name, scratch_text_name_root)
    return text
