import gc,time
gc.collect()
import network
def setup_ap(ssid, pwd, ip):
    """设置ESP32为AP模式"""
    try:
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        # 注意：authmode配置需要在password之前
        ap.config(essid=str(ssid), authmode=network.AUTH_WPA_WPA2_PSK, password=str(pwd))
        
        # 设置静态IP
        ap.ifconfig((str(ip), '255.255.255.0', str(ip), '8.8.8.8'))
        
        print("AP模式已启动")
        print("SSID: " + str(ssid))
        print("密码: " + str(pwd))
        print("IP地址: " + ap.ifconfig()[0])
        
        return ap
    except Exception as e:
        print("AP设置失败: " + str(e))
        return None

def setup_sta(ssid, pwd):
    """设置STA模式连接WiFi"""
    try:
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        if not sta.isconnected():
            print("正在连接WiFi: " + str(ssid))
            sta.connect(str(ssid), str(pwd))
            
            # 等待连接，最多30秒
            for i in range(30):
                if sta.isconnected():
                    break
                time.sleep(1)
                print(".", end='')
            print()
        
        if sta.isconnected():
            print("WiFi连接成功!")
            print("IP地址: " + sta.ifconfig()[0])
        else:
            print("WiFi连接失败!")
        
        return sta
    except Exception as e:
        print("STA设置失败: " + str(e))
        return None
ap = setup_ap('某某饭店_5G', '12345678', '192.168.4.1')
sta = setup_sta("wangtaohan", "13995506230")

# 基于 MicroFlask 的文件上传示例
from microflask import*
import binascii
max_request_length=8192
# 创建一个应用实例
app = Flask(__name__)

def parse_multipart_form_data(body, boundary):
    """
    一个简化的 multipart/form-data 解析器，用于在 ESP32 等资源受限环境。
    它提取第一个文件的文件名和内容。
    注意：这是一个简化实现，对于复杂表单可能需要增强。
    """
    parts = body.split(b'--' + boundary.encode())
    result = {}

    for part in parts:
        if b'Content-Disposition: form-data;' in part:
            # 找到头部和正文的分隔处
            header_end = part.find(b'\r\n\r\n')
            if header_end == -1:
                continue
            headers = part[:header_end]
            file_content = part[header_end+4:]  # 跳过 \r\n\r\n

            # 解析头部，寻找文件名
            lines = headers.split(b'\r\n')
            filename = None
            field_name = None
            for line in lines:
                if b'name=' in line and b'filename=' in line:
                    # 处理文件字段
                    try:
                        # 简单解析，查找 filename="..."
                        name_start = line.find(b'name="') + 6
                        name_end = line.find(b'"', name_start)
                        field_name = line[name_start:name_end].decode()

                        filename_start = line.find(b'filename="', name_end) + 10
                        filename_end = line.find(b'"', filename_start)
                        filename = line[filename_start:filename_end].decode()
                    except:
                        pass
                    if filename and field_name:
                        # 移除末尾可能存在的 \r\n (正文部分后的分隔符)
                        if file_content.endswith(b'\r\n'):
                            file_content = file_content[:-2]
                        result[field_name] = {'filename': filename, 'content': file_content}
                        break
    return result

@app.route('/upload', methods=['GET'])
def upload_form(request):
    """提供一个简单的文件上传HTML表单页面"""
    html_form = '''
    <!DOCTYPE html>
    <html>
    <head><title>Upload File</title></head>
    <body>
        <h2>Upload a .txt file to ESP32</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <label for="file">Select file (max 8KB):</label><br><br>
            <input type="file" id="file" name="file" accept=".txt"><br><br>
            <input type="submit" value="Upload">
        </form>
    </body>
    </html>
    '''
    return Response(html_form, content_type="text/html")

@app.route('/upload', methods=['POST'])
def handle_upload(request):
    """处理文件上传的POST请求"""
    content_type = request.headers.get('Content-Type', '')

    # 检查是否为multipart表单数据
    if 'multipart/form-data' not in content_type:
        return Response('Invalid content type. Expected multipart/form-data.', status=400)

    # 从Content-Type头中提取边界字符串
    try:
        boundary = content_type.split('boundary=')[1].strip()
    except IndexError:
        return Response('Could not find boundary in Content-Type.', status=400)

    # 限制文件大小（框架默认限制为max_request_length=8192，但是可以从run修改，此处再次检查）
    if len(request.body) > max_request_length:
        return Response(f'File too large. Maximum size is {max_request_length/1024}KB.', status=413)

    # 解析multipart数据
    uploaded_files = parse_multipart_form_data(request.body, boundary)

    if 'file' not in uploaded_files:
        return Response('No file uploaded or field name is not "file".', status=400)

    file_info = uploaded_files['file']
    filename = file_info['filename']
    file_content = file_info['content']

    # 检查是否为文本文件（简单通过扩展名）
    if not filename.lower().endswith('.txt'):
        return Response('Only .txt files are allowed.', status=400)

    # 将文件保存到ESP32的文件系统 (例如命名为 uploaded.txt)
    try:
        save_path = 'uploaded.txt'
        with open(save_path, 'wb') as f:
            f.write(file_content)
        save_message = f"File saved successfully to '{save_path}'."
    except Exception as e:
        return Response(f"Failed to save file: {e}", status=500)

    # 尝试将文件内容解码为UTF-8文本并输出
    try:
        text_content = file_content.decode('utf-8')
        content_preview = text_content[:500]  # 预览前500个字符，避免响应过大
        if len(text_content) > 500:
            content_preview += "\n... (truncated for display)"
    except UnicodeDecodeError:
        content_preview = "[File contains binary data, cannot display as text]"

    # 构建响应HTML，显示上传结果和文件内容
    result_html = f'''
    <!DOCTYPE html>
    <html>
    <head><title>Upload Result</title></head>
    <body>
        <h2>Upload Successful!</h2>
        <p><strong>Original Filename:</strong> {filename}</p>
        <p><strong>Save Status:</strong> {save_message}</p>
        <p><strong>File Size:</strong> {len(file_content)} bytes</p>
        <hr>
        <h3>Content of the uploaded file:</h3>
        <pre>{content_preview}</pre>
        <hr>
        <a href="/upload">Upload another file</a>
    </body>
    </html>
    '''
    return Response(result_html, content_type="text/html")

if __name__ == '__main__':
    # 注意：对于文件上传，根据文件大小调整 max_request_length 参数。
    app.run(port=80,max_request_length=max_request_length)