# 封装 dall-e 生成图片的函数

import os
import io
import time
import base64
import matplotlib.pyplot as plt
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()

# 获取 API 密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



# 把 base64 编码的图片转换为图片对象
def base64_to_img(b64_string):
	"""
	作用:
		把 base64 编码的图片转换为图片对象

	Parameters:
		b64_string (str): base64 编码的图片

	返回:
		Image: 图片对象
    """
	img_data = base64.b64decode(b64_string)
	img = Image.open(io.BytesIO(img_data))
	return img

# 调用 dall-e 3 来生成图片
def get_dalle_image(prompt):
	"""
	作用:
		调用 dall-e 3 来生成图片
	参数
		prompt (str): 图片的描述
	返回:
		img_file_path (str): 图片文件的路径
	"""
	client = OpenAI(api_key=OPENAI_API_KEY)
 
	# 获取当前的时间戳
	timestamp = int(time.time())

	# 调用 dall-e 3 来生成图片并取出响应中的图片数据
	response = client.images.generate(
		model="dall-e-3",
		prompt=prompt,
		n=1,
		quality="hd",
		size="1792x1024",
		# style="natural",
		response_format='b64_json',
	)
	img_b64 = response.data[0].b64_json

	# 保存图片
	image_name = f"{timestamp}.png" # 根据时间戳来命名图片

	# 保存图片
	img_file_path = f"../web/public/imgs/{image_name}"
	with open(img_file_path, "wb") as file:
		file.write(base64.b64decode(img_b64))
	# 绘制图片
	# imgs = base64_to_img(img_b64)
	# plt.imshow(imgs)
	# plt.axis('off')
	# plt.show()
	return {"✅ 图片路径": "/imgs/" + image_name} # 返回图片的路径

if __name__ == "__main__":
	get_dalle_image("一只黑色的小黑猫，背景是成都市，黑猫全身黑色毛发，大大的眼睛像是装满了宇宙，毛发在阳光照射下呈现出紫金色的次表面散射")
