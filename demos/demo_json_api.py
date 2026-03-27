"""
MicroFlask JSON API演示
演示各种JSON数据处理和API设计
"""
import sys
import os
import json
import time
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from microflask import Flask, Response

# 创建Flask应用实例
app = Flask(__name__)

# 模拟数据库
users_db = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 25},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 30},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com", "age": 35}
]

posts_db = [
    {"id": 1, "title": "First Post", "content": "This is the first post", "author_id": 1, "created_at": "2025-01-01"},
    {"id": 2, "title": "Second Post", "content": "This is the second post", "author_id": 2, "created_at": "2025-01-02"},
    {"id": 3, "title": "Third Post", "content": "This is the third post", "author_id": 1, "created_at": "2025-01-03"}
]

# 1. 基础JSON响应
@app.route("/api/hello")
def api_hello(req):
    """基础JSON API响应"""
    return {
        "message": "Hello from MicroFlask JSON API!",
        "status": "success",
        "timestamp": time.time()
    }

# 2. 获取所有用户
@app.route("/api/users", methods=["GET"])
def get_users(req):
    """获取所有用户列表"""
    return {
        "status": "success",
        "data": users_db,
        "count": len(users_db)
    }

# 3. 获取单个用户
@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(req):
    """获取指定用户"""
    user_id = req.view_args.get("user_id")
    user = next((u for u in users_db if u["id"] == user_id), None)
    
    if user:
        return {
            "status": "success",
            "data": user
        }
    else:
        return {
            "status": "error",
            "message": f"User with ID {user_id} not found"
        }, 404

# 4. 创建新用户
@app.route("/api/users", methods=["POST"])
def create_user(req):
    """创建新用户"""
    try:
        # 获取JSON数据
        user_data = req.json
        if not user_data:
            return {
                "status": "error",
                "message": "Invalid JSON data"
            }, 400
        
        # 验证必需字段
        required_fields = ["name", "email"]
        for field in required_fields:
            if field not in user_data:
                return {
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }, 400
        
        # 创建新用户
        new_user = {
            "id": max(u["id"] for u in users_db) + 1,
            "name": user_data["name"],
            "email": user_data["email"],
            "age": user_data.get("age", None)
        }
        
        users_db.append(new_user)
        
        return {
            "status": "success",
            "message": "User created successfully",
            "data": new_user
        }, 201
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating user: {str(e)}"
        }, 500

# 5. 更新用户
@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(req):
    """更新用户信息"""
    user_id = req.view_args.get("user_id")
    user = next((u for u in users_db if u["id"] == user_id), None)
    
    if not user:
        return {
            "status": "error",
            "message": f"User with ID {user_id} not found"
        }, 404
    
    try:
        update_data = req.json
        if not update_data:
            return {
                "status": "error",
                "message": "Invalid JSON data"
            }, 400
        
        # 更新字段
        for key, value in update_data.items():
            if key in ["name", "email", "age"]:
                user[key] = value
        
        return {
            "status": "success",
            "message": "User updated successfully",
            "data": user
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error updating user: {str(e)}"
        }, 500

# 6. 删除用户
@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(req):
    """删除用户"""
    user_id = req.view_args.get("user_id")
    user_index = next((i for i, u in enumerate(users_db) if u["id"] == user_id), None)
    
    if user_index is not None:
        deleted_user = users_db.pop(user_index)
        return {
            "status": "success",
            "message": "User deleted successfully",
            "data": deleted_user
        }
    else:
        return {
            "status": "error",
            "message": f"User with ID {user_id} not found"
        }, 404

# 7. 获取用户帖子
@app.route("/api/users/<int:user_id>/posts", methods=["GET"])
def get_user_posts(req):
    """获取指定用户的所有帖子"""
    user_id = req.view_args.get("user_id")
    user = next((u for u in users_db if u["id"] == user_id), None)
    
    if not user:
        return {
            "status": "error",
            "message": f"User with ID {user_id} not found"
        }, 404
    
    user_posts = [p for p in posts_db if p["author_id"] == user_id]
    
    return {
        "status": "success",
        "data": {
            "user": user,
            "posts": user_posts,
            "post_count": len(user_posts)
        }
    }

# 8. 查询参数演示
@app.route("/api/search", methods=["GET"])
def search_api(req):
    """演示查询参数处理"""
    query = req.args.get("q", "")
    limit = int(req.args.get("limit", 10))
    offset = int(req.args.get("offset", 0))
    
    # 搜索用户
    results = []
    if query:
        results = [u for u in users_db if query.lower() in u["name"].lower() or query.lower() in u["email"].lower()]
    else:
        results = users_db
    
    # 分页
    total = len(results)
    results = results[offset:offset + limit]
    
    return {
        "status": "success",
        "query": query,
        "limit": limit,
        "offset": offset,
        "total": total,
        "data": results
    }

# 9. 表单数据处理
@app.route("/api/form", methods=["POST"])
def handle_form(req):
    """演示表单数据处理"""
    name = req.form.get("name", "")
    email = req.form.get("email", "")
    message = req.form.get("message", "")
    
    if not name or not email:
        return {
            "status": "error",
            "message": "Name and email are required"
        }, 400
    
    return {
        "status": "success",
        "message": "Form data received",
        "data": {
            "name": name,
            "email": email,
            "message": message
        }
    }

