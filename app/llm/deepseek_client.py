import json
import logging
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.DEEPSEEK_BASE_URL,
    timeout=settings.AI_QUESTION_TIMEOUT,
)

@retry(
    stop=stop_after_attempt(settings.AI_QUESTION_MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((Exception,)),
    reraise=True,
)
async def _call_deepseek(messages: list, temperature: float = 0.8) -> str:
    response = await client.chat.completions.create(
        model=settings.DEEPSEEK_MODEL,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content.strip()

async def generate_questions(
    topic: str,
    question_type: str,
    difficulty: int,
    count: int = 1,
    extra_requirements: str = ""
) -> List[Dict[str, Any]]:
    type_desc = {
        "single_choice": "单选题，4个选项，只有一个正确",
        "multiple_choice": "多选题，4个选项，至少一个正确",
        "true_false": "判断题，两个选项：正确、错误",
        "essay": "简答题，无选项，答案为一段文字"
    }
    type_info = type_desc.get(question_type, question_type)

    system_prompt = (
        "你是一个专业的考试命题专家。请根据用户要求生成题目，严格以 JSON 格式返回。"
        "返回格式必须为：\n"
        '{"questions": [{"content": "题目内容", "type": "single_choice", "options": ["A.选项", "B.选项", ...], "answer": "正确答案", "analysis": "简短解析"}]}\n'
        "options 字段对于单选题和多选题必须是一个包含选项列表的数组；判断题 options 为 [\"正确\", \"错误\"]；简答题 options 为空数组 []。"
        "answer 字段对于选择题填写选项字母（如 'A'），判断题填写 '正确' 或 '错误'，简答题填写参考答案文字。"
        "务必只返回 JSON，不要包含任何额外文字。"
    )

    user_prompt = (
        f"知识点：{topic}\n"
        f"题型：{question_type}（{type_info}）\n"
        f"难度：{difficulty}（1简单 - 5困难）\n"
        f"数量：{count} 道\n"
        f"{extra_requirements}\n"
        "请按要求的 JSON 格式输出。"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    content = await _call_deepseek(messages)
    data = json.loads(content)
    questions = data.get("questions", [])

    validated = []
    for q in questions:
        if not all(k in q for k in ("content", "type", "answer")):
            continue
        q.setdefault("options", [])
        q.setdefault("analysis", "")
        validated.append(q)
    return validated