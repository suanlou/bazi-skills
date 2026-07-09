"""
阳历阴历换算模块
实现真太阳时计算、阴历转换、四柱计算功能
"""

import json
import math
from datetime import datetime, timedelta
from lunar_python import Lunar, Solar


class CalendarConverter:
    def __init__(self, config_path="config.json", city_coords_path="city_coordinates.json"):
        """初始化转换器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        with open(city_coords_path, 'r', encoding='utf-8') as f:
            self.city_coords = json.load(f)["中国主要城市经度"]
    
    def get_city_longitude(self, city_name):
        """获取城市经度，支持模糊匹配"""
        # 直接匹配
        if city_name in self.city_coords:
            return self.city_coords[city_name]
        
        # 模糊匹配
        for city, longitude in self.city_coords.items():
            if city_name in city or city in city_name:
                return longitude
        
        # 如果找不到，返回北京经度作为默认值
        print(f"警告：未找到城市 '{city_name}' 的经度信息，使用北京经度作为默认值")
        return self.city_coords["北京"]
    
    def calculate_true_solar_time(self, beijing_time, longitude):
        """计算真太阳时"""
        # 经度时差：(当地经度−120°)×4分钟 (正确方向)
        # 东经>120°为正(加时间)，东经<120°为负(减时间)
        longitude_diff_minutes = (longitude - 120) * 4
        
        # 计算一年中的第几天
        day_of_year = beijing_time.timetuple().tm_yday
        
        # 计算日角 d (以弧度为单位)
        d = 2 * math.pi * (day_of_year - 1) / 365
        
        # 均时差计算 (使用标准公式)
        eot_minutes = 229.2 * (
            0.000075 +
            0.001868 * math.cos(d) -
            0.032077 * math.sin(d) -
            0.014615 * math.cos(2 * d) -
            0.04089 * math.sin(2 * d)
        )
        
        # 真太阳时 = 北京时间 + 经度时差 + 均时差
        total_correction_minutes = longitude_diff_minutes + eot_minutes
        true_solar_time = beijing_time + timedelta(minutes=total_correction_minutes)
        
        return true_solar_time, longitude_diff_minutes, eot_minutes

    def handle_daylight_saving_time(self, input_time):
        """处理夏令时逆转换

        中国夏令时实施期间：1986-1991年
        夏令时期间：4月中旬第一个星期日2时 到 9月中旬第一个星期日2时
        逆转换：如果在夏令时期间，需要将输入时间减去1小时得到真正的北京时间
        """
        year = input_time.year

        # 只有1986-1991年需要处理夏令时
        if year < 1986 or year > 1991:
            return input_time, {
                "是否夏令时期间": False,
                "说明": f"{year}年不在夏令时实施期间(1986-1991)"
            }

        # 计算该年的夏令时开始和结束时间
        dst_start = self._get_dst_start_date(year)
        dst_end = self._get_dst_end_date(year)

        # 判断是否在夏令时期间
        if dst_start <= input_time < dst_end:
            # 在夏令时期间，需要减去1小时得到真正的北京时间
            beijing_time = input_time - timedelta(hours=1)
            dst_info = {
                "是否夏令时期间": True,
                "夏令时开始": dst_start.strftime("%Y年%m月%d日 %H时"),
                "夏令时结束": dst_end.strftime("%Y年%m月%d日 %H时"),
                "输入时间": input_time.strftime("%Y年%m月%d日 %H时%M分"),
                "北京时间": beijing_time.strftime("%Y年%m月%d日 %H时%M分"),
                "说明": "夏令时期间，输入时间减去1小时得到北京时间"
            }
            return beijing_time, dst_info
        else:
            # 不在夏令时期间，输入时间就是北京时间
            dst_info = {
                "是否夏令时期间": False,
                "夏令时开始": dst_start.strftime("%Y年%m月%d日 %H时"),
                "夏令时结束": dst_end.strftime("%Y年%m月%d日 %H时"),
                "说明": "不在夏令时期间，输入时间即为北京时间"
            }
            return input_time, dst_info

    def _get_dst_start_date(self, year):
        """获取指定年份夏令时开始日期：4月中旬第一个星期日2时"""
        # 4月15日作为中旬基准
        mid_april = datetime(year, 4, 15)

        # 找到4月15日当周或之后的第一个星期日
        days_until_sunday = (6 - mid_april.weekday()) % 7
        if days_until_sunday == 0 and mid_april.weekday() != 6:
            days_until_sunday = 7

        dst_start = mid_april + timedelta(days=days_until_sunday)
        # 设置为2时
        dst_start = dst_start.replace(hour=2, minute=0, second=0, microsecond=0)

        return dst_start

    def _get_dst_end_date(self, year):
        """获取指定年份夏令时结束日期：9月中旬第一个星期日2时"""
        # 9月15日作为中旬基准
        mid_september = datetime(year, 9, 15)

        # 找到9月15日当周或之后的第一个星期日
        days_until_sunday = (6 - mid_september.weekday()) % 7
        if days_until_sunday == 0 and mid_september.weekday() != 6:
            days_until_sunday = 7

        dst_end = mid_september + timedelta(days=days_until_sunday)
        # 设置为2时
        dst_end = dst_end.replace(hour=2, minute=0, second=0, microsecond=0)

        return dst_end

    def convert_to_lunar(self, solar_datetime):
        """将阳历转换为阴历"""
        try:
            # 使用lunar_python库进行转换
            solar = Solar.fromYmdHms(
                solar_datetime.year,
                solar_datetime.month, 
                solar_datetime.day,
                solar_datetime.hour,
                solar_datetime.minute,
                solar_datetime.second
            )
            
            lunar = solar.getLunar()
            
            # 获取四柱
            bazi = lunar.getEightChar()
            
            # 获取节气信息
            jieqi = lunar.getJieQi()
            
            return {
                "阴历年": lunar.getYear(),
                "阴历月": lunar.getMonth(),
                "阴历日": lunar.getDay(),
                "阴历时": lunar.getTimeZhi(),
                "年柱": bazi.getYear(),
                "月柱": bazi.getMonth(), 
                "日柱": bazi.getDay(),
                "时柱": bazi.getTime(),
                "节气": jieqi,
                "lunar_obj": lunar
            }
        except Exception as e:
            print(f"阴历转换错误: {e}")
            return None
    
    def process_birth_info(self, birth_year, birth_month, birth_day, 
                          birth_hour, birth_minute, city_name, name):
        """处理出生信息，返回完整的转换结果"""
        
        # 创建原始输入时间
        input_time = datetime(birth_year, birth_month, birth_day,
                             birth_hour, birth_minute)

        # 夏令时逆转换处理
        beijing_time, dst_info = self.handle_daylight_saving_time(input_time)

        # 获取城市经度
        longitude = self.get_city_longitude(city_name)
        
        # 计算真太阳时
        true_solar_time, longitude_diff, eot = self.calculate_true_solar_time(
            beijing_time, longitude
        )
        
        # 转换为阴历
        lunar_info = self.convert_to_lunar(true_solar_time)
        
        if lunar_info is None:
            return None
        
        result = {
            "姓名": name,
            "出生地": city_name,
            "经度": longitude,
            "输入时间": input_time.strftime("%Y年%m月%d日 %H时%M分"),
            "北京时间": beijing_time.strftime("%Y年%m月%d日 %H时%M分"),
            "夏令时信息": dst_info,
            "经度时差": f"{longitude_diff:.2f}分钟",
            "均时差": f"{eot:.2f}分钟",
            "真太阳时": true_solar_time.strftime("%Y年%m月%d日 %H时%M分"),
            "阴历信息": lunar_info,
            "四柱": {
                "年柱": lunar_info["年柱"],
                "月柱": lunar_info["月柱"],
                "日柱": lunar_info["日柱"],
                "时柱": lunar_info["时柱"]
            }
        }
        
        return result
    
    def format_output(self, result):
        """格式化输出结果"""
        if result is None:
            return "转换失败"
        
        output = f"""
=== 阳历阴历换算结果 ===
姓名：{result['姓名']}
出生地：{result['出生地']} (经度: {result['经度']}°)

时间换算：
北京时间：{result['北京时间']}
经度时差：{result['经度时差']}
均时差：{result['均时差']}
真太阳时：{result['真太阳时']}

阴历信息：
阴历日期：{result['阴历信息']['阴历年']}年{result['阴历信息']['阴历月']}月{result['阴历信息']['阴历日']}日 {result['阴历信息']['阴历时']}时

四柱八字：
年柱：{result['四柱']['年柱']}
月柱：{result['四柱']['月柱']}
日柱：{result['四柱']['日柱']}
时柱：{result['四柱']['时柱']}

节气：{result['阴历信息']['节气']}
"""
        return output


# 测试函数
def test_calendar_converter():
    """测试阳历阴历换算模块"""
    converter = CalendarConverter()
    
    # 测试数据 (修正为15:00)
    result = converter.process_birth_info(
        birth_year=1990,
        birth_month=5,
        birth_day=15,
        birth_hour=15,
        birth_minute=0,
        city_name="广州",
        name="测试用户"
    )
    
    print(converter.format_output(result))
    return result


if __name__ == "__main__":
    test_calendar_converter()
