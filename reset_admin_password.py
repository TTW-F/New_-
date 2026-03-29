"""
重置管理员密码脚本
"""

from sqlalchemy.orm import Session
from api.core.database import SessionLocal
from api.services.user_service import UserService
from api.models.user import User

def reset_admin_password():
    """重置管理员密码"""
    db: Session = SessionLocal()
    
    try:
        user_service = UserService(db)
        
        # 查找管理员账号
        admin = db.query(User).filter(User.username == "admin").first()
        
        if not admin:
            print("❌ 未找到管理员账号")
            return
        
        print(f"找到管理员账号:")
        print(f"  用户名: {admin.username}")
        print(f"  邮箱: {admin.email}")
        print(f"  当前密码哈希: {admin.password_hash[:50]}...")
        print()
        
        # 新密码
        new_password = "854468573Ta"
        
        # 生成新的密码哈希
        new_hash = user_service.hash_password(new_password)
        print(f"新密码哈希: {new_hash[:50]}...")
        print()
        
        # 更新密码
        admin.password_hash = new_hash
        db.commit()
        
        print("✅ 密码已重置!")
        print(f"   用户名: admin")
        print(f"   密码: {new_password}")
        print()
        
        # 验证新密码
        print("验证新密码...")
        is_valid = user_service.verify_password(new_password, admin.password_hash)
        if is_valid:
            print("✅ 密码验证成功!")
        else:
            print("❌ 密码验证失败!")
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
