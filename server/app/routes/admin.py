from flask import request, Blueprint
from app import app
from app.common import response, admin_token_required, SECRET_KEY, get_mysql_client, redis_client
from app.models.Admin import Admin, AdminModel
from app.models.User import User, UserModel
from app.models.Work import Work, WorkModel
from app.models.Template import Template, TemplateModel
import bcrypt
import jwt


admin_bp = Blueprint('admin', __name__)


# 管理员登录接口
@admin_bp.route('/login', methods=['POST'])
def login_admin():
    try:
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return response(400, '登录失败，不能为空！')

        admin = admin_model.get_admin_by_email(email)
        if not admin or not bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            return response(401, '登录失败，邮箱或密码错误！')

        admin_model.update_last_login_time(admin.email)

        admin_token = jwt.encode(
            {'admin_id': admin.admin_id}, SECRET_KEY, algorithm="HS256")
        return response(200, '登录成功！', {'admin_token': admin_token})
    except Exception as e:
        app.logger.error(f"登录失败: {e}")
        return response(500, '登录失败！')


# 管理员登出接口
@admin_bp.route('/logout', methods=['POST'])
@admin_token_required
def logout_admin(current_admin):
    return response(200, '登出成功！')


# 修改管理员信息接口
@admin_bp.route('/set', methods=['POST'])
@admin_token_required
def update_admin_info(current_admin):
    try:
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        data = request.get_json()
        new_adminname = data.get('adminname')
        new_email = data.get('email')
        password = data.get('password')

        if not new_adminname or not new_email or not password:
            return response(400, '修改失败，不能为空！')

        admin_id = current_admin.admin_id

        admin = admin_model.get_admin_by_email(current_admin.email)
        if not admin or not bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            return response(401, '密码错误！')

        if new_email != admin.email:
            existing_admin = admin_model.get_admin_by_email(new_email)
            if existing_admin:
                return response(400, '修改失败，邮箱已注册！')

        admin_data = admin_model.update_admin_info(
            admin_id, new_adminname, new_email)
        admin_data_dict = Admin.to_dict(admin_data)
        admin_data_dict.pop('password', None)
        return response(200, '管理员信息修改成功！', admin_data_dict)
    except Exception as e:
        app.logger.error(f"修改管理员信息失败: {e}")
        return response(500, '修改管理员信息失败！')


# 获取管理员信息接口
@admin_bp.route('/get', methods=['GET'])
@admin_token_required
def get_admin_info(current_admin):
    try:
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        admin = admin_model.get_admin_by_email(current_admin.email)
        if not admin:
            return response(404, '管理员未找到！')
        admin_data_dict = Admin.to_dict(admin)
        admin_data_dict.pop('password', None)
        return response(200, '获取成功！', admin_data_dict)
    except Exception as e:
        app.logger.error(f"获取管理员信息失败: {e}")
        return response(500, '获取管理员信息失败！')


# 修改管理员密码接口
@admin_bp.route('/password', methods=['POST'])
@admin_token_required
def update_admin_password(current_admin):
    try:
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        data = request.get_json()
        old_password = data.get('oldPassword')
        new_password = data.get('newPassword')

        if not old_password or not new_password:
            return response(400, '修改失败，不能为空！')

        admin = admin_model.get_admin_by_email(current_admin.email)
        if not admin or not bcrypt.checkpw(old_password.encode('utf-8'), admin.password.encode('utf-8')):
            return response(401, '旧密码错误！')

        admin_model.update_password(admin.email, new_password)
        return response(200, '密码修改成功！')
    except Exception as e:
        app.logger.error(f"修改管理员密码失败: {e}")
        return response(500, '修改管理员密码失败！')


# 注销管理员账户接口
@admin_bp.route('/del', methods=['POST'])
@admin_token_required
def delete_admin_account(current_admin):
    try:
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        data = request.get_json()
        password = data.get('password')

        if not password:
            return response(400, '密码不能为空！')

        admin = admin_model.get_admin_by_email(current_admin.email)
        if not admin or not bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            return response(401, '密码错误！')

        admin_model.delete_admin(admin.email)
        return response(200, '管理员账户注销成功！')
    except Exception as e:
        app.logger.error(f"注销管理员账户失败: {e}")
        return response(500, '注销管理员账户失败！')


# 管理员验证接口
@admin_bp.route('/verify', methods=['POST'])
@admin_token_required
def verify_admin(current_admin):
    return response(200, '管理员验证成功！', Admin.to_dict(current_admin))


