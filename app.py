from flask import Flask, request, jsonify
from markitdown import MarkItDown
from io import BytesIO
import os
app = Flask(__name__)

# 初始化 MarkItDown 实例
md = MarkItDown()

@app.route('/')
def index():
    return "TOMD API Service is running.", 200

@app.route('/convert', methods=['POST'])
def convert_to_markdown():
    # 检查请求中是否包含文件
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    
    # 检查是否选择了文件
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file:
        try:
            # 以二进制模式读取文件内容
            file_content = file.read()
            
            # 文件对象使用 BytesIO 包装
            file_stream = BytesIO(file_content)
            
            # 使用处理后的文件流进行转换
            result = md.convert(file_stream)
            
            # 返回转换后的 Markdown 内容
            return jsonify({
                "status": "success",
                "markdown_content": result.text_content
            }), 200
        except Exception as e:
            # 捕获转换过程中可能出现的错误
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 监听在所有网络接口的 5000 端口上
    app.run(host='0.0.0.0', port=5000, debug=True)
