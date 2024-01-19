# from openai import OpenAI
# client = OpenAI()
import os
import openai
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()

# 获取 API 密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 设置 API 密钥
openai.api_key = OPENAI_API_KEY

# 打开图片文件和遮罩文件
response = openai.Image.create_edit(
  model="dall-e-2",
  image=open("3D.png", "rb"),
  mask=open("3D_mask.png", "rb"),
  prompt="一只老虎, 3D风格, 白天自然光, 蓝紫色调, 反光带点暖色, 玻璃质感, 中景, 优质的, 高详细度的, 高精度的, 优美的",
  n=1,
  size="1024x1024"
)

# 获取编辑后的图片 URL
image_url = response.data[0].url

# 输出图片 URL
print(image_url)