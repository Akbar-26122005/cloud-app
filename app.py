from flask import Flask, request, jsonify, send_file, render_template_string
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'storage'
ALLOWED_EXTENTIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_FORM = '''
    <!DOCKTYPE>
    <html>
    <head>
        <title>Загрузка файлов</title>
    </head>
    <body>
        <div class="app">
            <h1>Приветствую</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <h3>Загрузка файлов</h3>
                <input type="file" name="file" >
                <input type="submit" value="Загрузить" >
            </form>
            <p><a href="/list">Список файлов</a></p>
            <form action="/files/">
                <h3>Скачивание файла</h3>
                <input type="text" name="path" placeholder="Имя файла" required>
                <button type="submit">Скачать</button>
                <br />
            </form>
            <small>Введите в формате: YYYY-mm-dd/название файла</small>
        </div>
        
        <style>
            body {
                display: grid;
                align-content: start;
                justify-items: center;
                margin-top: 80px;
            }
            
            .app {
                width: max-content;
                border: 1px solid gray;
                padding: 44px 32px;
                border-radius: 8px;
                box-shadow: 2px 2px 10px 2px rgba(0, 0, 0, 0.1);
                display: grid;
                align-content: center;
            }
            
            form {
                border: 1px solid black;
                border-radius: 4px;
                width: 100%;
            }
            
            h1 {
                justify-self: center;
            }
        </style>
    </body>
    </html>
'''

@app.route('/')
def index():
    return HTML_FORM

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден в запросе'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Имя файла пустое'}), 400
    
    filename = secure_filename(file.filename)
    
    today = datetime.now().strftime('%Y-%m-%d')
    save_folder = os.path.join(app.config['UPLOAD_FOLDER'], today)
    os.makedirs(save_folder, exist_ok=True)
    
    filepath = os.path.join(save_folder, filename)
    
    file.save(filepath)
    
    file_size = os.path.getsize(filepath)
    upload_time = datetime.now().isoformat()
    
    return jsonify({
        'message': 'Файл загружен успешно',
        'filename': filename,
        'size_bytes': file_size,
        'upload_time': upload_time,
        'path': f'{today}/{filename}'
    }), 201

@app.route('/list')
def list_files():
    files_list = []
    
    for root, dirs, files in os.walk(UPLOAD_FOLDER):
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, UPLOAD_FOLDER)
            
            stats = os.stat(filepath)
            files_list.append({
                'name': file,
                'path': rel_path,
                'size_bytes': stats.st_size,
                'modified': datetime.fromtimestamp(stats.st_mtime).isoformat()
            })
            
    return jsonify({'files': files_list, 'count': len(files_list)})

@app.route('/files/')
def download_file():
    filename = request.args.get('path')
    print(f'Получено значение: {filename}')
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Файл не найден'})
    
    return send_file(filepath, as_attachment=True)

@app.route('/upload-form')
def upload_form():
    return render_template_string(HTML_FORM)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
