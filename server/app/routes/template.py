from flask import request, Blueprint
from app import app
from app.common import response, get_mysql_client, redis_client
from app.models.Template import Template, TemplateModel


template_bp = Blueprint('template', __name__)


# 获取模板列表接口
@template_bp.route('/list', methods=['GET'])
def get_templates():
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)
        t_id = request.args.get('t_id', type=int)
        t_name = request.args.get('t_name', type=str)
        t_description = request.args.get('t_description', type=str)

        mysql_client = get_mysql_client()
        template_model = TemplateModel(mysql_client, redis_client, app)
        templates, total = template_model.get_templates_paginated(
            page, size, t_id, t_name, t_description
        )
        data = {
            "list": [Template.to_dict(t) for t in templates],
            "total": total
        }
        return response(200, '获取成功！', data)
    except Exception as e:
        app.logger.error(f"获取模板列表失败: {e}")
        return response(500, '获取模板列表失败！')

# 获取模板详情接口
@template_bp.route('/detail/<int:t_id>', methods=['GET'])
def get_template_detail(t_id):
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

# 获取模板文件接口
@template_bp.route('/file/<int:t_id>/<path:filename>', methods=['GET'])
def get_template_file(t_id, filename):
    try:
        mysql_client = get_mysql_client()
        template_model = TemplateModel(mysql_client, redis_client, app)
        file_response = template_model.get_template_file(t_id, filename)
        if not file_response:
            return response(404, '模板文件未找到！')
        return file_response
    except Exception as e:
        app.logger.error(f"获取模板文件失败: {e}")
        return response(500, '获取模板文件失败！')
    
# 获取模板主文件接口
@template_bp.route('/files/main/<int:t_id>', methods=['GET'])
def get_template_main_file(t_id):
    try:
        mysql_client = get_mysql_client()
        template_model = TemplateModel(mysql_client, redis_client, app)
        html_file, css_file, js_file, screenshot_file = template_model.get_main_file(t_id)
        return response(200, '获取成功！', {'html': html_file, 'css': css_file, 'javascript': js_file, 'screenshot': screenshot_file})
    except Exception as e:
        app.logger.error(f"获取模板主文件失败: {e}")
        return response(500, '获取模板主文件失败！')