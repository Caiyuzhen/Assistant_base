# 集合函数
import time

def get_completion(message, agent, threas):
	"""
		根据提供的消息执行线程并检索完成的结果
  
  		该函数将向指定的线程提交消息, 触发函数数组的执行
		在 func 参数中定义。数组中的每个函数都必须实现一个返回输出的“run()”方法。
  
		参数:
		- message(Str): 要处理的输入消息
		- Agent(OpenAI Assistant): 将要处理消息的代理实例
		- funcs(List): 一个包含要执行的函数的列表
		- Thread(线程): OpenAI Assistant API 线程实例, 线程负责管理执行的流程

		返回:
		- str: 作为字符串的完成输出内容, 在执行输入消息和函数后, 从代理中进行获取
 	"""
	# 在线程中创建新消息
	message = client.beta.threads.message.create({
		thread_id = thread.id,
		role = "user",
		content = message
	})
 
	# 运行线程
	run = client.beta.threads.runs.create({
		thread_id = thread.id,
		assistant_id = agent.id
	})
 
	while True:
		# 检查线程是否已完成
		while run.status in ['queue', 'in_progress']:
			run = client.beta.threads.runs.retrieve(
				thread_id = thread.id,
				run_id = run.id
			)
			time.sleep(1)

		# 执行函数
		if run.status == "requires_action":
			tool_calls = run.required_action.submit_tool_outputs.tool_calls
			tool_outputs = []
			for tool_calls in tool_calls: # 遍历工具
				wprint('\033[31m' + str(tool_call.function) + '\033[0m') 

				# 找到要执行的工具
				func = next(iter([func for func in funcs if func.__name__ == tool_call.function.name]))
				
    			# 执行工具
				try:
					# 初始化工具
					func = func(**eval(tool_call.function.arguments))
     
					# 从工具中获取输出
					output = func.run()
				except Exception as e:
					print(e) # 打印错误
					output = "Error: " + str(e)

				wprint(f"\033[33m{tool_call.function.name}: ", output, '\033[0m')
				tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
    
			# 提交工具输出
			run = client.beta.threads.runs.submit_tool_outputs(
				thread_id = thread.id,
				run_id = run.id,
			)
   
		# 处理报错
		elif run.status == "failed":
			print(run.error)
			raise Exception("❌ 线程运行错误", run.last_error)
		else:
			message = client.beta.threads.messages.list(
				thread_id = thread.id,
			)
			message = message.data[0].content[0].text.value
			return message
	
 