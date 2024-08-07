from flask import Flask, request, render_template,flash, send_file, make_response,jsonify,redirect,url_for
from werkzeug.utils import secure_filename
import os
from vse.cli import extract_subtitles
from io import BytesIO
import zipfile
from vsr.cli import remove_main
from srt.cli import translate_srt_files
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 设置一个密钥以启用 session
app.config['UPLOAD_FOLDER'] = '/home/song/Documents/Codes/subtitle-flask-bar/save_path'  # 替换为你的上传文件夹路径
ALLOWED_EXTENSIONS_videos = {'mp4', 'avi', 'proper', 'psd', 'swf'}
ALLOWED_EXTENSIONS_subtitles = {'srt'}
folder_path = '' ##当前用户上传的文件夹保存路径 unknown_floder
num_files=0 #总的视频个数
files_th=0 #第几个视频正在被处理
file_name='' #保存当前的文件名
language_in=''
language_out=''
area=None
start_t=None
end_t=None

def allowed_file_videos(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_videos

def allowed_file_subtitle(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_subtitles

def subtitle_finder():
    global folder_path
    path= folder_path
    out_path='SubtitleFinder'
    global files_th
    files_th=0
    extract_subtitles(path,out_path,files_th)
    # session['result'] = 'Subtitle Finder Successful'

def test():
    time.sleep(4)

@app.route('/')
def index():
    # if 'result' in session:
    #     del session['result']  # 每次加载页面时清除 session 中的 result
    # return render_template('app.html' )
    return render_template('app.html')

@app.route('/upload_folder', methods=['POST'])
def upload_folder():
    # session['result'] = 666  #'Load Successful!'
    if 'files' not in request.files:
        # if 'result' in session:
        #     del session['result']  # 每次加载页面时清除 session 中的 result
        return 'None file' 
    folder_name = request.form.get('folderName', 'unknown_folder')  # 获取文件夹名称
    global folder_path 
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    video_path= os.path.join(folder_path,'videos')
    Subtitlefinder_path=os.path.join(folder_path,'SubtitleFinder')
    files = request.files.getlist('files')
    global num_files
    num_files=len(files)
    if len(files) == 0:
        flash('No selected file')
        # if 'result' in session:
        #     del session['result']  # 每次加载页面时清除 session 中的 result
        return 'None file'   
    for file in files:
        if allowed_file_videos(file.filename):
               # 确保文件夹存在
           if not os.path.exists(video_path):
               os.makedirs(video_path)
           filename = secure_filename(file.filename)
           filename = filename.split('_')[-1]
           file.save(os.path.join(video_path, filename))  # 保存到以文件夹名称命名的子文件夹中 
        elif allowed_file_subtitle(file.filename):
           if not os.path.exists(Subtitlefinder_path):
               os.makedirs(Subtitlefinder_path)
           filename = secure_filename(file.filename)
           filename = filename.split('_')[-1]
           file.save(os.path.join(Subtitlefinder_path, filename))  # 保存到以文件夹名称命名的子文件夹中 
    # return render_template('app.html')
    return 'Successful'

@app.route('/upload_nosubvideos', methods=['POST'])
def upload_nosubvideos():
    # session['result'] = 666  #'Load Successful!'
    if 'files' not in request.files:
        # if 'result' in session:
        #     del session['result']  # 每次加载页面时清除 session 中的 result
        return 'None file' 
    folder_name = request.form.get('folderName', 'unknown_folder')  # 获取文件夹名称
    global folder_path 
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    video_path= os.path.join(folder_path,'videos_no_sub')
    files = request.files.getlist('files')
    global num_files
    num_files=len(files)
    if len(files) == 0:
        flash('No selected file')
        # if 'result' in session:
        #     del session['result']  # 每次加载页面时清除 session 中的 result
        return 'None file'   
    for file in files:
        if allowed_file_videos(file.filename):
               # 确保文件夹存在
           if not os.path.exists(video_path):
               os.makedirs(video_path)
           filename = secure_filename(file.filename)
           filename = filename.split('_')[-1]
           file.save(os.path.join(video_path, filename))  # 保存到以文件夹名称命名的子文件夹中 
    # return render_template('app.html')
    return 'Successful'

@app.route('/input_area',methods=['GET', 'POST'])
def input_area():
    if request.method == 'POST':
        global area
        global start_t
        global end_t
        area = request.form['area'] or None
        start_t = request.form['start_t'] or None
        end_t = request.form['end_t'] or None
        print(area,start_t,end_t)
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/select_language',methods=['GET', 'POST'])
def select_language():
    if request.method == 'POST':
        global language_in
        global language_out
        language_in = request.form['language_in']
        language_out = request.form['language_out']
        print(language_in,language_out)
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/subtitle_finder_go')
def subtitle_finder_go():
    subtitle_finder()
    # test()
    # return jsonify({'done': True})
    # return 'Subtitle Find successful!'
    return jsonify({'status': 'done'})

@app.route('/subfinder_download')
def subfinder_download():
    global folder_path
    path= folder_path
    out_path='SubtitleFinder'

        # 检查文件夹是否存在
    path = os.path.join(path, out_path)
    if not os.path.isdir(path):
        return 'Folder not found', 404

    # 创建一个BytesIO对象，用于存储ZIP文件内容
    zip_buffer = BytesIO()

    # 创建一个ZipFile对象，将文件写入BytesIO对象
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, path)
                zipf.write(file_path, arcname)

    # 将BytesIO对象移动到文件开头，准备读取
    zip_buffer.seek(0)

    # 设置HTTP响应头，指示浏览器这是一个ZIP文件，并且应该下载它
    response = make_response(send_file(
    zip_buffer,
    as_attachment=True,
    mimetype='application/zip',  # 显式指定MIME类型为application/zip
    download_name=f"{out_path}.zip"  # 可以设置下载的文件名
    ))
    response.headers["Content-Disposition"] = "attachment; filename={}.zip".format(out_path)
    return response

@app.route('/show_list')
def show_list():
    # 列出文件夹下的所有文件
    global folder_path
    
    out_path='SubtitleFinder'
    path= os.path.join(folder_path,out_path)

    # 列出当前目录下的所有文件和子目录
    files_and_dirs = os.listdir(path)
    
    # 过滤出文件（排除子目录）
    files = [f for f in files_and_dirs if os.path.isfile(os.path.join(path, f))]
    
    # 打印所有文件的名称
    # for file in files:
    #     print(file)

    # files = [f for f in os.listdir(FOLDER_PATH) if os.path.isfile(os.path.join(FOLDER_PATH, f))]
    return render_template('show_list.html', files=files)
    # return jsonify({'files': 'files'})

@app.route('/show_list/<filename>')
def file_clicked(filename):
    global file_name
    file_name = filename
    out_path='SubtitleFinder'
    global folder_path
    path= os.path.join(folder_path,out_path)
        # 列出当前目录下的所有文件和子目录
    files_and_dirs = os.listdir(path)
    
    # 过滤出文件（排除子目录）
    files = [f for f in files_and_dirs if os.path.isfile(os.path.join(path, f))]
    # 检查文件是否存在于指定文件夹中
    if filename in os.listdir(path):
        # 跳转成功页面
        dir_path = os.path.join(path,filename)
        # return jsonify({'file_content': open(dir_path, 'r').read()})
        # return render_template('show_file.html', file_content=open(dir_path, 'r').read()) #file_content=open(FILE_PATH, 'r').read()
        return render_template('show_list.html', files=files,file_content=open(dir_path, 'r').read(),select_file=filename)
    else:
        # 文件不存在时重定向回首页或显示错误信息
        return redirect(url_for('show_list'))

@app.route('/edit_file', methods=['POST'])
def edit_file():
    # 获取修改后的文件内容
    new_content = request.form['file_content']
    global file_name
    global folder_path
    out_path='SubtitleFinder'
    path= os.path.join(folder_path,out_path)
    
    # 写入文件
    with open(os.path.join(path,file_name), 'w') as file:
        file.write(new_content)
    
    # 重定向回首页或其他页面
    return redirect(url_for('file_clicked',filename=file_name))

@app.route('/Return_list')
def Return_list():
    return redirect(url_for('show_list'))

@app.route('/Return_index')
def Return_index():
    return redirect(url_for('index'))

@app.route('/subtitle_remover', methods=['GET'])
def subtitle_remover():
    global folder_path
    path= folder_path
    global area
    global start_t
    global end_t
    # out_path='Subtitleremover'
    remove_main(path,area,start_t,end_t)

    return jsonify({'status': 'done'})

@app.route('/subtitle_translation', methods=['GET'])
def subtitle_translate():
    global language_in
    global language_out
    print(language_in)
    print(language_out)
    if language_in=="" or language_out=="":
        return '请选择输入和输出语言！'
    else:
        global folder_path
        path= folder_path
        translate_srt_files(path,language_in,language_out)
        return jsonify({'status': 'done'})

@app.route('/show_translation')
def show_translation():
    # 列出文件夹下的所有文件
    global folder_path
    out_path='SubtitleFinder_out'
    path= os.path.join(folder_path,out_path)
    # 列出当前目录下的所有文件和子目录
    files_and_dirs = os.listdir(path)
    # 过滤出文件（排除子目录）
    files = [f for f in files_and_dirs if os.path.isfile(os.path.join(path, f))]
    # 打印所有文件的名称
    # for file in files:
    #     print(file)

    # files = [f for f in os.listdir(FOLDER_PATH) if os.path.isfile(os.path.join(FOLDER_PATH, f))]
    return render_template('show_translation.html', files=files)
    # return jsonify({'files': 'files'})

@app.route('/show_translation/<filename>')
def file_clicked_translation(filename):
    global file_name
    file_name = filename
    out_path_ch='SubtitleFinder'
    out_path='SubtitleFinder_out'
    global folder_path
    path= os.path.join(folder_path,out_path)
    out_path_ch = os.path.join(folder_path,out_path_ch)
        # 列出当前目录下的所有文件和子目录
    files_and_dirs = os.listdir(path)
    # 过滤出文件（排除子目录）
    files = [f for f in files_and_dirs if os.path.isfile(os.path.join(path, f))]
    # 检查文件是否存在于指定文件夹中
    if filename in os.listdir(path):
        # 跳转成功页面
        dir_path = os.path.join(path,filename)
        dir_path_ch = os.path.join(out_path_ch,filename)
        # return jsonify({'file_content': open(dir_path, 'r').read()})
        # return render_template('show_file.html', file_content=open(dir_path, 'r').read()) #file_content=open(FILE_PATH, 'r').read()
        return render_template('show_translation.html', files=files,file_content=open(dir_path, 'r').read(),file_content_ch=open(dir_path_ch,'r').read(),select_file=filename)
    else:
        # 文件不存在时重定向回首页或显示错误信息
        return redirect(url_for('show_translation'))

@app.route('/edit_file_translation', methods=['POST'])
def edit_file_translation():
    # 获取修改后的文件内容
    new_content = request.form['file_content']
    global file_name
    global folder_path
    out_path='SubtitleFinder_out'
    path= os.path.join(folder_path,out_path)
    # 写入文件
    with open(os.path.join(path,file_name), 'w') as file:
        file.write(new_content)
    # 重定向回首页或其他页面
    return redirect(url_for('file_clicked_translation',filename=file_name))

@app.route('/subtitle_combine', methods=['GET'])
def subtitle_combine():
    global folder_path
    path= folder_path

    return jsonify({'status': 'done'})

@app.route('/videos_download')
def videos_download():
    global folder_path
    path= folder_path
    out_path='videos_no_sub'
    # 检查文件夹是否存在
    path = os.path.join(path, out_path)
    if not os.path.isdir(path):
        return 'Folder not found', 404
    # 创建一个BytesIO对象，用于存储ZIP文件内容
    zip_buffer = BytesIO()
    # 创建一个ZipFile对象，将文件写入BytesIO对象
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, path)
                zipf.write(file_path, arcname)
    # 将BytesIO对象移动到文件开头，准备读取
    zip_buffer.seek(0)
    # 设置HTTP响应头，指示浏览器这是一个ZIP文件，并且应该下载它
    response = make_response(send_file(
    zip_buffer,
    as_attachment=True,
    mimetype='application/zip',  # 显式指定MIME类型为application/zip
    download_name=f"{out_path}.zip"  # 可以设置下载的文件名
    ))
    response.headers["Content-Disposition"] = "attachment; filename={}.zip".format(out_path)
    return response

if __name__ == "__main__":
    app.run(debug=True,port=8000)
    # app.run(host='0.0.0.0', port=5000, debug=True)  # 允许任何IP地址访问