# 10. 文件上传模拟（通过JSON）
@app.route("/api/upload", methods=["POST"])
def simulate_upload(req):
    """模拟文件上传（通过JSON数据）"""
    try:
        upload_data = req.json
        if not upload_data:
            return {
                "status": "error",
                "message": "No upload data provided"
            }, 400
        
        filename = upload_data.get("filename", "")
        content = upload_data.get("content", "")
        content_type = upload_data.get("content_type", "text/plain")
        
        if not filename or not content:
            return {
                "status": "error",
                "message": "Filename and content are required"
            }, 400
        
        # 模拟保存文件
        file_info = {
            "filename": filename,
            "size": len(content),
            "content_type": content_type,
            "uploaded_at": time.ctime(time.time())
        }
        
        return {
            "status": "success",
            "message": "File uploaded successfully",
            "data": file_info
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Upload failed: {str(e)}"
        }, 500

# 11. 分页API演示
@app.route("/api/posts", methods=["GET"])
def get_posts(req):
    """分页获取帖子列表"""
    page = int(req.args.get("page", 1))
    per_page = int(req.args.get("per_page", 2))
    
    # 计算偏移量
    offset = (page - 1) * per_page
    
    # 分页数据
    paginated_posts = posts_db[offset:offset + per_page]
    
    # 构建分页信息
    total_posts = len(posts_db)
    total_pages = (total_posts + per_page - 1) // per_page
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "status": "success",
        "data": paginated_posts,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total_posts,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "next_page": page + 1 if has_next else None,
            "prev_page": page - 1 if has_prev else None
        }
    }

# 12. 批量操作API
@app.route("/api/users/batch", methods=["POST"])
def batch_operations(req):
    """批量操作用户"""
    try:
        operations = req.json
        if not operations or "operations" not in operations:
            return {
                "status": "error",
                "message": "Invalid batch request"
            }, 400
        
        results = []
        
        for op in operations["operations"]:
            op_type = op.get("type")
            user_id = op.get("user_id")
            
            if op_type == "delete":
                user_index = next((i for i, u in enumerate(users_db) if u["id"] == user_id), None)
                if user_index is not None:
                    deleted_user = users_db.pop(user_index)
                    results.append({"type": "delete", "status": "success", "data": deleted_user})
                else:
                    results.append({"type": "delete", "status": "error", "message": f"User {user_id} not found"})
            
            elif op_type == "get":
                user = next((u for u in users_db if u["id"] == user_id), None)
                if user:
                    results.append({"type": "get", "status": "success", "data": user})
                else:
                    results.append({"type": "get", "status": "error", "message": f"User {user_id} not found"})
        
        return {
            "status": "success",
            "message": "Batch operations completed",
            "results": results
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Batch operation failed: {str(e)}"
        }, 500

# 13. API状态检查
@app.route("/api/status", methods=["GET"])
def api_status(req):
    """API状态检查"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "endpoints": [
            "/api/hello",
            "/api/users",
            "/api/users/<id>",
            "/api/posts",
            "/api/search",
            "/api/form",
            "/api/upload",
            "/api/users/batch"
        ],
        "statistics": {
            "total_users": len(users_db),
            "total_posts": len(posts_db)
        }
    }

# 14. 错误处理演示
@app.route("/api/error", methods=["GET"])
def trigger_error(req):
    """触发不同类型的错误"""
    error_type = req.args.get("type", "generic")
    
    if error_type == "400":
        return {"status": "error", "message": "Bad Request"}, 400
    elif error_type == "401":
        return {"status": "error", "message": "Unauthorized"}, 401
    elif error_type == "403":
        return {"status": "error", "message": "Forbidden"}, 403
    elif error_type == "404":
        return {"status": "error", "message": "Not Found"}, 404
    elif error_type == "500":
        # 故意引发服务器错误
        raise Exception("Internal server error")
    else:
        return {"status": "error", "message": "Generic error"}, 400

# 15. CORS演示（简单实现）
@app.route("/api/cors", methods=["GET", "POST", "OPTIONS"])
def cors_demo(req):
    """CORS演示"""
    if req.method == "OPTIONS":
        resp = Response("", status=200)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return resp
    
    data = {
        "message": "CORS enabled endpoint",
        "method": req.method,
        "origin": req.headers.get("Origin", "unknown")
    }
    
    resp = Response(json.dumps(data), content_type="application/json")
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

if __name__ == "__main__":
    print("=== MicroFlask JSON API演示 ===")
    print("可用路由:")
    print("  GET    /api/hello              - 基础JSON响应")
    print("  GET    /api/users              - 获取所有用户")
    print("  GET    /api/users/<id>         - 获取指定用户")
    print("  POST   /api/users              - 创建新用户")
    print("  PUT    /api/users/<id>         - 更新用户")
    print("  DELETE /api/users/<id>         - 删除用户")
    print("  GET    /api/users/<id>/posts   - 获取用户帖子")
    print("  GET    /api/search?q=alice     - 搜索用户")
    print("  POST   /api/form               - 处理表单数据")
    print("  POST   /api/upload             - 模拟文件上传")
    print("  GET    /api/posts?page=1       - 分页获取帖子")
    print("  POST   /api/users/batch        - 批量操作")
    print("  GET    /api/status             - API状态检查")
    print("  GET    /api/error?type=400     - 错误处理演示")
    print("  ANY    /api/cors               - CORS演示")
    print()
    print("测试示例:")
    print("  curl -X GET http://localhost:8083/api/users")
    print("  curl -X POST -H 'Content-Type: application/json' -d '{\"name\":\"Test\",\"email\":\"test@example.com\"}' http://localhost:8083/api/users")
    print()
    app.run(host="0.0.0.0", port=8083, debug=True)