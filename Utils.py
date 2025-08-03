import os
import configparser
import re

def get_pure_slack_message(text):
    # Remove everything between < and > (non-greedy)
    text = re.sub(r'<[^>]*>', '', text)
    return text


def set_env_from_ini(ini_path):
    # Create a config parser
    config = configparser.ConfigParser()
    
    # Read the INI file
    config.read(ini_path)
    
    # Iterate over sections and keys
    for section in config.sections():
        for key, value in config.items(section):
            # Set as environment variable
            os.environ[key.upper()] = value
            print(f"Set {key.upper()} = {value}")

def markdown_to_slack_mrkdwn(markdown_text):
    """
    将标准Markdown转换为Slack mrkdwn格式
    """
    slack_text = markdown_text
    
    # 1.1 处理粗体：**text** 或 __text__ -> *text* (临时换成@text@格式)
    slack_text = re.sub(r'\*\*(.*?)\*\*', r'@\1@', slack_text)
    slack_text = re.sub(r'__(.*?)__', r'@\1@', slack_text)
    
    # 2. 处理斜体：*text* -> _text_ (需要小心不与粗体冲突)
    # 先处理没有被转换的单个*
    slack_text = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)', r'_\1_', slack_text)
    # 1.2 处理完斜体之后再进行粗体的最终处理
    slack_text = re.sub(r'@(.*?)@', r'*\1*', slack_text)

    # 3. 处理删除线：~~text~~ -> ~text~
    slack_text = re.sub(r'~~(.*?)~~', r'~\1~', slack_text)
    
    # 4. 处理链接：[text](url) -> <url|text>
    slack_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<\2|\1>', slack_text)
    
    # 5. 处理行内代码（保持不变）：`code` -> `code`
    # 已经是正确格式，无需处理
    
    # 6. 处理代码块（保持不变）：```code``` -> ```code```
    # 已经是正确格式，无需处理
    
    # 7. 处理标题：# Title -> *Title*
    slack_text = re.sub(r'^#+\s*(.*?)$', r'*\1*', slack_text, flags=re.MULTILINE)
    
    # 8. 处理引用：> text -> > text (保持不变)
    # 已经是正确格式，无需处理
    
    # 9. 处理列表：- item 或 * item -> • item
    slack_text = re.sub(r'^[\s]*[-*+]\s+', '• ', slack_text, flags=re.MULTILINE)
    
    # 10. 处理数字列表：1. item -> 1. item (保持不变，但可以改为•)
    # slack_text = re.sub(r'^\s*\d+\.\s+', '• ', slack_text, flags=re.MULTILINE)
    
    return slack_text