"""
十神计算模块
实现十神识别、权重计算、身强身弱判断、喜用神忌神分析
"""

import json
from .wuxing_calculator import WuxingCalculator


class ShishenCalculator:
    def __init__(self, config_path="config.json"):
        """初始化十神计算器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # 初始化五行计算器以访问五行生克关系
        self.wuxing_calculator = WuxingCalculator(config_path)
        
        # 天干五行阴阳属性
        self.tiangan_info = {
            '甲': {'五行': '木', '阴阳': '阳'},
            '乙': {'五行': '木', '阴阳': '阴'},
            '丙': {'五行': '火', '阴阳': '阳'},
            '丁': {'五行': '火', '阴阳': '阴'},
            '戊': {'五行': '土', '阴阳': '阳'},
            '己': {'五行': '土', '阴阳': '阴'},
            '庚': {'五行': '金', '阴阳': '阳'},
            '辛': {'五行': '金', '阴阳': '阴'},
            '壬': {'五行': '水', '阴阳': '阳'},
            '癸': {'五行': '水', '阴阳': '阴'}
        }
        
        # 地支藏干信息 - 使用config配置的权重
        self.dizhi_canggan = self._build_dizhi_canggan_with_config()

        # 地支五行属性
        self.dizhi_info = {
            '子': {'五行': '水'},
            '丑': {'五行': '土'},
            '寅': {'五行': '木'},
            '卯': {'五行': '木'},
            '辰': {'五行': '土'},
            '巳': {'五行': '火'},
            '午': {'五行': '火'},
            '未': {'五行': '土'},
            '申': {'五行': '金'},
            '酉': {'五行': '金'},
            '戌': {'五行': '土'},
            '亥': {'五行': '水'}
        }

        # 五行生克关系
        self.wuxing_sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        self.wuxing_ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}

        # 配偶星对照表
        self.spouse_star = {
            '甲': {'男': {'正财': '己', '偏财': '戊'}, '女': {'正官': '辛', '七杀': '庚'}},
            '乙': {'男': {'正财': '戊', '偏财': '己'}, '女': {'正官': '庚', '七杀': '辛'}},
            '丙': {'男': {'正财': '辛', '偏财': '庚'}, '女': {'正官': '癸', '七杀': '壬'}},
            '丁': {'男': {'正财': '庚', '偏财': '辛'}, '女': {'正官': '壬', '七杀': '癸'}},
            '戊': {'男': {'正财': '癸', '偏财': '壬'}, '女': {'正官': '乙', '七杀': '甲'}},
            '己': {'男': {'正财': '壬', '偏财': '癸'}, '女': {'正官': '甲', '七杀': '乙'}},
            '庚': {'男': {'正财': '乙', '偏财': '甲'}, '女': {'正官': '丁', '七杀': '丙'}},
            '辛': {'男': {'正财': '甲', '偏财': '乙'}, '女': {'正官': '丙', '七杀': '丁'}},
            '壬': {'男': {'正财': '丁', '偏财': '丙'}, '女': {'正官': '己', '七杀': '戊'}},
            '癸': {'男': {'正财': '丙', '偏财': '丁'}, '女': {'正官': '戊', '七杀': '己'}}
        }

    def _build_dizhi_canggan_with_config(self):
        """根据config配置构建地支藏干权重"""
        # 基础地支藏干结构（天干顺序）
        base_structure = {
            '子': ['癸'],
            '丑': ['己', '癸', '辛'],
            '寅': ['甲', '丙', '戊'],
            '卯': ['乙'],
            '辰': ['戊', '乙', '癸'],
            '巳': ['丙', '戊', '庚'],
            '午': ['丁', '己'],
            '未': ['己', '丁', '乙'],
            '申': ['庚', '壬', '戊'],
            '酉': ['辛'],
            '戌': ['戊', '辛', '丁'],
            '亥': ['壬', '甲']
        }

        # 从config获取权重配置
        canggan_config = self.config['藏干权重']

        # 构建带权重的藏干字典
        result = {}
        for zhi, gans in base_structure.items():
            result[zhi] = {}

            if len(gans) == 1:
                # 只有本气
                result[zhi][gans[0]] = canggan_config['本气']
            elif len(gans) == 2:
                # 本气 + 中气
                result[zhi][gans[0]] = canggan_config['本气_中气']['本气']
                result[zhi][gans[1]] = canggan_config['本气_中气']['中气']
            elif len(gans) == 3:
                # 本气 + 中气 + 余气
                result[zhi][gans[0]] = canggan_config['本气_中气_余气']['本气']
                result[zhi][gans[1]] = canggan_config['本气_中气_余气']['中气']
                result[zhi][gans[2]] = canggan_config['本气_中气_余气']['余气']

        return result

    def get_wuxing_relation(self, my_wuxing, other_wuxing):
        """获取五行生克关系"""
        if my_wuxing == other_wuxing:
            return '同我'
        elif self.wuxing_sheng.get(my_wuxing) == other_wuxing:
            return '我生'
        elif self.wuxing_sheng.get(other_wuxing) == my_wuxing:
            return '生我'
        elif self.wuxing_ke.get(my_wuxing) == other_wuxing:
            return '我克'
        elif self.wuxing_ke.get(other_wuxing) == my_wuxing:
            return '克我'
        else:
            return '无关'
    
    def determine_shishen(self, day_gan, other_gan):
        """确定十神类型"""
        day_info = self.tiangan_info[day_gan]
        other_info = self.tiangan_info[other_gan]
        
        relation = self.get_wuxing_relation(day_info['五行'], other_info['五行'])
        same_yinyang = day_info['阴阳'] == other_info['阴阳']
        
        if relation == '同我':
            return '比肩' if same_yinyang else '劫财'
        elif relation == '生我':
            return '偏印' if same_yinyang else '正印'
        elif relation == '克我':
            return '七杀' if same_yinyang else '正官'
        elif relation == '我克':
            return '偏财' if same_yinyang else '正财'
        elif relation == '我生':
            return '食神' if same_yinyang else '伤官'
        else:
            return '未知'
    
    def calculate_shishen_weights(self, sizhu):
        """计算十神权重（用于十神权重汇总显示，不应用月干支权重系数）"""
        day_gan = sizhu['日柱'][0]
        shishen_weights = {}

        # 获取配置参数
        tougan_coeff = self.config['十神计算参数']['透干权重系数']

        # 分析每个位置的天干和藏干
        positions = [
            ('年柱', sizhu['年柱']),
            ('月柱', sizhu['月柱']),
            ('时柱', sizhu['时柱'])  # 日柱不分析自己
        ]

        for pos_name, (gan, zhi) in positions:
            # 天干分析
            if gan != day_gan:  # 不分析日干自己
                shishen = self.determine_shishen(day_gan, gan)
                if shishen not in shishen_weights:
                    shishen_weights[shishen] = 0

                weight = 1.0  # 天干基础权重为1，十神权重汇总时不应用月干支权重系数
                shishen_weights[shishen] += weight

            # 地支藏干分析
            canggan_dict = self.dizhi_canggan[zhi]
            for canggan, base_weight in canggan_dict.items():
                if canggan != day_gan:  # 不分析日干自己
                    shishen = self.determine_shishen(day_gan, canggan)
                    if shishen not in shishen_weights:
                        shishen_weights[shishen] = 0

                    # 十神权重汇总时不应用月干支权重系数
                    shishen_weights[shishen] += base_weight

        # 分析日支藏干（除了日干本身）
        day_zhi = sizhu['日柱'][1]
        day_canggan = self.dizhi_canggan[day_zhi]
        for canggan, base_weight in day_canggan.items():
            if canggan != day_gan:
                shishen = self.determine_shishen(day_gan, canggan)
                if shishen not in shishen_weights:
                    shishen_weights[shishen] = 0

                shishen_weights[shishen] += base_weight

        # 处理透干情况：检查所有地支藏干是否与日干一致
        all_positions = [
            ('年柱', sizhu['年柱'][1]),
            ('月柱', sizhu['月柱'][1]),
            ('日柱', sizhu['日柱'][1]),
            ('时柱', sizhu['时柱'][1])
        ]

        for pos_name, zhi in all_positions:
            canggan_dict = self.dizhi_canggan[zhi]
            for canggan, base_weight in canggan_dict.items():
                if canggan == day_gan:  # 透干情况
                    # 透干相当于增强日主力量，计入比肩
                    shishen = '比肩'
                    if shishen not in shishen_weights:
                        shishen_weights[shishen] = 0

                    # 十神权重汇总时，透干权重乘以透干系数，但不乘以月干支权重系数
                    final_weight = base_weight * tougan_coeff
                    shishen_weights[shishen] += final_weight

        # 排序
        sorted_shishen = sorted(shishen_weights.items(), key=lambda x: x[1], reverse=True)

        return dict(sorted_shishen)

    def calculate_body_strength_traditional(self, sizhu):
        """
        传统综合评分法计算身强身弱
        四大评判维度：得令(50%) + 得地(30%) + 得势(15%) + 得生(5%)
        """
        day_gan = sizhu['日柱'][0]
        day_wuxing = self.tiangan_info[day_gan]['五行']

        # 总分初始化
        total_score = 0
        details = {}

        # 1. 得令（看月令 - 权重50%）
        deling_score = self._calculate_deling_score(day_wuxing, sizhu['月柱'][1])
        total_score += deling_score * 0.5
        details['得令'] = {
            '月支': sizhu['月柱'][1],
            '日主五行': day_wuxing,
            '得令状态': self._get_deling_status(day_wuxing, sizhu['月柱'][1]),
            '得分': deling_score,
            '权重后得分': deling_score * 0.5
        }

        # 2. 得地（看地支根气 - 权重30%）
        dedi_score, dedi_details = self._calculate_dedi_score(day_gan, day_wuxing, sizhu)
        total_score += dedi_score * 0.3
        details['得地'] = {
            '得分': dedi_score,
            '权重后得分': dedi_score * 0.3,
            '详情': dedi_details
        }

        # 3. 得势（看天干比劫 - 权重15%）
        deshi_score, deshi_details = self._calculate_deshi_score(day_gan, sizhu)
        total_score += deshi_score * 0.15
        details['得势'] = {
            '得分': deshi_score,
            '权重后得分': deshi_score * 0.15,
            '详情': deshi_details
        }

        # 4. 得生（看天干印星 - 权重5%）
        desheng_score, desheng_details = self._calculate_desheng_score(day_gan, day_wuxing, sizhu)
        total_score += desheng_score * 0.05
        details['得生'] = {
            '得分': desheng_score,
            '权重后得分': desheng_score * 0.05,
            '详情': desheng_details
        }

        # 判断身强身弱（通常以50分为界限）
        if total_score >= 50:
            strength = '身强'
        else:
            strength = '身弱'

        return strength, total_score, details

    def _calculate_deling_score(self, day_wuxing, month_zhi):
        """计算得令得分（看月令）"""
        # 获取月支的五行属性
        month_wuxing = self.dizhi_info[month_zhi]['五行']

        # 判断得令状态
        if day_wuxing == month_wuxing:
            # 旺：日主五行 = 月支五行（最强得令）
            return 100
        elif self.wuxing_calculator.wuxing_sheng.get(month_wuxing) == day_wuxing:
            # 相：月支五行生日主五行（次强得令）
            return 80
        elif self.wuxing_calculator.wuxing_ke.get(day_wuxing) == month_wuxing:
            # 休：日主五行克月支五行
            return 30
        elif self.wuxing_calculator.wuxing_ke.get(month_wuxing) == day_wuxing:
            # 囚：月支五行克日主五行
            return 10
        else:
            # 死：其他情况
            return 0

    def _get_deling_status(self, day_wuxing, month_zhi):
        """获取得令状态描述"""
        month_wuxing = self.dizhi_info[month_zhi]['五行']

        if day_wuxing == month_wuxing:
            return '旺'
        elif self.wuxing_calculator.wuxing_sheng.get(month_wuxing) == day_wuxing:
            return '相'
        elif self.wuxing_calculator.wuxing_ke.get(day_wuxing) == month_wuxing:
            return '休'
        elif self.wuxing_calculator.wuxing_ke.get(month_wuxing) == day_wuxing:
            return '囚'
        else:
            return '死'

    def _calculate_dedi_score(self, day_gan, day_wuxing, sizhu):
        """计算得地得分（看地支根气）"""
        score = 0
        details = []

        # 定义根的类型和分值
        # 强根：禄（本气）、劫（同类阴阳）、墓库
        # 中根：余气根

        # 检查日支（权重最高）
        day_zhi = sizhu['日柱'][1]
        day_root_score = self._get_root_score(day_gan, day_wuxing, day_zhi, '日支')
        score += day_root_score * 2  # 日支权重加倍
        if day_root_score > 0:
            details.append(f"日支{day_zhi}: {day_root_score}分 (权重x2)")

        # 检查年支和时支
        for pos, zhi in [('年支', sizhu['年柱'][1]), ('时支', sizhu['时柱'][1])]:
            root_score = self._get_root_score(day_gan, day_wuxing, zhi, pos)
            score += root_score
            if root_score > 0:
                details.append(f"{pos}{zhi}: {root_score}分")

        return min(score, 100), details  # 最高100分

    def _get_root_score(self, day_gan, day_wuxing, zhi, position):
        """获取单个地支的根气得分"""
        canggan_dict = self.dizhi_canggan[zhi]

        for canggan, weight in canggan_dict.items():
            canggan_wuxing = self.tiangan_info[canggan]['五行']

            if canggan == day_gan:
                # 禄：完全相同的天干
                return 50
            elif canggan_wuxing == day_wuxing:
                # 同类五行但不同阴阳（劫财关系）
                if weight >= 0.6:  # 本气或中气
                    return 30
                else:  # 余气
                    return 15

        # 检查墓库关系
        if self._is_muzang_relation(day_wuxing, zhi):
            return 25

        return 0

    def _is_muzang_relation(self, day_wuxing, zhi):
        """判断是否为墓库关系"""
        muzang_relations = {
            '木': ['未'],  # 木墓于未
            '火': ['戌'],  # 火墓于戌
            '土': ['戌'],  # 土墓于戌
            '金': ['丑'],  # 金墓于丑
            '水': ['辰']   # 水墓于辰
        }
        return zhi in muzang_relations.get(day_wuxing, [])

    def _calculate_deshi_score(self, day_gan, sizhu):
        """计算得势得分（看天干比劫）"""
        score = 0
        details = []
        day_wuxing = self.tiangan_info[day_gan]['五行']

        # 检查年干、月干、时干
        for pos, gan in [('年干', sizhu['年柱'][0]), ('月干', sizhu['月柱'][0]), ('时干', sizhu['时柱'][0])]:
            if gan != day_gan:  # 不算日干自己
                gan_wuxing = self.tiangan_info[gan]['五行']
                if gan_wuxing == day_wuxing:
                    # 同类五行（比肩或劫财）
                    if gan == day_gan:
                        score += 30  # 比肩
                        details.append(f"{pos}{gan}: 比肩 +30分")
                    else:
                        score += 25  # 劫财
                        details.append(f"{pos}{gan}: 劫财 +25分")

        return min(score, 100), details  # 最高100分

    def _calculate_desheng_score(self, day_gan, day_wuxing, sizhu):
        """计算得生得分（看天干印星）"""
        score = 0
        details = []

        # 检查年干、月干、时干
        for pos, gan in [('年干', sizhu['年柱'][0]), ('月干', sizhu['月柱'][0]), ('时干', sizhu['时柱'][0])]:
            if gan != day_gan:  # 不算日干自己
                gan_wuxing = self.tiangan_info[gan]['五行']
                # 检查是否为印星（生日主的五行）
                if self.wuxing_calculator.wuxing_sheng.get(gan_wuxing) == day_wuxing:
                    # 判断正印还是偏印
                    gan_yinyang = self.tiangan_info[gan]['阴阳']
                    day_yinyang = self.tiangan_info[day_gan]['阴阳']

                    if gan_yinyang != day_yinyang:
                        score += 20  # 正印
                        details.append(f"{pos}{gan}: 正印 +20分")
                    else:
                        score += 15  # 偏印
                        details.append(f"{pos}{gan}: 偏印 +15分")

        return min(score, 100), details  # 最高100分

    def analyze_body_strength(self, sizhu):
        """分析身强身弱（使用传统综合评分法）"""
        # 使用新的传统综合评分法
        strength, total_score, details = self.calculate_body_strength_traditional(sizhu)

        # 返回传统综合评分法的结果，包含详细信息
        return {
            'method': 'traditional',
            'strength': strength,
            'total_score': total_score,
            'details': details
        }
    
    def determine_xiyongshen(self, body_strength, shishen_weights):
        """确定喜用神和忌神"""
        if body_strength == '身强':
            # 身强需要克泄耗
            xiyong_types = ['正官', '七杀', '食神', '伤官', '正财', '偏财']
            ji_types = ['正印', '偏印', '比肩', '劫财']
        else:
            # 身弱需要生扶
            xiyong_types = ['正印', '偏印', '比肩', '劫财']
            ji_types = ['正官', '七杀', '食神', '伤官', '正财', '偏财']

        # 收集喜用神并按权重排序
        xiyong_list = []
        for shishen_type in xiyong_types:
            if shishen_type in shishen_weights:
                xiyong_list.append((shishen_type, shishen_weights[shishen_type]))

        # 按权重从高到低排序喜用神
        xiyong_list.sort(key=lambda x: x[1], reverse=True)

        # 收集忌神并按权重排序
        ji_list = []
        for shishen_type in ji_types:
            if shishen_type in shishen_weights:
                ji_list.append((shishen_type, shishen_weights[shishen_type]))

        # 按权重从高到低排序忌神
        ji_list.sort(key=lambda x: x[1], reverse=True)

        return xiyong_list, ji_list
    
    def analyze_spouse_info(self, sizhu, gender):
        """分析夫妻宫和配偶星"""
        day_gan = sizhu['日柱'][0]
        day_zhi = sizhu['日柱'][1]  # 夫妻宫
        
        # 配偶星
        spouse_stars = self.spouse_star[day_gan][gender]
        
        # 在八字中寻找配偶星
        spouse_star_found = {}
        all_gans = [sizhu['年柱'][0], sizhu['月柱'][0], sizhu['时柱'][0]]
        
        # 加上藏干
        for zhi in [sizhu['年柱'][1], sizhu['月柱'][1], sizhu['日柱'][1], sizhu['时柱'][1]]:
            canggan_dict = self.dizhi_canggan[zhi]
            for gan, weight in canggan_dict.items():
                all_gans.append(gan)
        
        for star_type, star_gan in spouse_stars.items():
            count = all_gans.count(star_gan)
            if count > 0:
                spouse_star_found[star_type] = count
        
        return {
            '夫妻宫': day_zhi,
            '配偶星': spouse_star_found
        }
    
    def format_shishen_output(self, sizhu, shishen_weights, body_analysis, 
                             xiyong_info, spouse_info, gender='男'):
        """格式化十神分析输出"""
        body_strength, support_power, drain_power = body_analysis
        xiyong_list, ji_list = xiyong_info
        
        output = f"""
