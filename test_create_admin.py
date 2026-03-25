"""
通过API创建管理员账号
"""

import requests
import json

# API地址
BASE_URL = "http://localhost:8000"

def create_admin_via_api():
    """通过注册API创建管理员"""
    
    # 管理员信息
    admin_data = {
        "username": "admin",
        "email": "admin@medical-qa.com",
        "password": "854468573Ta",
        "user_type": "admin"
    }
    
    print("=" * 50)
    print("通过API创建管理员账号")
    print("=" * 50)
    print(f"API地址: {BASE_URL}")
    print(f"用户名: {admin_data['username']}")
    print(f"邮箱: {admin_data['email']}")
    print(f"密码: {admin_data['password']}")
    print(f"类型: {admin_data['user_type']}")
    print()
    
    try:
        # 发送注册请求
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        print()
        
        if response.status_code == 201:
            print("✅ 管理员账号创建成功!")
            print()
            print("现在可以使用以下凭据登录:")
            print(f"   用户名: {admin_data['username']}")
            print(f"   密码: {admin_data['password']}")
        else:
            print("❌ 创建失败")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器")
        print("   请确保后端服务正在运行 (python -m uvicorn api.main:app)")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    
    print()
    print("=" * 50)

if __name__ == "__main__":
    create_admin_via_api()
