from flask import request, Blueprint
from app import app
from app.common import response, token_required, get_mysql_client, redis_client
from app.models.Work import Work, WorkModel
from app.models.User import UserModel


work_bp = Blueprint('work', __name__)


# 获取作品列表接口
@work_bp.route('/list', methods=['GET'])
@token_required
def get_works(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)
        w_id = request.args.get('w_id', type=int)
        w_name = request.args.get('w_name', type=str)
        w_description = request.args.get('w_description', type=str)
        t_id = request.args.get('t_id', type=int)

        mysql_client = get_mysql_client()
        model = WorkModel(mysql_client, redis_client, app)
        works, total = model.get_works_paginated(
            current_user.u_id, page, size,
            w_id, w_name, w_description, t_id
        )

        data = {"list": [Work.to_dict(w) for w in works], "total": total}
        
        return response(200, '获取成功！', data)
    except Exception as e:
        app.logger.error(f"获取作品列表失败: {e}")
        return response(500, '获取作品列表失败！')


# 获取作品访问量接口
@work_bp.route('/visit/<int:w_id>', methods=['GET'])
@token_required
def get_work_visit_count(current_user, w_id):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        work = work_model.get_work_by_id(current_user.u_id, w_id)
        if not work:
            return response(404, '作品未找到！')
        visit_count = work_model.get_work_visit_count(w_id)
        if visit_count is None:
            return response(404, '作品访问量未找到！')
        return response(200, '获取成功！', {'visit_count': visit_count})
    except Exception as e:
        app.logger.error(f"获取作品访问量失败: {e}")
        return response(500, '获取作品访问量失败！')


# 获取总作品访问量接口
@work_bp.route('/visit/all', methods=['GET'])
@token_required
def get_all_work_visit_count(current_user):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        works = work_model.get_works(current_user.u_id)
        if not works:
            return response(404, '作品未找到！')
        total_visit_count = sum(work.visit_count for work in works)
        return response(200, '获取成功！', {'total_visit_count': total_visit_count})
    except Exception as e:
        app.logger.error(f"获取总作品访问量失败: {e}")
        return response(500, '获取总作品访问量失败！')


# 访问作品接口
@work_bp.route('/file/<string:user_id>/<int:w_id>/<path:filename>', methods=['GET'])
def get_work(user_id, w_id, filename):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        file_response = work_model.get_file(user_id, w_id, filename)
        if not file_response:
            return response(404, '作品文件未找到！')
        work_model.update_work_visit_count(w_id)
        return file_response
    except Exception as e:
        app.logger.error(f"获取作品文件失败: {e}")
        return response(500, '获取作品文件失败！')


# 获取作品文件接口
@work_bp.route('/file/<int:w_id>/<path:filename>', methods=['GET'])
def get_work_file(w_id, filename):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        user_model = UserModel(mysql_client, redis_client)
        work = work_model.get_work_by_w_id(w_id)
        if not work:
            return response(404, '作品未找到！')
        user_id = user_model.get_user_by_u_id(work.u_id).user_id
        if not user_id:
            return response(404, '用户未找到！')
        file_response = work_model.get_file(user_id, w_id, filename)
        if not file_response:
            return response(404, '作品文件未找到！')
        return file_response
    except Exception as e:
        app.logger.error(f"获取作品文件失败: {e}")
        return response(500, '获取作品文件失败！')


# 获取作品主文件接口
@work_bp.route('/files/main/<int:w_id>', methods=['GET'])
@token_required
def get_work_main_file(current_user, w_id):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        html_file, css_file, js_file = work_model.get_main_file(
            current_user.user_id, w_id)
        return response(200, '获取成功！', {'html': html_file, 'css': css_file, 'javascript': js_file})
    except Exception as e:
        app.logger.error(f"获取作品主文件失败: {e}")
        return response(500, '获取作品主文件失败！')


# 获取作品其他文件列表接口
@work_bp.route('/files/other/list/<int:w_id>', methods=['GET'])
@token_required
def get_work_other_files_list(current_user, w_id):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        files = work_model.get_other_files_list(current_user.user_id, w_id)
        files_dict = [Work.to_dict(file) for file in files]
        return response(200, '获取成功！', files_dict)
    except Exception as e:
        app.logger.error(f"获取作品其他文件列表失败: {e}")


