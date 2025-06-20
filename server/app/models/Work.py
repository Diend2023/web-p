from app.database import MySQLClient
from app.database import RedisClient
from flask import send_from_directory
import json
import datetime
import os
import shutil
import base64


class Work:
    def __init__(self, w_id, u_id, t_id, w_name, w_description, visit_count, create_time, update_time):
        self.w_id = w_id
        self.u_id = u_id
        self.t_id = t_id
        self.w_name = w_name
        self.w_description = w_description
        self.visit_count = visit_count
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
        从字典创建 Work 对象。
        """
        data = Work._convert_datetime(data)
        return Work(
            w_id=data.get('w_id'),
            u_id=data.get('u_id'),
            t_id=data.get('t_id'),
            w_name=data.get('w_name'),
            w_description=data.get('w_description'),
            visit_count=data.get('visit_count'),
            create_time=data.get('create_time'),
            update_time=data.get('update_time')
        )

    @staticmethod
    def to_dict(work):
        """
        将 Work 对象转换为字典。
        """
        return Work._convert_datetime({
            'w_id': work.w_id,
            'u_id': work.u_id,
            't_id': work.t_id,
            'w_name': work.w_name,
            'w_description': work.w_description,
            'visit_count': work.visit_count,
            'create_time': work.create_time,
            'update_time': work.update_time
        })


class WorkModel:
    def __init__(self, mysql_client: MySQLClient, redis_client: RedisClient, app):
        self.mysql_client = mysql_client
        self.redis_client = redis_client
        self.app = app

    def get_works(self, u_id):
        redis_key = f"user_works:{u_id}"
        works_data = self.redis_client.get(redis_key)
        if works_data:
            works_data = json.loads(works_data)
            return [Work.from_dict(work) for work in works_data]

        mysql_query = "SELECT * FROM works WHERE u_id = %s"
        params = (u_id,)
        works_data = self.mysql_client.execute_query(mysql_query, params)
        if works_data:
            works = [Work.from_dict(work) for work in works_data]
            self.redis_client.set(redis_key, json.dumps(
                [Work.to_dict(work) for work in works]), 300)
            return works
        return []

    def get_works_paginated(self, u_id, page, size,
                            w_id=None, w_name=None, w_description=None, t_id=None):
        where = ["u_id = %s"]
        params = [u_id]
        if w_id:
            where.append("w_id = %s")
            params.append(w_id)
        if w_name:
            where.append("w_name LIKE %s")
            params.append(f"%{w_name}%")
        if w_description:
            where.append("w_description LIKE %s")
            params.append(f"%{w_description}%")
        if t_id:
            where.append("t_id = %s")
            params.append(t_id)
        where_clause = " AND ".join(where)

        cnt_sql = f"SELECT COUNT(*) AS cnt FROM works WHERE {where_clause}"
        total = self.mysql_client.execute_query_one(
            cnt_sql, tuple(params))['cnt']

        offset = (page - 1) * size
        list_sql = f"""
          SELECT * FROM works
          WHERE {where_clause}
          ORDER BY create_time DESC
          LIMIT %s OFFSET %s
        """
        rows = self.mysql_client.execute_query(list_sql,
                                               tuple(params + [size, offset]))
        works = [Work.from_dict(r) for r in rows]
        return works, total

    def get_work_by_id(self, u_id, w_id):
        works_data = self.redis_client.get(f"user_works:{u_id}")
        if works_data:
            works_data = json.loads(works_data)
            for work in works_data:
                if work['w_id'] == w_id:
                    return Work.from_dict(work)
        # 从 MySQL 中获取数据
        mysql_query = "SELECT * FROM works WHERE u_id = %s AND w_id = %s"
        params = (u_id, w_id)
        work_data = self.mysql_client.execute_query_one(mysql_query, params)
        if work_data:
            return Work.from_dict(work_data)
        return None

    def get_work_by_w_id(self, w_id):
        mysql_query = "SELECT * FROM works WHERE w_id = %s"
        params = (w_id,)
        work_data = self.mysql_client.execute_query_one(mysql_query, params)
        if work_data:
            return Work.from_dict(work_data)
        return None

    def get_work_visit_count(self, w_id):
        mysql_query = "SELECT visit_count FROM works WHERE w_id = %s"
        params = (w_id,)
        result = self.mysql_client.execute_query_one(mysql_query, params)
        if result:
            return result['visit_count']
        return None

    def get_file(self, user_id, w_id, filename):
        user_work_folder = os.path.join(
            self.app.config['USER_WORK_FOLDER'], str(user_id), str(w_id))
        file_path = os.path.join(user_work_folder, filename)
        if os.path.exists(file_path):
            return send_from_directory(user_work_folder, filename)
        return None

    def get_main_file(self, user_id, w_id):
        user_work_folder = os.path.join(
            self.app.config['USER_WORK_FOLDER'], str(user_id), str(w_id))
        html_path = os.path.join(user_work_folder, 'index.html')
        css_path = os.path.join(user_work_folder, 'index.css')
        js_path = os.path.join(user_work_folder, 'index.js')
        html_file, css_file, js_file = None, None, None
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
                html_file = f.read()
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8', errors='replace') as f:
                css_file = f.read()
        if os.path.exists(js_path):
            with open(js_path, 'r', encoding='utf-8', errors='replace') as f:
                js_file = f.read()
        return html_file, css_file, js_file

    def get_other_files_list(self, user_id, w_id):
        user_work_folder = os.path.join(
            self.app.config['USER_WORK_FOLDER'], str(user_id), str(w_id))
        other_files = []
        for filename in os.listdir(user_work_folder):
            if filename.endswith('index.html') or filename.endswith('index.css') or filename.endswith('index.js'):
                continue
            file_path = os.path.join(user_work_folder, filename)
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

    def get_other_files_list_name(self, user_id, w_id):
        user_work_folder = os.path.join(
            self.app.config['USER_WORK_FOLDER'], str(user_id), str(w_id))
        other_files = []
        for filename in os.listdir(user_work_folder):
            if filename.endswith('index.html') or filename.endswith('index.css') or filename.endswith('index.js'):
                continue
            other_files.append(filename)
        return other_files

    def get_other_file(self, user_id, w_id, filename):
        user_work_folder = os.path.join(
            self.app.config['USER_WORK_FOLDER'], str(user_id), str(w_id))
        file_path = os.path.join(user_work_folder, filename)
        try:
            # 尝试以文本方式读取
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except UnicodeDecodeError:
            # 如果以文本方式读取失败，就以二进制方式读取，并转为Base64
            with open(file_path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
                file_content = f'data:application/octet-stream;base64,{encoded}'
        return file_content

    def create_work(self, u_id, user_id, w_name, w_description):
        create_time = datetime.datetime.now()
        update_time = create_time
        mysql_query = "INSERT INTO works (u_id, w_name, w_description, create_time, update_time) VALUES (%s, %s, %s, %s, %s)"
        params = (u_id, w_name, w_description, create_time, update_time)
        w_id = self.mysql_client.execute_insert(mysql_query, params)
        work = Work(w_id, u_id, None, w_name, w_description, 0,
                    create_time, update_time)  # t_id 设置为 None
        works_data = self.redis_client.get(f"user_works:{u_id}")
        if works_data:
            works_data = json.loads(works_data)
            works_data.append(Work.to_dict(work))
            self.redis_client.set(f"user_works:{u_id}", json.dumps(works_data))
        else:
            works_data = [Work.to_dict(work)]
            self.redis_client.set(f"user_works:{u_id}", json.dumps(works_data))

        # 在 WORK_FOLDER/user_id 中创建一个名字为 w_id 的文件夹
        user_work_folder = os.path.join(
            self.app.config['USER_WORK_FOLDER'], user_id, str(w_id))
        os.makedirs(user_work_folder, exist_ok=True)

        return work

    def create_work_from_template(self, u_id, user_id, t_id, w_name, w_description):
        create_time = datetime.datetime.now()
        update_time = create_time
        mysql_query = "INSERT INTO works (u_id, t_id, w_name, w_description, create_time, update_time) VALUES (%s, %s, %s, %s, %s, %s)"
        params = (u_id, t_id, w_name, w_description, create_time, update_time)
        w_id = self.mysql_client.execute_insert(mysql_query, params)
        work = Work(w_id, u_id, t_id, w_name, w_description,
                    0, create_time, update_time)
        works_data = self.redis_client.get(f"user_works:{u_id}")
        if works_data:
            works_data = json.loads(works_data)
            works_data.append(Work.to_dict(work))
            self.redis_client.set(f"user_works:{u_id}", json.dumps(works_data))
        else:
            works_data = [Work.to_dict(work)]
            self.redis_client.set(f"user_works:{u_id}", json.dumps(works_data))

        # 在 WORK_FOLDER/user_id 中创建一个名字为 w_id 的文件夹
        user_work_folder = os.path.join(
            self.app.config['USER_WORK_FOLDER'], user_id, str(w_id))
        os.makedirs(user_work_folder, exist_ok=True)

        # 将模板文件复制到 user_work_folder 中
        template_dir = os.path.join(
            self.app.config['TEMPLATE_FOLDER'], str(t_id))
        for file in os.listdir(template_dir):
            # 如果是 t_id.jpg，则不复制
            if file == "index.jpg":
                continue
            src_file = os.path.join(template_dir, file)
            if not os.path.isfile(src_file):
                continue
            dst_file = os.path.join(user_work_folder, file)
            shutil.copy(src_file, dst_file)

        return work

    def update_main_file(self, user_id, w_id, html_file, css_file, js_file):
        user_work_folder = os.path.join(
            self.app.config['USER_WORK_FOLDER'], str(user_id), str(w_id))
        if not os.path.exists(user_work_folder):
            return False
        html_path = os.path.join(user_work_folder, 'index.html')
        css_path = os.path.join(user_work_folder, 'index.css')
        js_path = os.path.join(user_work_folder, 'index.js')
        with open(html_path, 'w', encoding='utf-8', newline='') as f:
            f.write(html_file)
        with open(css_path, 'w', encoding='utf-8', newline='') as f:
            f.write(css_file)
        with open(js_path, 'w', encoding='utf-8', newline='') as f:
            f.write(js_file)
        return True

    def update_other_files(self, user_id, w_id, other_files):
        """
        更新其他文件，先删除当前目录中除主文件（w_id.html, w_id.css, w_id.js）之外的所有文件，
        然后保存上传的新文件。
        """
        user_work_folder = os.path.join(
            self.app.config['USER_WORK_FOLDER'], str(user_id), str(w_id))
        if not os.path.exists(user_work_folder):
            return False
        # 删除除主文件之外的所有其他文件
        for filename in os.listdir(user_work_folder):
            if filename in ("index.html", "index.css", "index.js"):
                continue
            file_path = os.path.join(user_work_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        # 保存上传的新文件
        for file in other_files:
            filename = file.filename
            if filename:
                file_path = os.path.join(user_work_folder, filename)
                file.save(file_path)
        return True

    def delete_file(self, user_id, w_id, filename):
        user_work_folder = os.path.join(
            self.app.config['USER_WORK_FOLDER'], str(user_id), str(w_id))
        file_path = os.path.join(user_work_folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def update_work(self, u_id, w_id, w_name, w_description):
        update_time = datetime.datetime.now()
        mysql_query = "UPDATE works SET w_name = %s, w_description = %s, update_time = %s WHERE w_id = %s"
        params = (w_name, w_description, update_time, w_id)
        self.mysql_client.execute_update(mysql_query, params)
        work = self.get_work_by_id(u_id, w_id)
        if work:
            work.w_name = w_name
            work.w_description = w_description
            work.update_time = update_time
            works_data = self.redis_client.get(f"user_works:{work.u_id}")
            if works_data:
                works_data = json.loads(works_data)
                for w in works_data:
                    if str(w['w_id']) == w_id:
                        w['w_name'] = w_name
                        w['w_description'] = w_description
                        w['update_time'] = update_time.strftime(
                            '%Y-%m-%d %H:%M:%S')
                        self.redis_client.set(
                            f"user_works:{work.u_id}", json.dumps(works_data))
                        break
        return work

    def update_work_visit_count(self, w_id):
        mysql_query = "UPDATE works SET visit_count = visit_count + 1 WHERE w_id = %s"
        params = (w_id,)
        self.mysql_client.execute_update(mysql_query, params)
        mysql_query = "SELECT u_id FROM works WHERE w_id = %s"
        params = (w_id,)
        result = self.mysql_client.execute_query_one(mysql_query, params)
        if result:
            u_id = result['u_id']
            works_data = self.redis_client.get(f"user_works:{u_id}")
            if works_data:
                works_data = json.loads(works_data)
                for work in works_data:
                    if work['w_id'] == w_id:
                        work['visit_count'] += 1
                        self.redis_client.set(
                            f"user_works:{u_id}", json.dumps(works_data))
                        break

    def delete_work(self, u_id, user_id, w_id):
        user_work_folder = os.path.join(
            self.app.config['USER_WORK_FOLDER'], str(user_id), str(w_id))
        if os.path.exists(user_work_folder):
            shutil.rmtree(user_work_folder)
        mysql_query = "DELETE FROM works WHERE w_id = %s"
        params = (w_id,)
        self.mysql_client.execute_delete(mysql_query, params)
        works_data = self.redis_client.get(f"user_works:{u_id}")
        if works_data:
            works_data = json.loads(works_data)
            for work in works_data:
                if work['w_id'] == w_id:
                    works_data.remove(work)
                    self.redis_client.set(
                        f"user_works:{u_id}", json.dumps(works_data))
                    break
        return True

    def make_user_work_folder(self, user_id):
        """
        在 WORK_FOLDER 中创建一个名字为 user_id 的文件夹。
        """
        user_work_folder = os.path.join(
            self.app.config['USER_WORK_FOLDER'], user_id)
        os.makedirs(user_work_folder, exist_ok=True)
        if os.path.exists(user_work_folder):
            return True
        return False

    def remove_user_work_folder(self, user_id, u_id):
        """
        删除 WORK_FOLDER 中名字为 user_id 的文件夹。
        """
        user_work_folder = os.path.join(
            self.app.config['USER_WORK_FOLDER'], user_id)
        if os.path.exists(user_work_folder):
            shutil.rmtree(user_work_folder)
            self.redis_client.delete(f"user_works:{u_id}")
            return True
        return False
