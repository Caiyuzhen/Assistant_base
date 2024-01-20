# 封装一层 assistant api 的工具函数
import os
import re
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv() 

# 获取环境变量的 API_KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 

# 初始化 OpenAI
client = OpenAI(api_key=OPENAI_API_KEY, timeout=600) 


# 【🔧 工具一: 创建或加载 Assistant 的方法】 (也要消费 token), 👇下面的参数都是有默认值的
def create_assistant(name="Assistant", instructions="You are a helpful assistant.", model="gpt-4-1106-preview",tools=None,files=None,debug=False):
	"""
	Creates an assistant with the given name, instructions, model, tools, and files.

	Args:
		name (str, optional): The name of the assistant. Defaults to "Assistant".
		instructions (str, optional): The instructions for the assistant. Defaults to "You are a helpful assistant.".
		model (str, optional): The model to use for the assistant. Defaults to "gpt-4-1106-preview".
		tools (list, optional): The list of tools to provide to the assistant. Defaults to None.
		files (list or str, optional): The list of files or a single file to upload and associate with the assistant. Defaults to None.

	Returns:
		str: The ID of the created assistant.
	"""
	# 1. 检测 assistant 是否存在
	# 每次创建 assistant 后, 我们就把 assistant 的 name 跟 assistant 的 id 保存为 assistant.json
	# 获取项目根目录的路径 (下一步才能找到 assistant.json 文件)
	root_dir = os.path.dirname(os.path.dirname(__file__))
    
	# 构建 city.json 的完整路径
	assistant_file_path = os.path.join(root_dir, 'data', 'assistant.json') # 🔥 assistant.json 的路径
	assistant_json = [] # 用于存放 assistant 的 json 数据
	
	# 如果存在同名的 assistant, 就直接返回 assistant id, 后续同名的 assistant 就可以直接调，不用重复创建
	if os.path.exists(assistant_file_path):
		with open(assistant_file_path, "r") as file:
			assistant_json = json.load(file) # 读取 assistant.json
			for assistant_data in assistant_json:
				assistant_name = assistant_data["assistant_name"]
				if assistant_name == name: # 如果已经存在同名的 assistant, 就直接返回 assistant id
					assistant_id = assistant_data["assistant_id"]
					print("已存在同名的 assistant_name, 直接返回 assistant_id")
					if debug:
						print("assistant_id: ", assistant_id)
					return assistant_id
	
	# 2.上传文件并获取 file_ids, 用于给 assistant 提供文件的上下文（记忆）
	file_ids = []
	if files:
		if isinstance(files, list): # 如果存在实例
			for file in files:
				file = client.files.create(
					file=open(file, "rb"),
					purpose="assistants"
           		)
		elif isinstance(files, str):
			file = client.files.create(
				file=open(file, "rb"),
				purpose="assistants"
			)
			file_ids.append(file.id)
   
	# 3.创建 assistant
	assistant = client.beta.assistants.create(
		name=name,
		instructions=instructions,
		model=model,
		tools=tools,
		file_ids=file_ids
	)
 
	assistant_id = assistant.id # 获取 assistant_id
	assistant_name = assistant.name # 获取 assistant_name
 
	# 4.保存 assistant 信息到 assistant.json
	assistant_json.append({ # 构造 json
		"assistant_name": assistant_name,
		"assistant_id": assistant_id
	})
	with open(assistant_file_path, "w", encoding="utf-8") as file:
		json.dump(assistant_json, file, ensure_ascii=False, indent=4) # dump 表示写入,  , 传入 json 数据、文件对象、ensure_ascii=False(保证中文不乱码)、indent=4(缩进4个空格)
		print("✅ 成功保存 Assistant 信息")
	return assistant_id


# 【🔧 工具二: 创建 Thread 的方法】
def create_thread(debug=False):
	"""
	Creates a new thread.

	Returns:
		str: The ID of the newly created thread.
	"""
	thread = client.beta.threads.create()
	if debug:
		print("Thread id: ", thread.id)
	return thread.id


# 【🔧 工具三: 根据问题获取回答】
def get_completion(assistant_id, thread_id, user_input, funcs, debug=False):
	"""
	Executes a completion request with the given parameters.

	Args:
		assistant_id (str): The ID of the assistant.
		thread_id (str): The ID of the thread.
		user_input (str): The user input content.
		funcs (list): A list of functions.
		debug (bool, optional): Whether to print debug information. Defaults to False.

	Returns:
		str: The message as a response to the completion request.
	"""
	if debug:
		print("debug, 获取回答中...")
  
	# 创建 message
	message = client.beta.threads.messages.create(
		thread_id==thread_id,
		role="user",
		content=user_input
	)

	# 创建 run
	run = client.beta.threads.runs.create(
		thread_id=thread_id,
		assistant_id=assistant_id,
	)
 
	# 运行 run
	while True:
		while run.status in ['queue', 'in_progress']:
			run = client.beta.threads.runs.retrieve( # 当 run 的状态是 queue 或者 in_progress 时, 就一直获取 run 的状态
				thread_id=thread_id,
				run_id=run.id
			)
			time.sleep(1)
   
		# 执行 function
		if run.status == "requires_action":
			tool_calls = run.required_action.submit_tool_outputs.tool_calls # 获取 tool_calls
			tool_outputs = [] # 用于存放 tool_calls 的输出
			for tool_call in tool_calls:
				if debug:
					print("debug:", str(tool_call.function))
				func = next(iter([func for func in funcs if func.__name__ == tool_call.function.name])) # next 表示获取迭代器的下一个元素, 这里是获取 funcs 中的 function ｜ iter 表示生成迭代器 ｜ if func.__name__ == tool_call.function.name 表示如果 func 的 name 等于 tool_call 的 name, 就返回 func
				try:
					output = func(**eval(tool_call.function.arguments)) # eval 表示执行字符串表达式并返回结果, 这里是执行 tool_call.function.arguments
				except Exception as e:
					output = "❌ 运行 Tool 出错了: " + str(e)
				if debug:
					print(f"{tool_call.function.name}: ", output)

				tool_outputs.append({
					"tool_call_id": tool_call.id,
					"output": json.dumps(output)
				})
    
			# 提交 tool_outputs
			run = client.beta.threads.runs.submit_tool_outputs(
				thread_id=thread_id,
				run_id=run.id,
				tool_outputs=tool_outputs
			)
		elif run.status == "completed": # run 的状态已经完成
			raise Exception("❌ 运行 Run 出错了: " + str(run.error))
		else:
			message = client.beta.threads.messages.list( # 返回 thread 的 message
				thread_id=thread_id,
			)
			message = message.data[0].content[0].text.value # 获取 message 的内容
			pattern = r"/imgs/\d{10}\.png" # 正则表达式, 匹配 /imgs/ + 10位数字 + .png
			match = re.search(pattern, message) # re.search 表示在字符串内查找匹配项, 这里是在 message 内查找 pattern
			if match:
				message = {"image": match.group()} # match.group() 表示返回匹配到的字符串
			if debug:
				print("debug message: ", message)
			return message
