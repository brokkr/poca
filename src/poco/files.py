import os
import shutil
import logging

import eyed3
from urlgrabber import urlgrab, progress

from poco import errors

_settings_synonyms = { \
    '2.3': eyed3.ID3_V2_3, \
    '2.4': eyed3.ID3_V2_4, \
    'latin-1': eyed3.LATIN1_ENCODING, \
    'utf-16': eyed3.UTF_16_ENCODING, \
    'utf-16be': eyed3.UTF_16BE_ENCODING, \
    'utf-8': eyed3.UTF_8_ENCODING \
    }

def delete_audio_file(entry_dic, sub_dic):
    '''Deletes one file'''
    localfile = _get_path(entry_dic, sub_dic)
    try:
        os.remove(localfile)
    except OSError:
        error = 'The file ' + localfile + ' could not be deleted. '
        suggest = ['Was poca interrupted during the last run?', \
        'Have you deleted/moved files manually? Or changed permissions?']
        errors.errors(error, suggest, fatal=False, title=sub_dic['title'].upper())

def download_audio_file(entry_dic, sub_dic, args_ns):
    '''Downloads one file'''
    meter = progress.text_progress_meter()
    localfile = _get_path(entry_dic, sub_dic)
    if args_ns.quiet:
        dummy = urlgrab(entry_dic['url'].encode('ascii'), localfile)
    else:
        dummy = urlgrab(entry_dic['url'].encode('ascii'), localfile, progress_obj=meter)
    # how to test if the right file was downloaded?
    # check file length? file name? 
    # not fool-proof as these could have been provided by the program itself...

def tag_audio_file(sets_dic, entry_dic, sub_dic):
    '''Tags one audio file with supplied metadata'''
    localfile = _get_path(entry_dic, sub_dic)
    container = eyed3.Tag()

    if not eyed3.isMp3File(localfile) or not container.link(localfile):
        error = 'The file ' + localfile + ' could not be tagged. '
        suggest = ['Please check to see if the feed delivers valid mp3 files.']
        errors.errors(error, suggest, fatal=False, title=sub_dic['title'].upper())
        return

    tags = {}
    tags['artist'] = container.getArtist()
    tags['album'] = container.getAlbum()
    tags['genre'] = container.getGenre()
    tags.update(sub_dic['metadata'])

    if sets_dic['metadata']['removeid3v1'] == 'yes':
        container.remove(eyed3.ID3_V1)
    id3version = _settings_synonyms[sets_dic['metadata']['id3version']]
    id3encoding = _settings_synonyms[sets_dic['metadata']['id3encoding']]
    container.header.setVersion(id3version)
    container.setTextEncoding(id3encoding)

    container.setArtist(tags['artist'])
    container.setAlbum(tags['album'])
    container.setGenre(tags['genre'])
    try:
        container.update(id3version)
    except UnicodeEncodeError:
        pass

def check_path(sub_dic):
    '''Creates one directory'''
    if os.path.isdir(sub_dic['sub_dir']):
        return
    try:
        os.makedirs(sub_dic['sub_dir'], 0755)
    except OSError:
        error = 'The directory ' + sub_dic['sub_dir']  + ' could not be created. ' 
        suggest = ['Please check your configuration and permissions.']
        errors.errors(error, suggest, fatal=True, title=sub_dic['title'].upper())
            
def restart(paths_dic, subs_list):
    '''Deletes log file and all created directories'''
    try:
        sub_dir_list = [sub_dic['sub_dir'] for sub_dic in subs_list]
        print 'The following directories will be deleted:'
        for sub_dir in sub_dir_list:
            if os.path.isdir(sub_dir):
                print sub_dir
            else:
                sub_dir_list.remove(sub_dir)
        response = raw_input('Proceed? (y/n) ')
        if response.lower() != 'y':
            print 'Abandoning restart', '\n'
            return False
        print 'Deleting old files...', '\n'
        for sub_dir in sub_dir_list:
            shutil.rmtree(sub_dir)
        os.remove(paths_dic['history_log'])
        return True
    except OSError:
        return False

def _get_path(entry_dic, sub_dic):
    '''Joins a directory with a filename to return one complete file path'''
    return os.path.join(sub_dic['sub_dir'], entry_dic['filename'])