# 获取作品其他文件接口
@work_bp.route('/files/other/<int:w_id>', methods=['GET'])
@token_required
def get_work_other_files(current_user, w_id):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        files_response = work_model.get_other_files_list(
            current_user.user_id, w_id)
        if not files_response:
            return response(404, '作品其他文件未找到！')
        return files_response
    except Exception as e:
        app.logger.error(f"获取作品其他文件失败: {e}")
        return response(500, '获取作品其他文件失败！')


# 获取作品详情接口
@work_bp.route('/detail/<int:w_id>', methods=['GET'])
@token_required
def get_work_detail(current_user, w_id):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        work = work_model.get_work_by_id(current_user.u_id, w_id)
        if not work:
            return response(404, '作品未找到！')
        return response(200, '获取成功！', Work.to_dict(work))
    except Exception as e:
        app.logger.error(f"获取作品详情失败: {e}")
        return response(500, '获取作品详情失败！')


# 创建作品接口
@work_bp.route('/create', methods=['POST'])
@token_required
def create_work(current_user):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        work_name = request.form.get('workName')
        work_description = request.form.get('workDescription')
        template_id = request.form.get('templateId')
        html_content = request.form.get('htmlContent')
        css_content = request.form.get('cssContent')
        js_content = request.form.get('jsContent')
        other_files = request.files.getlist('otherFiles')

        if not work_name or not work_description:
            return response(400, '创建作品失败，不能为空！')

        user_id = current_user.user_id
        u_id = current_user.u_id

        if template_id:
            work = work_model.create_work_from_template(u_id, user_id, template_id, work_name, work_description)
        else:
            work = work_model.create_work(u_id, user_id, work_name, work_description)
            # 创建主文件
            main_file = work_model.update_main_file(user_id, work.w_id, html_content, css_content, js_content)
            if not main_file:
                work_model.delete_work(u_id, user_id, work.w_id)
                return response(500, '创建作品失败！')

        if not work:
            return response(500, '创建作品失败！')

        # 更新其他文件
        if other_files:
            other_files = work_model.update_other_files(user_id, work.w_id, other_files)
            if not other_files:
                work_model.delete_work(current_user.u_id, work.w_id)
                return response(500, '创建作品失败！')

        return response(201, '创建成功！', Work.to_dict(work))

    except Exception as e:
        app.logger.error(f"创建作品失败: {e}")
        work_model.delete_work(current_user.u_id, work.w_id)
        return response(500, '创建作品失败！')


# 编辑作品接口
@work_bp.route('/set', methods=['POST'])
@token_required
def update_work(current_user):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        w_id = request.form.get('w_id')
        work_name = request.form.get('workName')
        work_description = request.form.get('workDescription')
        html_content = request.form.get('htmlContent')
        css_content = request.form.get('cssContent')
        js_content = request.form.get('jsContent')
        other_files = request.files.getlist('otherFiles')

        if not w_id or not work_name or not work_description:
            return response(400, '修改作品失败，不能为空！')

        user_id = current_user.user_id
        u_id = current_user.u_id

        work = work_model.get_work_by_id(u_id, w_id)
        if not work:
            return response(404, '作品未找到！')

        work = work_model.update_work(u_id, w_id, work_name, work_description)
        if not work:
            return response(501, '修改作品失败！')

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

        return response(200, '修改成功！')
    except Exception as e:
        app.logger.error(f"修改作品失败: {e}")
        return response(500, '修改作品失败！')


# 删除作品接口
@work_bp.route('/del', methods=['POST'])
@token_required
def delete_work(current_user):
    try:
        mysql_client = get_mysql_client()
        work_model = WorkModel(mysql_client, redis_client, app)
        data = request.get_json()
        w_id = data.get('w_id')
        u_id = current_user.u_id
        user_id = current_user.user_id

        if not w_id:
            return response(400, '作品ID不能为空！')

        work = work_model.get_work_by_id(u_id, w_id)
        if not work:
            return response(404, '作品未找到！')

        work_model.delete_work(u_id, user_id, w_id)
        return response(200, '作品删除成功！')
    except Exception as e:
        app.logger.error(f"删除作品失败: {e}")
        return response(500, '删除作品失败！')
