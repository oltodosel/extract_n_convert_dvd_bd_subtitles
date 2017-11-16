#! /usr/bin/env python3

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
notify_send_ = True		# notification after each conversion

##############################################

import re, sys, os
import subprocess
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QFileDialog, QApplication, QDialog, QVBoxLayout, QLabel)
from PyQt5.QtGui import (QFont)
from PyQt5.QtCore import *

app = QApplication(sys.argv)
fnames = QFileDialog.getOpenFileNames(QMainWindow(), 'Open files', '*')[0]

cmd = []
for fname in fnames:
	print('# ' + fname)
	
	if fname.rsplit('.', 1)[1].lower() not in ('sup', 'sub', 'idx'):
		if select_once_ and 'sub_tracks' in locals():
			pass
		else:
			PIPE = subprocess.PIPE
			sids = subprocess.Popen('mkvmerge --identify-verbose "%s"' % fname, shell=isinstance('', str), bufsize=-1, stdin=PIPE, stdout=PIPE,stderr=subprocess.STDOUT, close_fds=True).stdout.read().decode("utf8", "ignore")
			
			sids = [ re.findall('(Track ID (\d+): subtitles .+)', x) for x in sids.split('\n') if len(re.findall('(Track ID (\d+): subtitles .+)', x)) ]
			
			def on_button(n):
				global sub_tracks
				sub_tracks = n
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
			button.clicked.connect(lambda vb, v = sids: on_button(v))
			button.setFont(newfont)
			mainLayout.addWidget(button)
			
			mainLayout.addWidget(QLabel())
				
			for sid in sids:
				button = QPushButton(
					re.sub('\[.+\]', '', sid[0][0]) + ' | ' + 
					''.join(re.findall('language:(.*?) ', sid[0][0])) + ' | ' + 
					''.join(re.findall('track_name:(.*?) ', sid[0][0])).replace('\s', ' ')
				)
				button.clicked.connect(lambda vb, v = [sid]: on_button(v))
				button.setFont(newfont)
				mainLayout.addWidget(button)

			w = QDialog()
			w.setLayout(mainLayout)
			w.setWindowTitle("List of avaliable subtitles.")
			w.show()
			app.exec_()
		
		for strk in sub_tracks:
			sub_track = strk[0]
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

