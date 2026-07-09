"""
命格计算模块
按照八字命格完全分类与喜用神细则总表，严格按优先级判断格局类型和喜用神忌神
"""

import json


class MinggeCalculator:
    def __init__(self, config_path="config.json"):
        """初始化命格计算器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 天干五行属性
        self.tiangan_wuxing = {
            '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
            '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
        }
        
        # 地支五行属性
        self.dizhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
            '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        
        # 地支藏干
        self.dizhi_canggan = {
            '子': ['癸'], '丑': ['己', '癸', '辛'], '寅': ['甲', '丙', '戊'], '卯': ['乙'],
            '辰': ['戊', '乙', '癸'], '巳': ['丙', '戊', '庚'], '午': ['丁', '己'], '未': ['己', '丁', '乙'],
            '申': ['庚', '壬', '戊'], '酉': ['辛'], '戌': ['戊', '辛', '丁'], '亥': ['壬', '甲']
        }
        
        # 十神映射关系（以日干为中心）
        self.shishen_map = {
            '甲': {'甲': '比肩', '乙': '劫财', '丙': '食神', '丁': '伤官', '戊': '偏财', '己': '正财', '庚': '七杀', '辛': '正官', '壬': '偏印', '癸': '正印'},
            '乙': {'甲': '劫财', '乙': '比肩', '丙': '伤官', '丁': '食神', '戊': '正财', '己': '偏财', '庚': '正官', '辛': '七杀', '壬': '正印', '癸': '偏印'},
            '丙': {'甲': '偏印', '乙': '正印', '丙': '比肩', '丁': '劫财', '戊': '食神', '己': '伤官', '庚': '偏财', '辛': '正财', '壬': '七杀', '癸': '正官'},
            '丁': {'甲': '正印', '乙': '偏印', '丙': '劫财', '丁': '比肩', '戊': '伤官', '己': '食神', '庚': '正财', '辛': '偏财', '壬': '正官', '癸': '七杀'},
            '戊': {'甲': '七杀', '乙': '正官', '丙': '偏印', '丁': '正印', '戊': '比肩', '己': '劫财', '庚': '食神', '辛': '伤官', '壬': '偏财', '癸': '正财'},
            '己': {'甲': '正官', '乙': '七杀', '丙': '正印', '丁': '偏印', '戊': '劫财', '己': '比肩', '庚': '伤官', '辛': '食神', '壬': '正财', '癸': '偏财'},
            '庚': {'甲': '偏财', '乙': '正财', '丙': '七杀', '丁': '正官', '戊': '偏印', '己': '正印', '庚': '比肩', '辛': '劫财', '壬': '食神', '癸': '伤官'},
            '辛': {'甲': '正财', '乙': '偏财', '丙': '正官', '丁': '七杀', '戊': '正印', '己': '偏印', '庚': '劫财', '辛': '比肩', '壬': '伤官', '癸': '食神'},
            '壬': {'甲': '食神', '乙': '伤官', '丙': '偏财', '丁': '正财', '戊': '七杀', '己': '正官', '庚': '偏印', '辛': '正印', '壬': '比肩', '癸': '劫财'},
            '癸': {'甲': '伤官', '乙': '食神', '丙': '正财', '丁': '偏财', '戊': '正官', '己': '七杀', '庚': '正印', '辛': '偏印', '壬': '劫财', '癸': '比肩'}
        }
        
        # 五行到颜色、方位、数字的映射
        self.wuxing_attributes = {
            '木': {
                '衍生色': '绿色',
                '方位': ['东北', '东方'],  # 寅（东北）、卯（东方）
                '数字': [3, 8]  # 甲3、乙8
            },
            '火': {
                '衍生色': '紫色',
                '方位': ['东南', '南方'],  # 巳（东南）、午（南方）
                '数字': [2, 7]  # 丙2、丁7
            },
            '土': {
                '衍生色': '棕色',
                '方位': ['中央', '东北', '东南', '西南', '西北'],  # 戊己中央，丑辰未戌四隅
                '数字': [5, 10]  # 戊5、己10
            },
            '金': {
                '衍生色': '银色',
                '方位': ['西南', '西方'],  # 申（西南）、酉（西方）
                '数字': [4, 9]  # 庚4、辛9
            },
            '水': {
                '衍生色': '蓝色',
                '方位': ['北方', '西北'],  # 子（北方）、亥（西北）
                '数字': [1, 6]  # 壬1、癸6
            }
        }

        # 长生十二宫对应关系（日干在月支的状态）
        self.changsheng_state = {
            '甲': {'寅': '临官', '卯': '帝旺', '辰': '衰', '巳': '病', '午': '死', '未': '墓', '申': '绝', '酉': '胎', '戌': '养', '亥': '长生', '子': '沐浴', '丑': '冠带'},
            '乙': {'寅': '帝旺', '卯': '临官', '辰': '衰', '巳': '病', '午': '死', '未': '墓', '申': '绝', '酉': '胎', '戌': '养', '亥': '死', '子': '长生', '丑': '衰'},
            '丙': {'寅': '长生', '卯': '沐浴', '辰': '冠带', '巳': '临官', '午': '帝旺', '未': '衰', '申': '病', '酉': '死', '戌': '墓', '亥': '绝', '子': '胎', '丑': '养'},
            '丁': {'寅': '沐浴', '卯': '长生', '辰': '冠带', '巳': '帝旺', '午': '临官', '未': '衰', '申': '病', '酉': '死', '戌': '墓', '亥': '胎', '子': '绝', '丑': '养'},
            '戊': {'寅': '长生', '卯': '沐浴', '辰': '冠带', '巳': '临官', '午': '帝旺', '未': '衰', '申': '病', '酉': '死', '戌': '墓', '亥': '绝', '子': '胎', '丑': '养'},
            '己': {'寅': '沐浴', '卯': '长生', '辰': '冠带', '巳': '帝旺', '午': '临官', '未': '衰', '申': '病', '酉': '死', '戌': '墓', '亥': '胎', '子': '绝', '丑': '养'},
            '庚': {'寅': '绝', '卯': '胎', '辰': '养', '巳': '长生', '午': '沐浴', '未': '冠带', '申': '临官', '酉': '帝旺', '戌': '衰', '亥': '病', '子': '死', '丑': '墓'},
            '辛': {'寅': '胎', '卯': '绝', '辰': '养', '巳': '沐浴', '午': '长生', '未': '冠带', '申': '帝旺', '酉': '临官', '戌': '衰', '亥': '病', '子': '死', '丑': '墓'},
            '壬': {'寅': '病', '卯': '死', '辰': '墓', '巳': '绝', '午': '胎', '未': '养', '申': '长生', '酉': '沐浴', '戌': '冠带', '亥': '临官', '子': '帝旺', '丑': '衰'},
            '癸': {'寅': '死', '卯': '病', '辰': '墓', '巳': '绝', '午': '胎', '未': '养', '申': '沐浴', '酉': '长生', '戌': '冠带', '亥': '帝旺', '子': '临官', '丑': '衰'}
        }

    def calculate_mingge(self, sizhu, wuxing_scores, shishen_weights, month_info):
        """
        按照优先级严格计算命格类型和喜用神忌神
        参数：
        - sizhu: 四柱八字
        - wuxing_scores: 五行力量分数
        - shishen_weights: 十神权重
        - month_info: 月份信息
        """
        result = {
            'main_format': '',           # 主要格局
            'sub_format': '',            # 副格局（月令格局标签）
            'xi_shen': [],               # 喜神
            'yong_shen': [],             # 用神
            'ji_shen': [],               # 忌神
            'analysis': ''               # 格局分析
        }
        
        year_gan, year_zhi = sizhu['年柱']
        month_gan, month_zhi = sizhu['月柱']
        day_gan, day_zhi = sizhu['日柱']
        hour_gan, hour_zhi = sizhu['时柱']
        
        # 计算各十神的力量占比
        # wuxing_scores的值是字典，需要提取'力量值'
        wuxing_power_values = {k: v['力量值'] if isinstance(v, dict) else v for k, v in wuxing_scores.items()}
        total_power = sum(wuxing_power_values.values())
        wuxing_percent = {k: (v / total_power * 100) if total_power > 0 else 0 for k, v in wuxing_power_values.items()}
        
        # 计算印比力量和克泄耗力量
        yin_bi_power = self._get_yin_bi_power(shishen_weights)
        ke_xie_hao_power = self._get_ke_xie_hao_power(shishen_weights)
        
        # 第一优先级：特殊格局（规则颠覆）
        special_format = self._check_special_format(sizhu, wuxing_percent, shishen_weights)
        if special_format:
            result.update(special_format)
            # 添加月令格局标签
            sub_format = self._get_monthly_format(month_zhi, month_gan, day_gan)
            if sub_format:
                result['sub_format'] = sub_format
            return result
        
        # 第二优先级：调候格局（环境优先）
        climate_format = self._check_climate_format(month_zhi, wuxing_percent)
        if climate_format:
            result.update(climate_format)
            sub_format = self._get_monthly_format(month_zhi, month_gan, day_gan)
            if sub_format:
                result['sub_format'] = sub_format
            return result
        
        # 第三优先级：月令格局（标准框架）
        monthly_format = self._check_monthly_format(month_zhi, month_gan, day_gan, sizhu)
        if monthly_format:
            result.update(monthly_format)
            return result
        
        # 第四优先级：普通扶抑格局（基础平衡）
        basic_format = self._check_basic_format(yin_bi_power, ke_xie_hao_power)
        result.update(basic_format)
        
        return result

    def _get_yin_bi_power(self, shishen_weights):
        """计算印比力量"""
        yin_bi_list = ['正印', '偏印', '比肩', '劫财']
        return sum(shishen_weights.get(s, 0) for s in yin_bi_list)
    
    def _get_ke_xie_hao_power(self, shishen_weights):
        """计算克泄耗力量"""
        ke_xie_hao_list = ['正官', '七杀', '食神', '伤官', '正财', '偏财']
        return sum(shishen_weights.get(s, 0) for s in ke_xie_hao_list)

    def _check_special_format(self, sizhu, wuxing_percent, shishen_weights):
        """检查特殊格局（从格）"""
        day_gan = sizhu['日柱'][0]
        month_zhi = sizhu['月柱'][1]
        
        # 判断日主是否失令
        is_shi_ling = self._is_day_lord_weak_season(day_gan, month_zhi)
        
        # 判断是否无根（日支和其他地支中没有强根）
        is_no_root = self._is_no_root(sizhu, day_gan)
        
        # 计算印比力量占比
        yin_bi_power = self._get_yin_bi_power(shishen_weights)
        total_power = sum(shishen_weights.values())
        yin_bi_percent = (yin_bi_power / total_power * 100) if total_power > 0 else 0
        
        # 基础从格条件
        if is_shi_ling and is_no_root and yin_bi_percent < 10:
            
            # 1.1 从财格
            cai_power = shishen_weights.get('正财', 0) + shishen_weights.get('偏财', 0)
            cai_percent = (cai_power / total_power * 100) if total_power > 0 else 0
            if cai_percent > 70:
                return {
                    'main_format': '从财格',
                    'xi_shen': ['食神', '伤官', '正财', '偏财'],
                    'yong_shen': ['正财', '偏财'],
                    'ji_shen': ['正印', '偏印', '比肩', '劫财'],
                    'analysis': f'日主失令无根，印比力量极弱({yin_bi_percent:.1f}%)，财星力量极强({cai_percent:.1f}%)，从财星之势。'
                }
            
            # 1.2 从官杀格
            guan_sha_power = shishen_weights.get('正官', 0) + shishen_weights.get('七杀', 0)
            guan_sha_percent = (guan_sha_power / total_power * 100) if total_power > 0 else 0
            if guan_sha_percent > 70:
                return {
                    'main_format': '从官杀格',
                    'xi_shen': ['正财', '偏财', '正官', '七杀'],
                    'yong_shen': ['正官', '七杀'],
                    'ji_shen': ['食神', '伤官', '正印', '偏印', '比肩', '劫财'],
                    'analysis': f'日主失令无根，印比力量极弱({yin_bi_percent:.1f}%)，官杀力量极强({guan_sha_percent:.1f}%)，从官杀之势。'
                }
            
            # 1.3 从儿格
            shi_shang_power = shishen_weights.get('食神', 0) + shishen_weights.get('伤官', 0)
            shi_shang_percent = (shi_shang_power / total_power * 100) if total_power > 0 else 0
            if shi_shang_percent > 70:
                return {
                    'main_format': '从儿格',
                    'xi_shen': ['正财', '偏财', '食神', '伤官'],
                    'yong_shen': ['食神', '伤官'],
                    'ji_shen': ['正印', '偏印', '比肩', '劫财'],
                    'analysis': f'日主失令无根，印比力量极弱({yin_bi_percent:.1f}%)，食伤力量极强({shi_shang_percent:.1f}%)，从食伤之势。'
                }
        
        # 判断从强格
        is_de_ling = self._is_day_lord_strong_season(day_gan, month_zhi)
        has_root = self._has_strong_root(sizhu, day_gan)
        
        ke_xie_hao_power = self._get_ke_xie_hao_power(shishen_weights)
        ke_xie_hao_percent = (ke_xie_hao_power / total_power * 100) if total_power > 0 else 0
        
        if is_de_ling and has_root and yin_bi_percent > 80 and ke_xie_hao_percent < 20:
            yin_power = shishen_weights.get('正印', 0) + shishen_weights.get('偏印', 0)
            bi_power = shishen_weights.get('比肩', 0) + shishen_weights.get('劫财', 0)
            
            # 1.4 从印格
            if yin_power > bi_power:
                return {
                    'main_format': '从印格',
                    'xi_shen': ['比肩', '劫财', '正印', '偏印'],
                    'yong_shen': ['正印', '偏印'],
                    'ji_shen': ['正财', '偏财', '正官', '七杀', '食神', '伤官'],
                    'analysis': f'日主得令有根，官财食伤极弱({ke_xie_hao_percent:.1f}%)，印星力量最强，从印星之势。'
                }
            
            # 1.5 从旺格
            else:
                return {
                    'main_format': '从旺格',
                    'xi_shen': ['正印', '偏印', '比肩', '劫财'],
                    'yong_shen': ['比肩', '劫财'],
                    'ji_shen': ['正官', '七杀', '正财', '偏财', '食神', '伤官'],
                    'analysis': f'日主得令有根，官财食伤极弱({ke_xie_hao_percent:.1f}%)，比劫力量最强，从比劫之势。'
                }
        
        return None

    def _check_climate_format(self, month_zhi, wuxing_percent):
        """检查调候格局"""
        # 2.1 寒性命局
        if month_zhi in ['亥', '子', '丑'] and wuxing_percent.get('火', 0) < 10:
            return {
                'main_format': '寒性命局',
                'xi_shen': ['木'],
                'yong_shen': ['火'],
                'ji_shen': ['水', '金'],
                'analysis': f'生于{month_zhi}月，命局中火之力极弱({wuxing_percent.get("火", 0):.1f}%)，需要调候用火。'
            }
        
        # 2.2 燥性命局
        if month_zhi in ['巳', '午', '未'] and wuxing_percent.get('水', 0) < 10:
            return {
                'main_format': '燥性命局',
                'xi_shen': ['金'],
                'yong_shen': ['水'],
                'ji_shen': ['火', '土'],
                'analysis': f'生于{month_zhi}月，命局中水之力极弱({wuxing_percent.get("水", 0):.1f}%)，需要调候用水。'
            }
        
        return None

    def _check_monthly_format(self, month_zhi, month_gan, day_gan, sizhu):
        """检查月令格局"""
        # 获取月支对日干的十神
        month_shishen = self.shishen_map[day_gan][self.dizhi_canggan[month_zhi][0]]
        
        # 检查是否透干（月干是否为月支本气或相关十神）
        is_tou_gan = self._check_tou_gan(month_gan, month_zhi, day_gan)
        
        if not is_tou_gan:
            return None
            
        format_map = {
            '正官': {
                'main_format': '正官格',
                'xi_shen': ['正财', '偏财'],
                'yong_shen': ['正官'],
                'ji_shen': ['伤官', '七杀'],
                'analysis': '月令正官透干成格，以财生官为喜，忌伤官坏印、七杀混官。'
            },
            '七杀': {
                'main_format': '七杀格',
                'xi_shen': ['食神', '伤官', '正印', '偏印'],
                'yong_shen': ['食神', '伤官', '正印', '偏印'],
                'ji_shen': ['正财', '偏财'],
                'analysis': '月令七杀透干成格，食伤制杀或印化杀为用，忌财生杀。'
            },
            '正财': {
                'main_format': '正财格',
                'xi_shen': ['食神', '伤官', '正官', '七杀'],
                'yong_shen': ['正财'],
                'ji_shen': ['比肩', '劫财'],
                'analysis': '月令正财透干成格，食伤生财、官护财为喜，忌比劫夺财。'
            },
            '偏财': {
                'main_format': '偏财格',
                'xi_shen': ['食神', '伤官', '正官', '七杀'],
                'yong_shen': ['偏财'],
                'ji_shen': ['比肩', '劫财'],
                'analysis': '月令偏财透干成格，食伤生财、官护财为喜，忌比劫夺财。'
            },
            '正印': {
                'main_format': '正印格',
                'xi_shen': ['正官', '七杀', '比肩', '劫财'],
                'yong_shen': ['正印'],
                'ji_shen': ['正财', '偏财'],
                'analysis': '月令正印透干成格，官杀生印、比劫泄印为喜，忌财破印。'
            },
            '偏印': {
                'main_format': '偏印格',
                'xi_shen': ['比肩', '劫财'],
                'yong_shen': ['偏印'],
                'ji_shen': ['正财', '偏财', '食神', '伤官'],
                'analysis': '月令偏印透干成格，比劫泄印为喜，忌财破印、食神被夺。'
            },
            '食神': {
                'main_format': '食神格',
                'xi_shen': ['比肩', '劫财', '正财', '偏财'],
                'yong_shen': ['食神'],
                'ji_shen': ['偏印'],
                'analysis': '月令食神透干成格，比劫生食神、食神生财为喜，最忌枭神夺食。'
            },
            '伤官': {
                'main_format': '伤官格',
                'xi_shen': ['正财', '偏财'],
                'yong_shen': ['伤官'],
                'ji_shen': ['正官'],
                'analysis': '月令伤官透干成格，伤官生财为喜，最忌伤官见官。'
            }
        }
        
        # 检查建禄格和羊刃格
        changsheng = self.changsheng_state[day_gan][month_zhi]
        if changsheng == '临官':
            return {
                'main_format': '建禄格',
                'xi_shen': ['正官', '七杀', '正财', '偏财', '食神', '伤官'],
                'yong_shen': ['正官', '七杀'],
                'ji_shen': ['正印', '偏印', '比肩', '劫财'],
                'analysis': '月令为日主临官禄地，身旺需要官杀约束或食伤财星泄秀。'
            }
        elif changsheng == '帝旺':
            return {
                'main_format': '羊刃格',
                'xi_shen': ['七杀', '食神', '伤官', '正财', '偏财'],
                'yong_shen': ['七杀'],
                'ji_shen': ['正官', '正印', '偏印', '比肩', '劫财'],
                'analysis': '月令为日主帝旺羊刃地，身旺刃强，最喜七杀制刃。'
            }
        
        return format_map.get(month_shishen)

    def _check_basic_format(self, yin_bi_power, ke_xie_hao_power):
        """检查基础扶抑格局"""
        if yin_bi_power > ke_xie_hao_power:
            return {
                'main_format': '身旺格',
                'xi_shen': ['食神', '伤官', '正财', '偏财'],
                'yong_shen': ['正官', '七杀'],
                'ji_shen': ['正印', '偏印', '比肩', '劫财'],
                'analysis': f'生扶之力({yin_bi_power:.2f}) > 克泄耗之力({ke_xie_hao_power:.2f})，身旺喜泄耗，用官杀约束。'
            }
        else:
            return {
                'main_format': '身弱格',
                'xi_shen': ['正印', '偏印'],
                'yong_shen': ['比肩', '劫财'],
                'ji_shen': ['正官', '七杀', '食神', '伤官', '正财', '偏财'],
                'analysis': f'生扶之力({yin_bi_power:.2f}) < 克泄耗之力({ke_xie_hao_power:.2f})，身弱需要印比扶助。'
            }

    def _is_day_lord_weak_season(self, day_gan, month_zhi):
        """判断日主是否失令"""
        changsheng = self.changsheng_state[day_gan][month_zhi]
        weak_states = ['病', '死', '墓', '绝', '胎']
        return changsheng in weak_states

    def _is_day_lord_strong_season(self, day_gan, month_zhi):
        """判断日主是否得令"""
        changsheng = self.changsheng_state[day_gan][month_zhi]
        strong_states = ['临官', '帝旺', '长生']
        return changsheng in strong_states

    def _is_no_root(self, sizhu, day_gan):
        """判断日主是否无根"""
        # 简化判断：检查地支中是否有同类五行
        day_wuxing = self.tiangan_wuxing[day_gan]
        zhi_list = [sizhu['年柱'][1], sizhu['月柱'][1], sizhu['日柱'][1], sizhu['时柱'][1]]
        
        for zhi in zhi_list:
            if self.dizhi_wuxing[zhi] == day_wuxing:
                return False
            # 检查藏干
            for gan in self.dizhi_canggan[zhi]:
                if self.tiangan_wuxing[gan] == day_wuxing:
                    return False
        return True

    def _has_strong_root(self, sizhu, day_gan):
        """判断日主是否有强根"""
        day_wuxing = self.tiangan_wuxing[day_gan]
        strong_root_count = 0
        
        zhi_list = [sizhu['年柱'][1], sizhu['月柱'][1], sizhu['日柱'][1], sizhu['时柱'][1]]
        for zhi in zhi_list:
            if self.dizhi_wuxing[zhi] == day_wuxing:
                strong_root_count += 1
            # 检查藏干中的本气
            if self.dizhi_canggan[zhi][0] == day_gan:
                strong_root_count += 1
                
        return strong_root_count >= 2

    def _check_tou_gan(self, month_gan, month_zhi, day_gan):
        """检查月令是否透干"""
        # 获取月支藏干
        canggan_list = self.dizhi_canggan[month_zhi]
        
        # 月干是否为月支藏干之一
        if month_gan in canggan_list:
            return True
            
        # 月干是否与月支本气形成特定十神关系
        month_bengqi = canggan_list[0]
        month_shishen = self.shishen_map[day_gan][month_bengqi]
        month_gan_shishen = self.shishen_map[day_gan][month_gan]
        
        # 如果月干十神与月支本气十神相关（同类）
        related_shishen = {
            '正官': ['正官'], '七杀': ['七杀'],
            '正财': ['正财', '偏财'], '偏财': ['正财', '偏财'],
            '正印': ['正印', '偏印'], '偏印': ['正印', '偏印'],
            '食神': ['食神', '伤官'], '伤官': ['食神', '伤官'],
            '比肩': ['比肩', '劫财'], '劫财': ['比肩', '劫财']
        }
        
        for key, value_list in related_shishen.items():
            if month_shishen == key and month_gan_shishen in value_list:
                return True
                
        return False

    def _get_monthly_format(self, month_zhi, month_gan, day_gan):
        """获取月令格局标签"""
        month_bengqi = self.dizhi_canggan[month_zhi][0]
        month_shishen = self.shishen_map[day_gan][month_bengqi]
        
        changsheng = self.changsheng_state[day_gan][month_zhi]
        if changsheng == '临官':
            return '建禄'
        elif changsheng == '帝旺':
            return '羊刃'
        
        shishen_to_format = {
            '正官': '正官', '七杀': '七杀',
            '正财': '正财', '偏财': '偏财',
            '正印': '正印', '偏印': '偏印',
            '食神': '食神', '伤官': '伤官'
        }
        
        return shishen_to_format.get(month_shishen, '')

    def get_lucky_attributes(self, xi_shen_list, yong_shen_list):
        """根据喜神用神计算幸运属性"""
        # 将十神转换为对应的五行
        shishen_to_wuxing = {
            '正印': '水', '偏印': '水',  # 生日主的
            '比肩': '木', '劫财': '木',  # 同日主的（这里假设日主是木）
            '食神': '火', '伤官': '火',  # 日主生的
            '正财': '土', '偏财': '土',  # 日主克的
            '正官': '金', '七杀': '金'   # 克日主的
        }

        # 收集喜神用神对应的五行
        wuxing_set = set()
        for shishen in xi_shen_list + yong_shen_list:
            if shishen in shishen_to_wuxing:
                wuxing_set.add(shishen_to_wuxing[shishen])

        # 计算幸运属性
        lucky_colors = []
        lucky_directions = []
        lucky_numbers = []
        lucky_wuxing = []

        for wuxing in wuxing_set:
            if wuxing in self.wuxing_attributes:
                attrs = self.wuxing_attributes[wuxing]
                lucky_colors.append(attrs['衍生色'])
                lucky_directions.extend(attrs['方位'])
                lucky_numbers.extend(attrs['数字'])
                lucky_wuxing.append(wuxing)

        # 去重并排序
        lucky_colors = list(set(lucky_colors))
        lucky_directions = list(set(lucky_directions))
        lucky_numbers = sorted(list(set(lucky_numbers)))
        lucky_wuxing = list(set(lucky_wuxing))

        return {
            '喜用属性': '、'.join(lucky_wuxing),
            '幸运颜色': '、'.join(lucky_colors),
            '幸运方位': '、'.join(lucky_directions),
            '幸运数字': '、'.join(map(str, lucky_numbers))
        }

    def convert_shishen_to_wuxing(self, shishen_list, day_gan):
        """将十神转换为对应的五行属性"""
        day_wuxing = self.tiangan_wuxing[day_gan]

        # 根据日主五行确定十神对应的五行
        wuxing_relations = {
            '木': {
                '正印': '水', '偏印': '水',  # 生木
                '比肩': '木', '劫财': '木',  # 同木
                '食神': '火', '伤官': '火',  # 木生火
                '正财': '土', '偏财': '土',  # 木克土
                '正官': '金', '七杀': '金'   # 金克木
            },
            '火': {
                '正印': '木', '偏印': '木',  # 生火
                '比肩': '火', '劫财': '火',  # 同火
                '食神': '土', '伤官': '土',  # 火生土
                '正财': '金', '偏财': '金',  # 火克金
                '正官': '水', '七杀': '水'   # 水克火
            },
            '土': {
                '正印': '火', '偏印': '火',  # 生土
                '比肩': '土', '劫财': '土',  # 同土
                '食神': '金', '伤官': '金',  # 土生金
                '正财': '水', '偏财': '水',  # 土克水
                '正官': '木', '七杀': '木'   # 木克土
            },
            '金': {
                '正印': '土', '偏印': '土',  # 生金
                '比肩': '金', '劫财': '金',  # 同金
                '食神': '水', '伤官': '水',  # 金生水
                '正财': '木', '偏财': '木',  # 金克木
                '正官': '火', '七杀': '火'   # 火克金
            },
            '水': {
                '正印': '金', '偏印': '金',  # 生水
                '比肩': '水', '劫财': '水',  # 同水
                '食神': '木', '伤官': '木',  # 水生木
                '正财': '火', '偏财': '火',  # 水克火
                '正官': '土', '七杀': '土'   # 土克水
            }
        }

        wuxing_list = []
        if day_wuxing in wuxing_relations:
            relations = wuxing_relations[day_wuxing]
            for shishen in shishen_list:
                if shishen in relations:
                    wuxing_list.append(relations[shishen])

        return list(set(wuxing_list))  # 去重

    def format_mingge_result(self, result, day_gan=None):
        """格式化命格分析结果为文本输出，包括幸运属性"""
        output = []

        # 格局类型
        if result['sub_format']:
            output.append(f"格局类型：{result['main_format']}（{result['sub_format']}）")
        else:
            output.append(f"格局类型：{result['main_format']}")

        # 格局分析
        if result['analysis']:
            output.append(f"格局分析：{result['analysis']}")

        # 喜神
        if result['xi_shen']:
            output.append(f"喜神：{' '.join(result['xi_shen'])}")

        # 用神
        if result['yong_shen']:
            output.append(f"用神：{' '.join(result['yong_shen'])}")

        # 忌神
        if result['ji_shen']:
            output.append(f"忌神：{' '.join(result['ji_shen'])}")

        # 添加幸运属性信息（如果提供了日干）
        if day_gan and result['xi_shen'] and result['yong_shen']:
            # 将十神转换为五行
            xi_wuxing = self.convert_shishen_to_wuxing(result['xi_shen'], day_gan)
            yong_wuxing = self.convert_shishen_to_wuxing(result['yong_shen'], day_gan)
            all_wuxing = list(set(xi_wuxing + yong_wuxing))

            if all_wuxing:
                # 计算幸运属性
                lucky_colors = []
                lucky_directions = []
                lucky_numbers = []

                for wuxing in all_wuxing:
                    if wuxing in self.wuxing_attributes:
                        attrs = self.wuxing_attributes[wuxing]
                        lucky_colors.append(attrs['衍生色'])
                        lucky_directions.extend(attrs['方位'])
                        lucky_numbers.extend(attrs['数字'])

                # 去重并格式化
                if all_wuxing:
                    output.append(f"喜用属性：{'、'.join(all_wuxing)}")
                if lucky_colors:
                    output.append(f"幸运颜色：{'、'.join(list(set(lucky_colors)))}")
                if lucky_directions:
                    unique_directions = []
                    # 只保留用神对应的方位（根据需求调整）
                    yong_directions = []
                    for wuxing in yong_wuxing:
                        if wuxing in self.wuxing_attributes:
                            yong_directions.extend(self.wuxing_attributes[wuxing]['方位'])
                    if yong_directions:
                        output.append(f"幸运方位：{'、'.join(list(set(yong_directions)))}")
                if lucky_numbers:
                    sorted_numbers = sorted(list(set(lucky_numbers)))
                    output.append(f"幸运数字：{'、'.join(map(str, sorted_numbers))}")

        return '\n'.join(output)