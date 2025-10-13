# Markdown 转换接口

一个基于 Flask 和 [markitdown](https://github.com/microsoft/markitdown) 开发的文件转 Markdown 接口服务，支持上传文档类文件（如 PDF、DOCX、PPTX、XLSX、XLS），返回转换后的 Markdown 内容，适用于文档自动化处理场景。

## 一、核心功能

* **文件上传转换**：支持多种格式文件（具体依赖 `markitdown` 库）。

* **简洁响应结构**：成功返回 Markdown 内容，失败返回明确错误信息，便于前端解析。

## 二、环境准备

### 1. 本地开发环境

| 依赖项     | 版本要求  | 安装命令                                                 |
| ---------- | --------- | ------------------------------------------------------ |
| Python     | 3.11+     | 参考 [Python 官网](https://www.python.org/) 安装        |
| Flask      | 2.0+      | `pip install flask`                                    |
| markitdown | 1.0+      | `pip install 'markitdown[pdf, pptx, docx, xlsx, xls]'` |

### 2. 依赖清单导出

本地开发完成后，建议生成 `requirements.txt` 锁定依赖版本，便于服务器部署：

``` bash
# 激活虚拟环境后执行
pip freeze > requirements.txt
```

## 三、本地测试

1. **克隆代码**

``` bash
# 方式一：使用 SSH (推荐)
git clone git@github.com/chuxinyuan/tomd.git
# 方式二：使用 HTTPS
git clone https://github.com/chuxinyuan/tomd.git
```

2. **安装依赖**

``` bash
# 创建并激活虚拟环境（推荐）
python -m venv venv

# Windows 激活
venv\Scripts\activate

# macOS/Linux 激活
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

3. **启动本地服务**

``` bash
python app.py
```

4. **验证服务**

服务启动后，访问 `http://127.0.0.1:5000`，若页面显示如下信息说明服务正常运行。

```
Not Found

The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.
```

## 四、接口调用说明

### 1. 基础信息

| 项目     | 内容                                      |
| -------- | ----------------------------------------- |
| 接口地址 | `http://{服务IP}:5000/convert`            |
| 请求方法 | POST                                      |
| 内容类型 | `multipart/form-data`（文件上传）         |
| 核心参数 | `file`：待转换的文件（大小建议 ≤ 10MB）   |
| 响应格式 | JSON                                      |

### 2. 调用示例

#### Curl 命令

``` bash
# 替换 {本地文件路径} 为实际文件（如 ./test.pdf）
curl -X POST -F "file=@/{本地文件路径}" http://127.0.0.1:5000/convert
```

#### R 脚本

``` r
加载 R 包
library(httr)

# 接口配置
api_url = "http://{服务IP}:5000/convert"  # 替换为实际服务IP
file_path = "path/to/file"  # 替换为待测试文件路径

# 检查文件是否存在
if (!file.exists(file_path)) {
  stop(paste("文件不存在:", file_path))
}

# 发送文件上传请求
tryCatch({
  response = POST(
    url = api_url,
    body = list(
      file = upload_file(file_path)
    ),
    encode = "multipart"
  )
  
  # 解析响应结果
  if (status_code(response) == 200) {
    result = content(response, "parsed")  # 解析JSON响应
    cat("转换成功！\nMarkdown内容预览:\n")
    cat(substr(result$markdown_content, 1, 500), "...\n")  # 显示前500字符
  } else {
    error_info = content(response, "parsed")
    cat("请求失败: ", error_info$error, "\n")
  }
  
}, error = function(e) {
  cat("请求发生错误:", e$message, "\n")
})
```

### 3. 响应说明

#### 成功响应（200 OK）

```
{
  "status": "success",
  "markdown_content": "# Document Title\n\nThis is the converted content..."
}
```

#### 失败响应

* 400 错误（请求参数问题）：

```
{"error": "No file part in the request"}  # 未携带 file 参数
{"error": "No file selected"}             # 未选择文件
```

* 500 错误（服务端问题）：

```
{"error": "Input stream must be a readable BinaryIO object."}  # 文件流处理错误
{"error": "Unsupported file format"}                          # 不支持的文件格式
```

## 五、Debian 服务器部署

### 1. 环境配置

```
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv
```

### 2. 代码部署

```
# 创建项目目录
sudo mkdir -p /srv/tomd

# 克隆代码（或通过 SCP 上传）
cd /srv/tomd
git clone git@github.com/chuxinyuan/tomd.git .

# 配置虚拟环境并安装依赖
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置 Systemd 服务

```
# 创建服务文件
sudo nano /etc/systemd/system/tomd.service
```

粘贴以下内容（注意修改路径为实际项目路径）：

``` bash
[Unit]
Description=Document to Markdown Converter Service
After=network.target
[Service]
User=www-data
Group=www-data
WorkingDirectory=/srv/tomd
ExecStart=/srv/tomd/.venv/bin/python app.py
Restart=always
[Install]
WantedBy=multi-user.target
```

启动并设置开机自启：

```
sudo systemctl daemon-reload
sudo systemctl start tomd
sudo systemctl enable tomd
sudo systemctl status tomd
```

### 4. 防火墙配置

```
# 开放 5000 端口
sudo ufw allow 5000/tcp
sudo ufw reload
```

## 六、常见问题

1. **本地启动后无法访问？**

* 检查端口是否被占用：`netstat -tulpn | grep 5000`（Linux/macOS）、`netstat -ano | findstr :5000`（Windows）。
* 确认服务绑定地址为 `0.0.0.0`（允许外部访问）或 `127.0.0.1`（仅本地访问）。

2. **文件转换报 500 错误？**

* 检查文件格式是否在 `markitdown` 支持列表内。
* 查看服务日志定位错误：`sudo journalctl -u tomd -f`。

3. **服务器部署后无法通过 IP 访问？**

* 检查防火墙是否开放 5000 端口：`sudo ufw status`。
* 确认服务器安全组（如阿里云、AWS）已放行 5000 端口。

## 七、技术栈

* 后端框架：Flask
* 文件转换：markitdown
* 进程管理：Systemd