=== 十神分析结果 ===
日主：{sizhu['日柱'][0]} ({self.tiangan_info[sizhu['日柱'][0]]['五行']}{self.tiangan_info[sizhu['日柱'][0]]['阴阳']})

十神权重分布：
"""
        for shishen, weight in shishen_weights.items():
            output += f"{shishen}：{weight:.2f}\n"
        
        output += f"""
身强身弱分析：
判定结果：{body_strength}
生扶力量：{support_power:.2f}
克泄耗力量：{drain_power:.2f}

喜用神：
"""
        for shishen, weight in xiyong_list[:4]:  # 显示前4个
            output += f"{shishen} ({weight:.2f}) "
        
        output += f"""

忌神：
"""
        for shishen, weight in ji_list[:4]:  # 显示前4个
            output += f"{shishen} ({weight:.2f}) "
        
        output += f"""

夫妻宫配偶星分析：
夫妻宫：{spouse_info['夫妻宫']}
配偶星：{spouse_info['配偶星']}
"""
        
        return output


# 测试函数
def test_shishen_calculator():
    """测试十神计算模块"""
    from calendar_converter import CalendarConverter
    
    # 先获取四柱信息
    converter = CalendarConverter()
    result = converter.process_birth_info(
        birth_year=1990,
        birth_month=5,
        birth_day=15,
        birth_hour=14,
        birth_minute=30,
        city_name="广州",
        name="测试用户"
    )
    
    # 计算十神
    calculator = ShishenCalculator()
    shishen_weights = calculator.calculate_shishen_weights(result['四柱'])
    body_analysis = calculator.analyze_body_strength(shishen_weights)
    xiyong_info = calculator.determine_xiyongshen(body_analysis[0], shishen_weights)
    spouse_info = calculator.analyze_spouse_info(result['四柱'], '男')
    
    print(calculator.format_shishen_output(
        result['四柱'], shishen_weights, body_analysis, 
        xiyong_info, spouse_info, '男'
    ))
    
    return shishen_weights, body_analysis, xiyong_info


if __name__ == "__main__":
    test_shishen_calculator()