# 获取用户列表接口
@admin_bp.route('/user/list', methods=['GET'])
@admin_token_required
def get_users(current_admin):
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)
        u_id = request.args.get('u_id', type=int)
        user_id = request.args.get('user_id', type=str)
        username = request.args.get('username', type=str)
        email = request.args.get('email', type=str)

        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        users, total = admin_model.get_users_paginated(
            page, size, u_id, user_id, username, email
        )
        data = {
            "list": [User.to_dict(u) for u in users],
            "total": total
        }
        return response(200, '获取用户列表成功！', data)
    except Exception as e:
        app.logger.error(f"获取用户列表失败: {e}")
        return response(500, '获取用户列表失败！')


# 获取用户详情接口
@admin_bp.route('/user/get/<int:u_id>', methods=['GET'])
@admin_token_required
def get_user_info(current_admin, u_id):
    try:
        mysql_client = get_mysql_client()
        user_model = UserModel(mysql_client, redis_client)
        user = user_model.get_user_by_u_id(u_id)
        if not user:
            return response(404, '用户未找到！')
        return response(200, '获取成功！', User.to_dict(user))
    except Exception as e:
        app.logger.error(f"获取用户信息失败: {e}")
        return response(500, '获取用户信息失败！')


# 编辑用户信息接口
@admin_bp.route('/user/set', methods=['POST'])
@admin_token_required
def update_user_info(current_admin):
    try:
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        user_model = UserModel(mysql_client, redis_client)
        data = request.get_json()
        new_username = data.get('username')
        new_email = data.get('email')
        password = data.get('password')
        u_id = data.get('u_id')

        if not new_username or not new_email or not password or not u_id:
            return response(400, '修改失败，不能为空！')

        admin = admin_model.get_admin_by_email(current_admin.email)
        if not admin or not bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            return response(401, '密码错误！')

        user = user_model.get_user_by_u_id(u_id)
        if not user:
            return response(404, '用户未找到！')

        if new_email != user.email:
            existing_user = user_model.get_user_by_email(new_email)
            if existing_user:
                return response(400, '修改失败，邮箱已注册！')

        user_data = user_model.update_user_info(
            user.user_id, new_username, new_email)
        user_data_dict = User.to_dict(user_data)
        user_data_dict.pop('password', None)
        user_data_dict.pop('u_id', None)

        return response(200, '用户信息修改成功！', user_data_dict)
    except Exception as e:
        app.logger.error(f"修改用户信息失败: {e}")
        return response(500, '修改用户信息失败！')


# 删除用户接口
@admin_bp.route('/user/del', methods=['POST'])
@admin_token_required
def delete_user(current_admin):
    try:
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        user_model = UserModel(mysql_client, redis_client)
        work_model = WorkModel(mysql_client, redis_client, app)
        data = request.get_json()
        password = data.get('password')
        u_id = data.get('u_id')

        if not password:
            return response(400, '密码不能为空！')

        if not u_id:
            return response(401, 'ID不能为空！')

        admin = admin_model.get_admin_by_email(current_admin.email)
        if not admin or not bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            return response(402, '密码错误！')

        user = user_model.get_user_by_u_id(u_id)
        if not user:
            return response(404, '用户未找到！')

        user_work_file = work_model.remove_user_work_folder(
            user.user_id, user.u_id)
        if not user_work_file:
            return response(500, '注销账户失败！作品文件夹异常！')

        user_model.delete_user(user.email)
        return response(200, '账户注销成功！')
    except Exception as e:
        app.logger.error(f"注销账户失败: {e}")
        return response(500, '注销账户失败！')


# 获取作品列表接口
@admin_bp.route('/work/list', methods=['GET'])
@admin_token_required
def get_works(current_admin):
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)
        w_id = request.args.get('w_id', type=int)
        u_id = request.args.get('u_id', type=int)
        w_name = request.args.get('w_name', type=str)
        w_description = request.args.get('w_description', type=str)
        t_id = request.args.get('t_id', type=int)

        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        works, total = admin_model.get_works_paginated(
            page, size, w_id, u_id, w_name, w_description, t_id
        )
        data = {
            "list": [Work.to_dict(w) for w in works],
            "total": total
        }
        return response(200, '获取作品列表成功！', data)
    except Exception as e:
        app.logger.error(f"获取作品列表失败: {e}")
        return response(500, '获取作品列表失败！')


# 获取作品详情接口
@admin_bp.route('/work/get/<int:w_id>', methods=['GET'])
@admin_token_required
def get_work_detail(current_admin, w_id):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        work = work_model.get_work_by_w_id(w_id)
        if not work:
            return response(404, '作品未找到！')
        return response(200, '获取成功！', Work.to_dict(work))
    except Exception as e:
        app.logger.error(f"获取作品详情失败: {e}")
        return response(500, '获取作品详情失败！')


