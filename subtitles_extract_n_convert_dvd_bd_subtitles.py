#!/usr/bin/env python

##############################################
# Extract dvd/bluray (VobSub/PGS) subtitles and convert them into *.srt
# 
# Select video file/s with subtitles to convert.
# To skip extraction from video and go straight to conversion select file with extension sup, sub, idx
# 
# required: 
# https://github.com/mbunkus/mkvtoolnix
# https://github.com/amichaelt/BDSup2SubPlusPlus
# https://github.com/ruediger/VobSub2SRT
# 
# convert sup to srt
# convert sub to srt
# convert idx to srt
# convert dvd subtitles to srt
# convert bluray subtitles to srt
##############################################

execute_ = True			# execute through os.system(); or just print out commands
del_ = True				# remove intermediate files
select_once_ = True		# manually select subtitle track only once; for every subsequent video script will select the same track-number (for videos with same track template)
notify_send_ = True		# notification after all conversions

##############################################

import re, sys, os
import subprocess
import json
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QFileDialog, QApplication, QDialog, QVBoxLayout, QLabel)
from PyQt5.QtGui import (QFont)
from PyQt5.QtCore import *

if len(sys.argv) > 1:
	fnames = sys.argv[1:]
else:
	app = QApplication(sys.argv)
	fnames = QFileDialog.getOpenFileNames(QMainWindow(), 'Open files', '*')[0]

cmd = []
all_ = 0
for fname in fnames:
	print('# ' + fname)
	
	if not os.path.isfile(fname):
		continue
	
	if fname.rsplit('.', 1)[1].lower() not in ('sup', 'sub', 'idx'):
		if select_once_ and 'sub_tracks' in locals():
			pass
		else:
			PIPE = subprocess.PIPE
			sids = subprocess.Popen('mkvmerge -J "%s"' % fname, shell=isinstance('', str), bufsize=-1, stdin=PIPE, stdout=PIPE,stderr=subprocess.STDOUT, close_fds=True).stdout.read().decode("utf8", "ignore")
			
			def on_button(n, a = 0):
				global sub_tracks, all_
				sub_tracks = n
				if a:
					all_ = 1
				w.close()

			app = None
			app = QApplication(sys.argv)
			mainLayout = QVBoxLayout()
			
			newfont = QFont()
			newfont.setPixelSize(40)
			
			label = QLabel(fname.split('/')[-1])
			label.setFont(newfont)
			label.setAlignment(Qt.AlignCenter)
			mainLayout.addWidget(label)
			mainLayout.addWidget(QLabel())

			button = QPushButton('Convert all subtitles(tracks).')
			button.clicked.connect(lambda vb, v = sids: on_button(v, 1))
			button.setFont(newfont)
			mainLayout.addWidget(button)
			
			mainLayout.addWidget(QLabel())
			
			#print(sids)
			tracks = json.loads(sids)['tracks']
			
			for track in tracks:
				if track['type'] == 'subtitles':
					bt = str(track['id']) + ' | '
					bt += track['codec'] + ' | '
					
					if 'language' in track['properties']:
						bt += track['properties']['language'] + ' | '
					if 'track_name' in track['properties']:
						bt += track['properties']['track_name']
					
					button = QPushButton(bt)
					button.clicked.connect(lambda vb, v = [[track['codec'], str(track['id'])]]: on_button(v))
					button.setFont(newfont)
					mainLayout.addWidget(button)

			w = QDialog()
			w.setLayout(mainLayout)
			w.setWindowTitle("List of avaliable subtitles.")
			w.show()
			app.exec_()
		
		if all_:
			PIPE = subprocess.PIPE
			
			sids = subprocess.Popen('mkvmerge -J "%s"' % fname, shell=isinstance('', str), bufsize=-1, stdin=PIPE, stdout=PIPE,stderr=subprocess.STDOUT, close_fds=True).stdout.read().decode("utf8", "ignore")
			
			tracks = json.loads(sids)['tracks']
			sub_tracks = []
			for track in tracks:
				if track['type'] == 'subtitles':
					sub_tracks.append([track['codec'], str(track['id'])])
		
		for sub_track in sub_tracks:
			if 'PGS' in sub_track[0]:
				cmd.append('mkvextract tracks "%s" "%s:%s.%s.sup"' % (fname, sub_track[1], fname.rsplit('.', 1)[0], sub_track[1]))
				cmd.append('bdsup2subpp -o "%s.%s.idx" "%s.%s.sup"' % (fname.rsplit('.', 1)[0], sub_track[1], fname.rsplit('.', 1)[0], sub_track[1]))
				
				cmd.append('vobsub2srt --verbose "%s.%s"' % (fname.rsplit('.', 1)[0], sub_track[1]))
				if del_:
					for ext in ('sup', 'sub', 'idx'):
						cmd.append('rm "%s.%s.%s"' % (fname.rsplit('.', 1)[0], sub_track[1], ext))
			elif 'VobSub' in sub_track[0]:
				cmd.append('mkvextract tracks "%s" "%s:%s.%s.sup"' % (fname, sub_track[1], fname.rsplit('.', 1)[0], sub_track[1]))
				
				cmd.append('vobsub2srt --verbose "%s.%s"' % (fname.rsplit('.', 1)[0], sub_track[1]))
				if del_:
					for ext in ('sub', 'idx'):
						cmd.append('rm "%s.%s.%s"' % (fname.rsplit('.', 1)[0], sub_track[1], ext))
			else:
				print('# Some ERROR ##########################')
				os.system('notify-send -i none -t 5000 "Some ERROR \n ' + str(fname) + '"')
	else:
		if fname.rsplit('.', 1)[1].lower() == 'sup':
			cmd.append('bdsup2subpp -o "%s.idx" "%s.sup"' % (fname.rsplit('.', 1)[0], fname.rsplit('.', 1)[0]))
			if del_:
				cmd.append('rm "%s.%s"' % (fname.rsplit('.', 1)[0], 'sup'))
	
		cmd.append('vobsub2srt --verbose "%s"' %  fname.rsplit('.', 1)[0])
	
if notify_send_:
	cmd.append('notify-send -i none -t 5000 "DONE \n %s"' %  fname)

if execute_:
	os.system(';'.join(cmd))
else:
	print('\n'.join(cmd))


