from IGFirehose import IGFirehose
from flask import render_template, url_for

from flask import Flask
app = Flask(__name__)

config_file = 'igf.conf'
igf = IGFirehose(config_file)

@app.route('/')
def dashboard():
	str_tags=igf.get_mined_tags()
	tags=[]
	for tag in str_tags:
		t={}
		t['name']=tag
		t['size']=igf.get_n_tag(tag)
		t['mined']=igf.get_n_mined(tag)
		e=igf.fetch(tag,n=1)
		if len(e)>0:
			t['thumbnail']=e[0]['thumbnails'][0]['src']
		else:
			t['thumbnail']=url_for('static', filename='imgs/no_imgs.png')
		#tags['thumb']=e[0]['thumbnails'][0]['src']
		tags.append(t)
	return render_template('dashboard.html',tags=tags)


if __name__ == '__main__':
      app.run(host='0.0.0.0', port=59995)
