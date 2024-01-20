import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 获取 API 密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 实例化 OpenAI 客户端
client = OpenAI(api_key=OPENAI_API_KEY)

# 上传文件（记忆）
file = client.files.create(
	file=open("Prompt Format.md", "rb"),
	purpose='assistants'
)

# 1.创建 Assistant
assistant = client.beta.assistants.create(
	name="提示词助手",
	instructions="你是一位图片创作的提示词高手,你可以写出非常合理的结构化的提示词",
	model="gpt-4-1106-preview",
	tools=[
		{"type": "retrieval"},
		{"type": "code_interpreter"},
	],
	file_ids=[file.id]
)

# 2.创建 Thread
thread = client.beta.threads.create()

# 3.创建 Message
message = client.beta.threads.messages.create(
	thread_id=thread.id,
	role="user",
	content="给我一段关于龙的提示词",
	file_ids=[file.id]
)

# 4.创建 Run
run = client.beta.threads.runs.create(
	thread_id=thread.id,
	assistant_id=assistant.id,
)

# 5.执行 Run
while True:
    run = client.beta.threads.runs.retrieve(
		thread_id=thread.id,
		run_id=run.id
	)
    if run.status not in ["queue", "in_progress"]:
        break
    time.sleep(1)
    
# 6.取出 Message
messages = client.beta.threads.message.list(
	thread_id=thread.id
)

message = messages.data[0].content.text.value