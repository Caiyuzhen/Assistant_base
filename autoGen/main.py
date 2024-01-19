# 核心步骤:
# 1. 创建 Assistant 对象
# 2. 创建 Thread 对象 => Assistant 跟 user 对话消息的库
# 3. Message => 消息
# 4. Run 给 Assistant 配置一些工具
# 5. Run Step 运行, 执行步骤

# from langchain_openai import OpenAI

# assistant = client.beta.assistants.create(
# 	name="数据分析师·助手",
#  	description="你是一个数据分析师，你的工作是帮助公司分析数据",
# 	model="gpt-4-1106-preview",
# 	tools=[{"type:" "code_interpreter"}]
# 	file_ids=[file.id]
# )


# thread = client.beta.threads.create(
# 	message=[
# 		{
# 			"role": "user",
# 			"content": "根据 file 创建一份分析报告"
#    			"file_ids": [file.id]
# 		}
# 	]
# )