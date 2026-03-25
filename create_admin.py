"""
创建管理员账号脚本
"""

import sys
from sqlalchemy.orm import Session
from api.core.database import SessionLocal
from api.services.user_service import UserService

def create_admin():
    """创建管理员账号"""
    db: Session = SessionLocal()
    
    try:
        user_service = UserService(db)
        
        # 管理员信息
        username = "admin"
        email = "admin@medical-qa.com"
        password = "854468573Ta"
        user_type = "admin"
        
        print(f"正在创建管理员账号...")
        print(f"用户名: {username}")
        print(f"邮箱: {email}")
        print(f"密码: {password}")
        print(f"类型: {user_type}")
        print()
        
        # 检查是否已存在
        existing_user = user_service.get_user_by_username(username)
        if existing_user:
            print(f"❌ 用户名 '{username}' 已存在")
            print(f"   用户ID: {existing_user.id}")
            print(f"   邮箱: {existing_user.email}")
            print(f"   类型: {existing_user.user_type.value}")
            print()
            
            # 询问是否更新密码
            response = input("是否更新该用户的密码? (y/n): ")
            if response.lower() == 'y':
                success = user_service.change_password(existing_user, password)
                if success:
                    print("✅ 密码已更新")
                else:
                    print("❌ 密码更新失败")
            return
        
        # 创建新用户
        user, error = user_service.register(
            username=username,
            email=email,
            password=password,
            user_type=user_type
        )
        
        if user:
            print("✅ 管理员账号创建成功!")
            print(f"   用户ID: {user.id}")
            print(f"   用户名: {user.username}")
            print(f"   邮箱: {user.email}")
            print(f"   类型: {user.user_type.value}")
            print(f"   状态: {'激活' if user.is_active else '禁用'}")
            print()
            print("现在可以使用以下凭据登录:")
            print(f"   用户名: {username}")
            print(f"   密码: {password}")
        else:
            print(f"❌ 创建失败: {error}")
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
