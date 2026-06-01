"""
敏感词过滤模块
用于检查用户提问和知识库内容是否包含违规敏感词
"""
import re
import os
import time
from typing import List, Tuple, Dict, Optional

class SensitiveFilter:
    """敏感词过滤器"""
    
    def __init__(self):
        # 从文件加载敏感词
        self.sensitive_words = self._load_sensitive_words()
        # 从文件加载业务违禁词
        self.business_forbidden_words = self._load_business_forbidden_words()
        
        # 构建敏感词正则表达式
        self.sensitive_patterns = {}
        for category, words in self.sensitive_words.items():
            if words:
                pattern = '|'.join(re.escape(word) for word in words)
                self.sensitive_patterns[category] = re.compile(pattern, re.IGNORECASE)
        
        # 构建业务违禁词正则表达式
        if self.business_forbidden_words:
            business_pattern = '|'.join(re.escape(word) for word in self.business_forbidden_words)
            self.business_pattern = re.compile(business_pattern, re.IGNORECASE)
        else:
            self.business_pattern = None
        
        # 兜底回答
        self.fallback_responses = {
            "default": "很抱歉，我无法回答这个问题。",
            "sensitive": "很抱歉，您的问题涉及敏感内容，我无法回答。",
            "business": "很抱歉，您的问题涉及业务违禁内容，我无法回答。"
        }
        
        # 过滤开关控制
        self.filter_enabled = True
    
    def _load_sensitive_words(self):
        """
        从文件加载敏感词
        
        Returns:
            Dict[str, List[str]]: 敏感词字典
        """
        sensitive_words = {
            "政治": [],
            "色情": [],
            "暴力": [],
            "赌博": [],
            "毒品": [],
            "违法": []
        }
        
        try:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建敏感词文件路径
            file_path = os.path.join(current_dir, "tencent-sensitive-words.txt")
            with open(file_path, "r", encoding="utf-8") as f:
                current_category = None
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释
                    if not line or line.startswith("#"):
                        # 检查是否是类别注释
                        if line.startswith("# "):
                            category_name = line[2:].strip()
                            # 映射类别名称
                            category_map = {
                                "政治敏感": "政治",
                                "色情": "色情",
                                "暴力": "暴力",
                                "赌博": "赌博",
                                "毒品": "毒品",
                                "违法": "违法"
                            }
                            if category_name in category_map:
                                current_category = category_map[category_name]
                        continue
                    
                    # 添加敏感词到当前类别
                    if current_category and current_category in sensitive_words:
                        sensitive_words[current_category].append(line)
        except Exception as e:
            # 如果文件加载失败，使用默认敏感词
            print(f"加载敏感词文件失败: {e}")
            # 默认敏感词
            sensitive_words = {
                "政治": ["颠覆", "推翻", "造反", "反动", "恐怖", "极端"],
                "色情": ["色情", "黄色", "淫秽", "成人", "情色"],
                "暴力": ["暴力", "血腥", "杀人", "自杀", "斗殴"],
                "赌博": ["赌博", "赌场", "博彩", "下注", "赔率"],
                "毒品": ["毒品", "大麻", "海洛因", "冰毒", "摇头丸"],
                "违法": ["诈骗", "盗窃", "抢劫", "绑架", "勒索"]
            }
        
        return sensitive_words
    
    def _load_business_forbidden_words(self):
        """
        从文件加载业务违禁词
        
        Returns:
            List[str]: 业务违禁词列表
        """
        forbidden_words = []
        
        try:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建业务违禁词文件路径
            file_path = os.path.join(current_dir, "business_forbidden_words.txt")
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释
                    if not line or line.startswith("#"):
                        continue
                    forbidden_words.append(line)
        except Exception as e:
            # 如果文件加载失败，使用默认业务违禁词
            print(f"加载业务违禁词文件失败: {e}")
            forbidden_words = [
                "诈骗", "欺诈", "骗钱", "钓鱼", "刷单",
                "推广", "广告", "营销", "推销", "兼职", "代理",
                "身份证", "银行卡", "密码", "手机号", "验证码",
                "洗钱", "走私", "假货", "盗版"
            ]
        
        return forbidden_words
    
    def check_sensitive_content(self, content: str) -> Tuple[bool, List[str], List[str]]:
        """
        检查内容是否包含敏感词
        
        Args:
            content: 要检查的内容
            
        Returns:
            Tuple[bool, List[str], List[str]]: (是否包含敏感词, 敏感词列表, 敏感词类别列表)
        """
        if not content:
            return False, [], []
        
        detected_words = []
        detected_categories = []
        
        for category, pattern in self.sensitive_patterns.items():
            matches = pattern.findall(content)
            if matches:
                detected_words.extend(matches)
                detected_categories.append(category)
        
        return len(detected_words) > 0, list(set(detected_words)), list(set(detected_categories))
    
    def check_business_forbidden(self, content: str) -> Tuple[bool, List[str]]:
        """
        检查内容是否包含业务违禁词
        
        Args:
            content: 要检查的内容
            
        Returns:
            Tuple[bool, List[str]]: (是否包含业务违禁词, 违禁词列表)
        """
        if not content or not self.business_pattern:
            return False, []
        
        matches = self.business_pattern.findall(content)
        return len(matches) > 0, list(set(matches))
    
    def filter_sensitive_content(self, content: str) -> str:
        """
        过滤内容中的敏感词，用*替换
        
        Args:
            content: 要过滤的内容
            
        Returns:
            str: 过滤后的内容
        """
        if not content:
            return content
        
        filtered_content = content
        
        for category, pattern in self.sensitive_patterns.items():
            def replace_func(match):
                word = match.group(0)
                return '*' * len(word)
            filtered_content = pattern.sub(replace_func, filtered_content)
        
        return filtered_content
    
    def filter_business_forbidden(self, content: str) -> str:
        """
        过滤内容中的业务违禁词，用*替换
        
        Args:
            content: 要过滤的内容
            
        Returns:
            str: 过滤后的内容
        """
        if not content or not self.business_pattern:
            return content
        
        def replace_func(match):
            word = match.group(0)
            return '*' * len(word)
        
        return self.business_pattern.sub(replace_func, content)
    
    def filter_content(self, text: str, filter_dimensions: List[str]) -> Dict:
        """
        过滤函数 - 接收两个参数：大模型生成的原始文本、规则库过滤维度
        
        Args:
            text: 大模型生成的原始文本
            filter_dimensions: 规则库过滤维度列表，支持["敏感词", "业务违禁词", "格式校验"]
            
        Returns:
            Dict: 包含过滤结果的字典
                {
                    "original_text": str,  # 原始文本
                    "filtered_text": str,  # 过滤后的文本
                    "has_violation": bool,  # 是否有违规
                    "violation_words": List[str],  # 违规词列表
                    "violation_categories": List[str],  # 违规类别列表
                    "fallback_response": Optional[str],  # 兜底回答
                    "processing_time": float,  # 处理时间
                    "filter_enabled": bool  # 过滤是否启用
                }
        """
        start_time = time.time()
        
        result = {
            "original_text": text,
            "filtered_text": text,
            "has_violation": False,
            "violation_words": [],
            "violation_categories": [],
            "fallback_response": None,
            "processing_time": 0,
            "filter_enabled": self.filter_enabled
        }
        
        # 如果过滤未启用，直接返回
        if not self.filter_enabled:
            result["processing_time"] = time.time() - start_time
            return result
        
        # 检查敏感词
        if "敏感词" in filter_dimensions:
            has_sensitive, sensitive_words, categories = self.check_sensitive_content(text)
            if has_sensitive:
                result["has_violation"] = True
                result["violation_words"].extend(sensitive_words)
                result["violation_categories"].extend(categories)
                # 应用敏感词过滤
                result["filtered_text"] = self.filter_sensitive_content(result["filtered_text"])
        
        # 检查业务违禁词
        if "业务违禁词" in filter_dimensions:
            has_forbidden, forbidden_words = self.check_business_forbidden(text)
            if has_forbidden:
                result["has_violation"] = True
                result["violation_words"].extend(forbidden_words)
                result["violation_categories"].append("业务违禁")
                # 应用业务违禁词过滤
                result["filtered_text"] = self.filter_business_forbidden(result["filtered_text"])
        
        # 检查格式校验（这里简单实现，实际可根据具体需求扩展）
        if "格式校验" in filter_dimensions:
            # 检查是否包含过多特殊字符
            special_chars = re.findall(r'[^\w\s\u4e00-\u9fa5]', text)
            if len(special_chars) > len(text) * 0.3:
                result["has_violation"] = True
                result["violation_categories"].append("格式违规")
        
        # 检查是否全量违规
        if result["has_violation"]:
            # 计算违规词占比
            violation_ratio = len(''.join(result["violation_words"])) / len(text) if text else 0
            if violation_ratio > 0.5:
                # 全量违规，使用兜底回答
                if "敏感词" in result["violation_categories"]:
                    result["fallback_response"] = self.fallback_responses["sensitive"]
                elif "业务违禁" in result["violation_categories"]:
                    result["fallback_response"] = self.fallback_responses["business"]
                else:
                    result["fallback_response"] = self.fallback_responses["default"]
                result["filtered_text"] = result["fallback_response"]
        
        result["processing_time"] = time.time() - start_time
        return result
    
    def set_filter_enabled(self, enabled: bool):
        """
        设置过滤开关
        
        Args:
            enabled: 是否启用过滤
        """
        self.filter_enabled = enabled

# 全局敏感词过滤器实例
sensitive_filter = SensitiveFilter()
