"""报价 API 服务层 - 统一处理报价请求"""
from services.quote_service import process_quote as _process

def submit_quote(text: str) -> dict:
    """提交报价文本，返回标准响应。"""
    if not text or not text.strip():
        return {"success": False, "message": "请输入报价需求", "data": None, "file_url": ""}

    result = _process(text)

    return {
        "success": result.get("success", False),
        "message": result.get("message", ""),
        "data": result.get("data"),
        "file_url": result.get("url", "")
    }