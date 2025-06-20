from app.database import MySQLClient
from app.database import RedisClient
from flask import send_from_directory
import json
import os
import datetime
import base64


class Template:
    def __init__(self, t_id, t_author, t_name, t_description, create_time=None, update_time=None):
        self.t_id = t_id
        self.t_author = t_author
        self.t_name = t_name
        self.t_description = t_description
        self.create_time = create_time
        self.update_time = update_time

    @staticmethod
    def _convert_datetime(data):
        """
        将数据中的 datetime 对象转换为字符串格式。
        """
        for key, value in data.items():
            if isinstance(value, datetime.datetime):
                data[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        return data

    @staticmethod
    def from_dict(data):
        """
        从字典创建 Template 对象。
        """
        data = Template._convert_datetime(data)
        return Template(
            t_id=data.get('t_id'),
            t_author=data.get('t_author'),
            t_name=data.get('t_name'),
            t_description=data.get('t_description'),
            create_time=data.get('create_time'),
            update_time=data.get('update_time')
        )

    @staticmethod
    def to_dict(template):
        data = {
            't_id': template.t_id,
            't_author': template.t_author,
            't_name': template.t_name,
            't_description': template.t_description,
            'create_time': template.create_time,
            'update_time': template.update_time
        }
        return Template._convert_datetime(data)


class TemplateModel:
    def __init__(self, mysql_client: MySQLClient, redis_client: RedisClient, app):
        self.mysql_client = mysql_client
        self.redis_client = redis_client
        self.app = app

    def get_templates(self):
        redis_key = 'template_list'
        templates = self.redis_client.get(redis_key)
        if templates:
            templates = json.loads(templates)
            return [Template.from_dict(template) for template in templates]
        mysql_query = "SELECT t_id, t_name, t_description FROM templates"
        templates = self.mysql_client.execute_query(mysql_query)
        if templates:
            self.redis_client.set(redis_key, json.dumps(templates), 300)
            return [Template.from_dict(template) for template in templates]
        return []

    def get_templates_paginated(self, page=1, size=10, t_id=None, t_name=None, t_description=None):
        where = []
        params = []
        if t_id:
            where.append("t_id = %s")
            params.append(t_id)
        if t_name:
            where.append("t_name LIKE %s")
            params.append(f"%{t_name}%")
        if t_description:
            where.append("t_description LIKE %s")
            params.append(f"%{t_description}%")
        where_clause = " AND ".join(where) or "1=1"

        # 总数
        cnt_sql = f"SELECT COUNT(*) AS cnt FROM templates WHERE {where_clause}"
        total = self.mysql_client.execute_query_one(
            cnt_sql, tuple(params))['cnt']

        # 分页数据
        offset = (page - 1) * size
        list_sql = f"SELECT t_id, t_name, t_description FROM templates WHERE {where_clause} ORDER BY t_id DESC LIMIT %s OFFSET %s"
        rows = self.mysql_client.execute_query(
            list_sql, tuple(params + [size, offset]))
        templates = [Template.from_dict(r) for r in rows]
        return templates, total

    def get_template_detail(self, t_id):
        redis_key = f"template_detail:{t_id}"
        template = self.redis_client.get(redis_key)
        if template:
            return Template.from_dict(json.loads(template))
        mysql_query = "SELECT * FROM templates WHERE t_id = %s"
        params = (t_id,)
        template = self.mysql_client.execute_query_one(mysql_query, params)
        if template:
            template = Template(
                t_id, template['t_author'], template['t_name'], template['t_description'], template['create_time'], template['update_time'])
            self.redis_client.set(redis_key, json.dumps(
                Template.to_dict(template)), 300)
            return template
        return None

    def get_template_file(self, t_id, filename):
        template_dir = os.path.join(
            self.app.config['TEMPLATE_FOLDER'], str(t_id))
        safe_dir = os.path.abspath(template_dir)
        safe_path = os.path.abspath(os.path.join(template_dir, filename))
        if not safe_path.startswith(safe_dir):
            return None
        return send_from_directory(template_dir, filename)

    def get_main_file(self, t_id):
        template_folder = os.path.join(
            self.app.config['TEMPLATE_FOLDER'], str(t_id))
        if not os.path.exists(template_folder):
            return None
        html_path = os.path.join(template_folder, 'index.html')
        css_path = os.path.join(template_folder, 'index.css')
        js_path = os.path.join(template_folder, 'index.js')
        screenshot_path = os.path.join(template_folder, 'index.jpg')
        html_file, css_file, js_file, screenshot_file = None, None, None, None
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
                html_file = f.read()
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8', errors='replace') as f:
                css_file = f.read()
        if os.path.exists(js_path):
            with open(js_path, 'r', encoding='utf-8', errors='replace') as f:
                js_file = f.read()
        if os.path.exists(screenshot_path):
            with open(screenshot_path, 'rb') as f:
                screenshot_file = f.read()
        if screenshot_file:
            screenshot_file = 'data:image/jpeg;base64,' + \
                base64.b64encode(screenshot_file).decode('utf-8')
        return html_file, css_file, js_file, screenshot_file

    def get_other_files_list(self, t_id):
        template_folder = os.path.join(
            self.app.config['TEMPLATE_FOLDER'], str(t_id))
        if not os.path.exists(template_folder):
            return None
        other_files = []
        for filename in os.listdir(template_folder):
            if filename in ("index.html", "index.css", "index.js", "index.jpg"):
                continue
            file_path = os.path.join(template_folder, filename)
            try:
                # 尝试以文本方式读取
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except UnicodeDecodeError:
                # 如果以文本方式读取失败，就以二进制方式读取，并转为Base64
                with open(file_path, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')
                    file_content = f'data:application/octet-stream;base64,{encoded}'
            other_files.append({
                'filename': filename,
                'file_content': file_content
            })
        return other_files

    def get_file(self, t_id, filename):
        template_folder = os.path.join(
            self.app.config['TEMPLATE_FOLDER'], str(t_id))
        if not os.path.exists(template_folder):
            return None
        file_path = os.path.join(template_folder, filename)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return f.read()
        return None

    def create_template(self, t_author, t_name, t_description):
        create_time = datetime.datetime.now()
        update_time = create_time
        mysql_query = "INSERT INTO templates (t_author, t_name, t_description, create_time, update_time) VALUES (%s, %s, %s, %s, %s)"
        params = (t_author, t_name, t_description,
                  create_time, update_time)
        t_id = self.mysql_client.execute_insert(mysql_query, params)
        if t_id:
            return Template(t_id, t_author, t_name, t_description, create_time, update_time)
        return None

    def create_template_folder(self, t_id):
        template_folder = os.path.join(
            self.app.config['TEMPLATE_FOLDER'], str(t_id))
        if not os.path.exists(template_folder):
            os.makedirs(template_folder, exist_ok=True)
            return True
        return False

    def update_template(self, t_id, t_name=None, t_description=None):
        update_time = datetime.datetime.now()
        params = []
        set_clause = []
        if t_name:
            set_clause.append("t_name = %s")
            params.append(t_name)
        if t_description:
            set_clause.append("t_description = %s")
            params.append(t_description)
        if not set_clause:
            return None
        set_clause.append("update_time = %s")
        params.append(update_time)
        params.append(t_id)
        mysql_query = f"UPDATE templates SET {', '.join(set_clause)} WHERE t_id = %s"
        self.mysql_client.execute_update(mysql_query, tuple(params))
        return self.get_template_detail(t_id)

    def update_main_file(self, t_id, html_file, css_file, js_file, screenshot_file):
        template_folder = os.path.join(
            self.app.config['TEMPLATE_FOLDER'], str(t_id))
        if not os.path.exists(template_folder):
            return None
        if html_file:
            html_path = os.path.join(template_folder, 'index.html')
            with open(html_path, 'w', encoding='utf-8', newline='') as f:
                f.write(html_file)
        if css_file:
            css_path = os.path.join(template_folder, 'index.css')
            with open(css_path, 'w', encoding='utf-8', newline='') as f:
                f.write(css_file)
        if js_file:
            js_path = os.path.join(template_folder, 'index.js')
            with open(js_path, 'w', encoding='utf-8', newline='') as f:
                f.write(js_file)
        if screenshot_file:
            screenshot_path = os.path.join(
                template_folder, 'index.jpg')
            screenshot_file[0].save(screenshot_path)
        return True

    def update_other_files(self, t_id, other_files):
        template_folder = os.path.join(
            self.app.config['TEMPLATE_FOLDER'], str(t_id))
        if not os.path.exists(template_folder):
            return None
        # 删除除主文件之外的所有其他文件
        for filename in os.listdir(template_folder):
            if filename in ("index.html", "index.css", "index.js", "index.jpg"):
                continue
            file_path = os.path.join(template_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        # 保存上传的新文件
        for file in other_files:
            filename = file.filename
            if filename:
                file_path = os.path.join(template_folder, filename)
                file.save(file_path)
        return True

    def delete_template_folder(self, t_id):
        template_folder = os.path.join(
            self.app.config['TEMPLATE_FOLDER'], str(t_id))
        if os.path.exists(template_folder):
            for filename in os.listdir(template_folder):
                file_path = os.path.join(template_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(template_folder)
        return True

    def delete_template(self, t_id):
        mysql_query = "DELETE FROM templates WHERE t_id = %s"
        params = (t_id,)
        self.mysql_client.execute_delete(mysql_query, params)
        template_folder = os.path.join(
            self.app.config['TEMPLATE_FOLDER'], str(t_id))
        if os.path.exists(template_folder):
            os.rmdir(template_folder)
        return True