# 获取作品主文件接口
@admin_bp.route('/work/files/main/<int:w_id>', methods=['GET'])
@admin_token_required
def get_work_main_file(current_admin, w_id):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        user_model = UserModel(mysql_client, redis_client)
        work = work_model.get_work_by_w_id(w_id)
        if not work:
            return response(404, '作品未找到！')
        user_id = user_model.get_user_by_u_id(work.u_id).user_id
        html_file, css_file, js_file = work_model.get_main_file(user_id, w_id)
        return response(200, '获取成功！', {'html': html_file, 'css': css_file, 'javascript': js_file})
    except Exception as e:
        app.logger.error(f"获取作品主文件失败: {e}")
        return response(500, '获取作品主文件失败！')


# 获取作品其他文件接口
@admin_bp.route('/work/files/other/<int:w_id>', methods=['GET'])
@admin_token_required
def get_work_other_files(current_admin, w_id):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        user_model = UserModel(mysql_client, redis_client)
        work = work_model.get_work_by_w_id(w_id)
        if not work:
            return response(404, '作品未找到！')
        user_id = user_model.get_user_by_u_id(work.u_id).user_id
        files_response = work_model.get_other_files_list(user_id, w_id)
        if not files_response:
            return response(404, '作品其他文件未找到！')
        return files_response
    except Exception as e:
        app.logger.error(f"获取作品其他文件失败: {e}")
        return response(500, '获取作品其他文件失败！')


# 获取作品文件接口
@admin_bp.route('/file/<int:w_id>/<path:filename>', methods=['GET'])
@admin_token_required
def get_work_file(current_admin, w_id, filename):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        user_model = UserModel(mysql_client, redis_client)
        work = work_model.get_work_by_w_id(w_id)
        if not work:
            return response(404, '作品未找到！')
        user_id = user_model.get_user_by_u_id(work.u_id).user_id
        file_response = work_model.get_file(user_id, w_id, filename)
        if not file_response:
            return response(404, '作品文件未找到！')
        return file_response
    except Exception as e:
        app.logger.error(f"获取作品文件失败: {e}")
        return response(500, '获取作品文件失败！')


# 编辑作品信息接口
@admin_bp.route('/work/set', methods=['POST'])
@admin_token_required
def update_work_info(current_admin):
    try:
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        work_model = WorkModel(mysql_client, redis_client, app)
        user_model = UserModel(mysql_client, redis_client)
        w_id = request.form.get('w_id')
        work_name = request.form.get('workName')
        work_description = request.form.get('workDescription')
        html_content = request.form.get('htmlContent')
        css_content = request.form.get('cssContent')
        js_content = request.form.get('jsContent')
        other_files = request.files.getlist('otherFiles')
        password = request.form.get('password')

        if not w_id or not work_name or not work_description:
            return response(400, '修改作品失败，不能为空！')

        admin = admin_model.get_admin_by_email(current_admin.email)
        if not admin or not bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            return response(401, '密码错误！')

        work = work_model.get_work_by_w_id(w_id)
        if not work:
            return response(404, '作品未找到！')

        work = work_model.update_work(
            work.u_id, w_id, work_name, work_description)
        if not work:
            return response(501, '修改作品失败！')

        user_id = user_model.get_user_by_u_id(work.u_id).user_id

        # 更新主文件
        main_file = work_model.update_main_file(
            user_id, w_id, html_content, css_content, js_content)
        if not main_file:
            return response(502, '修改作品失败！')

        # 更新其他文件
        if other_files:
            other_files = work_model.update_other_files(
                user_id, w_id, other_files)
            if not other_files:
                return response(503, '修改作品失败！')

        return response(200, '作品信息修改成功！')
    except Exception as e:
        app.logger.error(f"修改作品信息失败: {e}")
        return response(500, '修改作品信息失败！')


# 删除作品接口
@admin_bp.route('/work/del', methods=['POST'])
@admin_token_required
def delete_work(current_admin):
    try:
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        user_model = UserModel(mysql_client, redis_client)
        work_model = WorkModel(mysql_client, redis_client, app)
        data = request.get_json()
        password = data.get('password')
        w_id = data.get('w_id')

        if not password:
            return response(400, '密码不能为空！')

        if not w_id:
            return response(401, 'ID不能为空！')

        admin = admin_model.get_admin_by_email(current_admin.email)
        if not admin or not bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            return response(402, '密码错误！')

        work = work_model.get_work_by_w_id(w_id)
        if not work:
            return response(404, '作品未找到！')

        user = user_model.get_user_by_u_id(work.u_id)
        if not user:
            return response(404, '用户未找到！')

        work_model.delete_work(user.u_id, user.user_id, work.w_id)
        return response(200, '作品删除成功！')
    except Exception as e:
        app.logger.error(f"删除作品失败: {e}")
        return response(500, '删除作品失败！')


