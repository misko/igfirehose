from IGFirehose import IGFirehose
from flask import render_template, url_for,  jsonify

from flask import Flask
import datetime
app = Flask(__name__)

config_file = 'igf.conf'
igf = IGFirehose(config_file)

@app.route('/')
def dashboard():
	str_tags=list(igf.get_mined_tags())
	str_tags.sort()
	tags=[]
        total_images = 0
        total_mined = 0
	for tag in str_tags:
		t={}
		t['name']=tag
		t['size']=igf.get_n_tag(tag)
		t['mined']=igf.get_n_mined(tag)
                total_images+=t['size']
                total_mined+=t['mined']
		if t['size']==0:
			t['percent']='X'
		else:
			t['percent']="%0.2f" % (100*float(t['mined'])/(t['size']))
				

		t['size']="{:,}".format(t['size'])
		t['mined']="{:,}".format(t['mined'])
		e=igf.fetch(tag,n=1)
		print e
		if len(e)>0:
			t['thumbnail']=e[0]['thumbnails'][1]
		else:
			t['thumbnail']=url_for('static', filename='imgs/no_imgs.png')
		#tags['thumb']=e[0]['thumbnails'][0]['src']
		tags.append(t)
        total_progress=(100*float(total_mined)/total_images)
        total_progress_str="%0.2f" % (total_progress)
	total_images="{:,}".format(total_images)
	return render_template('dashboard.html',tags=tags,total_images=total_images,total_progress=total_progress_str,total_progress_int=int(total_progress))

@app.route('/mined/<tag>')
@app.route('/mined/')
def n_mined(tag=""):
        return jsonify(igf.get_n_mined(tag))

@app.route('/tag_view/<tag>')
def tag_view(tag):
	imgs=igf.fetch(tag,n=100)
	for img in imgs:
		img['thumbnail']=img['thumbnails'][1]
		img['time']=datetime.datetime.fromtimestamp(img['timestamp']).strftime('%c')
	wordcloud=url_for('static', filename='wordclouds/'+tag+'.png')
	return render_template('tag_view.html',tag=tag,imgs=imgs,wordcloud=wordcloud)
	

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=59995)
