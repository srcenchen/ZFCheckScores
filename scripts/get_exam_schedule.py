import time
import traceback
from datetime import datetime


def get_exam_schedule(student_client, output_type="none"):
    try:
        # 定义重试次数上限为5次
        attempts = 5
        # 初始化exam_schedule为空列表
        exam_schedule = []

        # 使用while循环最多重试5次获取考试安排信息
        while attempts > 0:

            # 调用student_client的get_exam_schedule方法获取考试安排信息
            exam_data = student_client.get_exam_schedule().get("data", {})
            exam_schedule = exam_data.get("courses", [])

            # 如果exam_schedule不为空，跳出循环
            if exam_schedule:
                break

            # 如果exam_schedule为空，等待1秒后重试
            time.sleep(1)
            # 减少剩余重试次数
            attempts -= 1

        # 考试安排不为空时
        if exam_schedule:
            # 遍历 exam_schedule 中的每个字典，将 title 中的中文括号替换为英文括号
            for exam in exam_schedule:
                if exam.get("title"):
                    exam["title"] = (
                        exam["title"].replace("（", "(").replace("）", ")")
                    )

            # 过滤未结束的考试（考试日期 >= 今天），已过期的不再显示
            today_str = datetime.now().strftime("%Y-%m-%d")
            upcoming_exams = [
                e for e in exam_schedule
                if e.get("time") and e["time"][:10] >= today_str
            ]

            # 按照考试时间升序排序（最近要考的排最前面）
            # 对于没有考试时间的，将时间设置为 9999-12-31，确保排在最后
            sorted_exam = sorted(
                upcoming_exams,
                key=lambda x: (
                    x.get("time")
                    if x.get("time")
                    else "9999-12-31 23:59:59"
                ),
                reverse=False,
            )

            # 最近一场考试时间
            last_exam_time = sorted_exam[0].get("time") if sorted_exam else ""

            # 初始化输出考试安排信息字符串
            integrated_exam_info = "------\n考试安排信息："

            if not sorted_exam:
                integrated_exam_info += "\n暂无未结束的考试安排\n------"
            else:
                # 遍历所有未结束的考试安排
                for _, exam in enumerate(sorted_exam):

                    # 清理教师名称，去除工号前缀 (如 "880382/徐鹤鸣" -> "徐鹤鸣")
                    teacher_raw = exam.get('teacher') or ''
                    teacher_clean = teacher_raw.split('/')[-1] if '/' in teacher_raw else teacher_raw

                    # 整合考试安排信息
                    integrated_exam_info += (
                        f"\n"
                        f"课程名称：{exam.get('title')}\n"
                        f"考试时间：{exam.get('time')}\n"
                        f"考试地点：{exam.get('location')}\n"
                        f"任课教师：{teacher_clean}\n"
                        f"教学班：{exam.get('class_name')}\n"
                        f"考试批次：{exam.get('exam_name')}\n"
                        f"重修标记：{exam.get('retake_flag') or '否'}\n"
                        f"备注：{exam.get('remarks') or '无'}\n"
                        f"------"
                    )

            if output_type == "raw":
                return exam_schedule
            elif output_type == "integrated_exam_info":
                return integrated_exam_info
            elif output_type == "last_exam_time":
                return last_exam_time
            elif output_type == "sorted_exam":
                return sorted_exam
            else:
                return "获取考试安排：参数缺失"

        else:
            if output_type == "raw":
                return []
            return "------\n考试安排信息：\n考试安排为空\n------"

    except Exception:
        print(traceback.format_exc())
        if output_type == "raw":
            return []
        return "获取考试安排时出错"