# 获取模板列表接口
@admin_bp.route('/template/list', methods=['GET'])
@admin_token_required
def get_templates(current_admin):
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)
        t_id = request.args.get('t_id', type=int)
        t_author = request.args.get('t_author', type=str)
        t_name = request.args.get('t_name', type=str)
        t_description = request.args.get('t_description', type=str)

        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        templates, total = admin_model.get_templates_paginated(
            page, size, t_id, t_author, t_name, t_description
        )
        data = {
            "list": [Template.to_dict(t) for t in templates],
            "total": total
        }
        return response(200, '获取模板列表成功！', data)
    except Exception as e:
        app.logger.error(f"获取模板列表失败: {e}")
        return response(500, '获取模板列表失败！')


# 获取模板详情接口
@admin_bp.route('/template/get/<int:t_id>', methods=['GET'])
@admin_token_required
def get_template_detail(current_admin, t_id):
    try:
        mysql_client = get_mysql_client()
        template_model = TemplateModel(mysql_client, redis_client, app)
        template = template_model.get_template_detail(t_id)
        if not template:
            return response(404, '模板未找到！')
        return response(200, '获取成功！', Template.to_dict(template))
    except Exception as e:
        app.logger.error(f"获取模板详情失败: {e}")
        return response(500, '获取模板详情失败！')


# 获取模板主文件接口
@admin_bp.route('/template/files/main/<int:t_id>', methods=['GET'])
@admin_token_required
def get_template_main_file(current_admin, t_id):
    try:
        mysql_client = get_mysql_client()
        template_model = TemplateModel(mysql_client, redis_client, app)
        template = template_model.get_template_detail(t_id)
        if not template:
            return response(404, '模板未找到！')
        html_file, css_file, js_file, screenshot_file = template_model.get_main_file(
            t_id)
        return response(200, '获取成功！', {'html': html_file, 'css': css_file, 'javascript': js_file, 'screenshot': screenshot_file})
    except Exception as e:
        app.logger.error(f"获取模板主文件失败: {e}")
        return response(500, '获取模板主文件失败！')


# 获取模板其他文件接口
@admin_bp.route('/template/files/other/<int:t_id>', methods=['GET'])
@admin_token_required
def get_template_other_files(current_admin, t_id):
    try:
        mysql_client = get_mysql_client()
        template_model = TemplateModel(mysql_client, redis_client, app)
        template = template_model.get_template_detail(t_id)
        if not template:
            return response(404, '模板未找到！')
        files_response = template_model.get_other_files_list(t_id)
        if not files_response:
            return response(404, '模板其他文件未找到！')
        return files_response
    except Exception as e:
        app.logger.error(f"获取模板其他文件失败: {e}")
        return response(500, '获取模板其他文件失败！')


# 获取模板文件接口
@admin_bp.route('/template/file/<int:t_id>/<path:filename>', methods=['GET'])
@admin_token_required
def get_template_file(current_admin, t_id, filename):
    try:
        mysql_client = get_mysql_client()
        template_model = TemplateModel(mysql_client, redis_client, app)
        template = template_model.get_template_detail(t_id)
        if not template:
            return response(404, '模板未找到！')
        file_response = template_model.get_file(t_id, filename)
        if not file_response:
            return response(404, '模板文件未找到！')
        return file_response
    except Exception as e:
        app.logger.error(f"获取模板文件失败: {e}")
        return response(500, '获取模板文件失败！')


# 创建模板接口
@admin_bp.route('/template/create', methods=['POST'])
@admin_token_required
def create_template(current_admin):
    try:
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        template_model = TemplateModel(mysql_client, redis_client, app)
        t_name = request.form.get('t_name')
        t_description = request.form.get('t_description')
        html_content = request.form.get('htmlContent')
        css_content = request.form.get('cssContent')
        js_content = request.form.get('jsContent')
        other_files = request.files.getlist('otherFiles')
        screenshot = request.files.getlist('screenshot')
        password = request.form.get('password')

        admin = admin_model.get_admin_by_email(current_admin.email)
        if not admin or not bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            return response(402, '密码错误！')

        if not t_name or not t_description:
            return response(400, '创建模板失败，不能为空！')

        t_author = admin.a_id

        template = template_model.create_template(
            t_author, t_name, t_description)
        if not template:
            return response(500, '创建模板失败！')

        template_model.create_template_folder(template.t_id)
        template_main_file = template_model.update_main_file(
            template.t_id, html_content, css_content, js_content, screenshot)
        if not template_main_file:
            template_model.delete_template_folder(template.t_id)
            template_model.delete_template(template.t_id)
            return response(501, '创建模板失败！')
        if other_files:
            template_other_files = template_model.update_other_files(
                template.t_id, other_files)
            if not template_other_files:
                template_model.delete_template_folder(template.t_id)
                template_model.delete_template(template.t_id)
                return response(502, '创建模板失败！')

        return response(200, '创建模板成功！', Template.to_dict(template))
    except Exception as e:
        app.logger.error(f"创建模板失败: {e}")
        return response(500, '创建模板失败！')


