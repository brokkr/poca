import os
import shutil
import logging
import requests

from mutagen import id3

from poco.id3v23_frames import frame_dic
from poco import errors

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
    #meter = progress.text_progress_meter()
    localfile = _get_path(entry_dic, sub_dic)
    if args_ns.quiet:
        file_object = requests.get(entry_dic['url'])
    else:
        file_object = requests.get(entry_dic['url'])
    if file_object.status_code == 200:
        open(localfile, 'w').write(file_object.content)

    # how to test if the right file was downloaded?
    # check file length? file name? 
    # not fool-proof as these could have been provided by the program itself...

def tag_audio_file(sets_dic, entry_dic, sub_dic):
    '''Reintroducing id3 tagging using mutagen'''
    # get general metadata settings
    id3version_dic = {'2.3': 3, '2.4': 4}
    id3encoding_dic = {'latin1': 0, 'utf16': 1, 'utf16be': 2, 'utf8': 3}
    id3v1_dic = {'yes': 0, 'no': 2}
    id3version = id3version_dic[sets_dic['metadata']['id3version']]
    id3encoding = id3encoding_dic[sets_dic['metadata']['id3encoding']]
    id3v1 = id3v1_dic[sets_dic['metadata']['removeid3v1']] 
    # overwrite metadata in the present file 
    localfile = _get_path(entry_dic, sub_dic)
    id3tag = id3.ID3(localfile)
    if id3version == 3:
        id3tag.update_to_v23()
    for override in sub_dic['metadata']:
        frame = frame_dic[override]
        ftext = sub_dic['metadata'][override]
        id3tag.add(frame(encoding=id3encoding, text=ftext))
        id3tag.save(v1=id3v1, v2_version=id3version)

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

