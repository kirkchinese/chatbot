# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key="sk-862159fd441345c0ae51a129101d2ebe", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[
        {"role": "system", "content": ""},
        {"role": "user", "content": "现在是25年,我需要填写一个表名为《团支部推荐优秀团员为入党积极分子信息登记表》，其中包含的主要信息有:姓名:徐路,自动化专业，所属团支部自动化2202，现担任学生组织社团或班级职务：校学生代表大会委员，入团时间，2023年11月。何时何地递交入党申请书：2022年9月于军训队伍中初次递交入党申请书.智育专业排名:18/65,德育排名:3/65，曾受到何种奖励或处分：浙大城市学院新生军训演讲团体一等奖、23年学生会优秀干部、24届浙大城市学院青年马克思主义者学生骨干、19届杭州亚运会志愿者每日之星、Robotmaster无人飞行器智能感知技术竞赛综合赛优秀奖、优秀干部奖学金、2024年浙大城市学院第三届大学生机器人竟赛优胜奖、2024年浙江省第八届大学生机器人竞赛三等奖，第六届浙江省大学生智能机器人创意竞赛三等奖、2024年浙大城市学院物理实验与科技创新竟赛三等奖。主要经历有：先后担任，摄影部干事，文字部干事，宣传部干事，宣传部部长，学生代表大会委员等职务。我现在需要着重填写自我表现及自荐理由部分，请你帮我生成一份。下面是我22年写的一份自荐，可供参考：本人作为一名光荣的浙大城市学院大二学生，积极向党组织靠拢，第一时间提交入党申请书，在学习方面，积极、努力、刻苦，成绩一直名列前茅。积极帮助同学共同进步。在担任学生会干事和部长期间不折不扣的完成老师和领导交给的各项任务，积极参加学院组织的各项活动。在亚运会和亚残会期间作为志愿者，圆满的完成了党、团组织的各项工作，并得到党、团组织的认可。现为“青年马克思主义者（学生骨干）”学员，积极学习党的基本知识，提高自己理论素养。在今后的生活和学习中，我将努力理论结合实际，使我党的各项基本原则落到实处，以一个党员的标准严格要求自己。希望党组织考验我。"},
    ],
    stream=False
)

print(response.choices[0].message.content)
# for chunk in response:
#     print(chunk['message']['content'], end='', flush=True)