# 编辑模板接口
@admin_bp.route('/template/set', methods=['POST'])
@admin_token_required
def update_template_info(current_admin):
    try:
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        template_model = TemplateModel(mysql_client, redis_client, app)
        t_id = request.form.get('t_id')
        t_name = request.form.get('t_name')
        t_description = request.form.get('t_description')
        html_content = request.form.get('htmlContent')
        css_content = request.form.get('cssContent')
        js_content = request.form.get('jsContent')
        other_files = request.files.getlist('otherFiles')
        screenshot = request.files.getlist('screenshot')
        password = request.form.get('password')

        if not t_id or not t_name or not t_description:
            return response(400, '修改模板失败，不能为空！')

        admin = admin_model.get_admin_by_email(current_admin.email)
        if not admin or not bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            return response(401, '密码错误！')

        template = template_model.update_template(t_id, t_name, t_description)
        if not template:
            return response(501, '修改模板失败！')

        template_main_file = template_model.update_main_file(
            t_id, html_content, css_content, js_content, screenshot)
        if not template_main_file:
            return response(502, '修改模板失败！')

        if other_files:
            template_other_files = template_model.update_other_files(
                t_id, other_files)
            if not template_other_files:
                return response(503, '修改模板失败！')

        return response(200, '模板信息修改成功！', Template.to_dict(template))
    except Exception as e:
        app.logger.error(f"修改模板信息失败: {e}")
        return response(500, '修改模板信息失败！')


# 删除模板接口
@admin_bp.route('/template/del', methods=['POST'])
@admin_token_required
def delete_template(current_admin):
    try:
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        template_model = TemplateModel(mysql_client, redis_client, app)
        data = request.get_json()
        password = data.get('password')
        t_id = data.get('t_id')

        if not password:
            return response(400, '密码不能为空！')

        if not t_id:
            return response(401, '模板id不能为空！')

        admin = admin_model.get_admin_by_email(current_admin.email)
        if not admin or not bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            return response(402, '密码错误！')

        template = template_model.get_template_detail(t_id)
        if not template:
            return response(404, '模板未找到！')

        template_model.delete_template_folder(t_id)
        template_model.delete_template(t_id)
        return response(200, '模板删除成功！')
    except Exception as e:
        app.logger.error(f"删除模板失败: {e}")
        return response(500, '删除模板失败！')


# 获取管理员列表接口
@admin_bp.route('/admin/list', methods=['GET'])
@admin_token_required
def get_admins(current_admin):
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)
        a_id = request.args.get('a_id', type=int)
        admin_id = request.args.get('admin_id', type=str)
        adminname = request.args.get('adminname', type=str)
        email = request.args.get('email', type=str)

        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        admins, total = admin_model.get_admins_paginated(
            page, size, a_id, admin_id,  adminname, email
        )
        data = {
            "list": [Admin.to_dict(a) for a in admins],
            "total": total
        }
        return response(200, '获取管理员列表成功！', data)
    except Exception as e:
        app.logger.error(f"获取管理员列表失败: {e}")
        return response(500, '获取管理员列表失败！')


# 添加管理员接口
@admin_bp.route('/admin/create', methods=['POST'])
@admin_token_required
def create_admin_account(current_admin):
    try:
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        data = request.get_json()
        adminname = data.get('adminname')
        email = data.get('email')
        password = data.get('password')

        if not adminname or not email or not password:
            return response(400, '注册失败，不能为空！')

        existing_admin = admin_model.get_admin_by_email(email)
        if existing_admin:
            return response(401, '注册失败，邮箱已注册！')

        admin = admin_model.create_admin(adminname, email, password)

        if not admin:
            return response(500, '注册失败！管理员创建失败！')

        return response(200, '注册成功！', Admin.to_dict(admin))
    except Exception as e:
        app.logger.error(f"添加管理员失败: {e}")
        return response(500, '添加管理员失败！')
