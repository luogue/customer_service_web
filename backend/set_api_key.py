"""
设置API Key脚本
"""
import argparse
from knowledge_base.api_key_manager import set_api_key, get_api_key, list_api_keys


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="设置API Key")
    parser.add_argument("--action", type=str, choices=["set", "get", "list"], required=True, help="操作类型")
    parser.add_argument("--name", type=str, help="API Key名称")
    parser.add_argument("--key", type=str, help="API Key值")
    
    args = parser.parse_args()
    
    if args.action == "set":
        if not args.name or not args.key:
            print("错误：设置API Key时需要指定name和key参数")
            return
        
        success = set_api_key(args.name, args.key)
        if success:
            print(f"API Key '{args.name}' 设置成功")
        else:
            print(f"API Key '{args.name}' 设置失败")
    
    elif args.action == "get":
        if not args.name:
            print("错误：获取API Key时需要指定name参数")
            return
        
        api_key = get_api_key(args.name)
        if api_key:
            print(f"API Key '{args.name}': {api_key}")
        else:
            print(f"API Key '{args.name}' 不存在")
    
    elif args.action == "list":
        api_keys = list_api_keys()
        if api_keys:
            print("所有API Key:")
            for key in api_keys:
                print(f"- {key['key_name']} (创建时间: {key['created_at']}, 更新时间: {key['updated_at']})")
        else:
            print("没有API Key")


if __name__ == "__main__":
    main()