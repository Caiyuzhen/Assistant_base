# 存放 funcrion_call 中会调用到的功能函数
import os
import datetime # 用于获取当前时间
import json
import random
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取 API 密钥
NINJAS_API_KEY = os.getenv("NINJAS_API_KEY")

# 设置随机种子, 用来生成随机数
random.seed(2023)


# 随机返回一个城市的方法
def get_city_list():
	"""
	作用：
		从 JSON 中获取城市列表数据
	
	返回:
		list: 城市列表数据
	"""
	city_list = []
 
	# 获取项目根目录的路径 (下一步才能找到 city.json 文件)
	root_dir = os.path.dirname(os.path.dirname(__file__))
    
	# 构建 city.json 的完整路径
	city_file_path = os.path.join(root_dir, 'data', 'city.json') # 🌟 获取 city.json 文件的路径
	
	print("✅ 成功拿到 city.json 文件的路径: ", city_file_path)
 
	with open(city_file_path, "r") as file:
		data = json.load(file) # 读取 city.json 文件 => 从 省份 读取到 -> 城市 的数据
		for province in data['provinces']:
			for city in province['citys']:
				city_list.append(city['cityName'])
	random.shuffle(city_list) # 打乱城市列表数据
	return city_list # 返回城市列表数据


city_list = get_city_list()


# 映射每天的【日期】以及【猫所在的城市】
def generate_city_mapping(year):
	"""
	作用:
		根据给定年份生成日期到城市的映射 (每天去一座城市, 去过后则映射进对象内, 下一次就不去这座城市了)
	参数:
		year (int): 年份
	返回:
		dict: 日期 -> 城市 的映射字典
	"""
	city_mapping = {}
	start_date = datetime.date(year, 1, 1) # 从 1 月 1 日开始
	end_date = datetime.date(year, 12, 31) # 到 12 月 31 日结束
	delta = datetime.timedelta(days=1) # 间隔为 1 天
	current_date = start_date # 当前日期
	while current_date <= end_date:
		city_mapping[current_date] = city_list[current_date.timetuple().tm_yday % len(city_list)] # current_date.timetuple() 表示当前日期的元组 tm_yday % len(city_list) 表示当前日期在城市列表中的索引
		current_date += delta # 日期加 1 天
	return city_mapping


# 固定城市的方法
def get_city_for_date(date_str): # 传入今天的日期, 获取今天所在的城市
	"""
	作用:
		固定猫每天所在的城市, 不然每次运行, 猫都会出现在不同的城市, 不符合逻辑
	参数:
		date_str (str): 日期字符串, 格式为 YYYY-MM-DD
	返回:
		str: 每套所在的城市
	Raises:
		ValueError: 如果日期字符串格式不正确, 则抛出异常
	Examples:
		>>> get_city_for_date("2022-01-01")
		'深圳市'
		>>> get_city_for_date("2022-01-02")
		'广州市'
	"""
	date_format = "%Y-%m-%d" # 日期格式
	try:
		input_date = datetime.datetime.strptime(date_str, date_format).date() # 将日期字符串转换为日期对象
	except ValueError:
		return "无效日期格式。请使用YYYY-MM-DD格式。"
	year_mapping = generate_city_mapping(input_date.year)
	return year_mapping.get(input_date, "日期不在当前年份内")
 
	
     
# 获取每天的回答
def get_qa(category=''): # 传入 category, 获取对应的回答
	"""
	作用:
		获取猫每天的回答
	参数:
		category (str): 问题的分类
	返回:
		dist: 问题 -> 回答 的映射字典
	"""
	api_url = 'https://api.api-ninjas.com/v1/trivia?category={}'.format(category) # 🥷 API 地址 => https://api-ninjas.com/api/trivia
	response = requests.get(api_url, headers={'X-Api-Key': NINJAS_API_KEY}) # 发送请求
	if response.status_code == requests.codes.ok:
		content = response.json()[0]
		del content['category'] # del 表示删除字典中的 category 这个键值对
		return content
	else:
		print("Error:", response.status_code, response.json())
		return {}


if __name__ == "__main__":
	city_on_date = get_city_for_date("2023-11-25")
	print(city_on_date)
	qa = get_qa()
	print(qa)