"""
五行计算模块
实现五行力量计算，包括藏干、旺度、生扶克制等计算
"""

import json


class WuxingCalculator:
    def __init__(self, config_path="config.json"):
        """初始化五行计算器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 天干五行阴阳属性
        self.tiangan_info = {
            '甲': {'五行': '木', '阴阳': '阳', '编码': 1},
            '乙': {'五行': '木', '阴阳': '阴', '编码': 0},
            '丙': {'五行': '火', '阴阳': '阳', '编码': 1},
            '丁': {'五行': '火', '阴阳': '阴', '编码': 0},
            '戊': {'五行': '土', '阴阳': '阳', '编码': 1},
            '己': {'五行': '土', '阴阳': '阴', '编码': 0},
            '庚': {'五行': '金', '阴阳': '阳', '编码': 1},
            '辛': {'五行': '金', '阴阳': '阴', '编码': 0},
            '壬': {'五行': '水', '阴阳': '阳', '编码': 1},
            '癸': {'五行': '水', '阴阳': '阴', '编码': 0}
        }
        
        # 地支五行阴阳属性和藏干 - 使用config配置的权重
        self.dizhi_info = self._build_dizhi_info_with_config()
        
        # 五行相生相克关系
        self.wuxing_sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        self.wuxing_ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}

        # 五行生克反向映射（谁生我，谁克我）
        self.wuxing_sheng_reverse = {'火': '木', '土': '火', '金': '土', '水': '金', '木': '水'}
        self.wuxing_ke_reverse = {'土': '木', '水': '土', '火': '水', '金': '火', '木': '金'}
        
        # 季节对应的五行旺度
        self.season_wangdu = {
            '春': {'旺': '木', '相': '火', '死': '土', '囚': '金', '休': '水'},
            '夏': {'旺': '火', '相': '土', '死': '金', '囚': '水', '休': '木'},
            '秋': {'旺': '金', '相': '水', '死': '木', '囚': '火', '休': '土'},
            '冬': {'旺': '水', '相': '木', '死': '火', '囚': '土', '休': '金'},
            '季末': {'旺': '土', '相': '金', '死': '水', '囚': '木', '休': '火'}
        }

        # 《滴天髓》五行旺衰状态表 - "XX盛XX藏"风格
        self.wangshui_patterns = {
            # 旺极状态 (某五行>50%且似五行<10%)
            '木': {
                '旺极': {
                    '金': {'name': '木盛金藏', 'description': '木旺极似金，坚硬如金，需炼化或疏泄', 'use_god': ['火', '土'], 'post_desc': '泄日主（火）、耗日主（土）'},
                    '火': {'name': '木盛火藏', 'description': '木旺极似火，烈焰般旺，需培土耗泄', 'use_god': ['土', '火'], 'post_desc': '耗日主（土）、泄日主（火）'}
                },
                '衰极': {
                    '水': {'name': '木衰水藏', 'description': '木衰极似水，柔弱如水，需生扶木气', 'use_god': ['水', '木'], 'post_desc': '调候日主（火）'},
                    '土': {'name': '木衰土藏', 'description': '木衰极似土，埋没如土，需火暖生', 'use_god': ['火', '水'], 'post_desc': '调候日主（火）'}
                },
                '中和': {'name': '木和无藏', 'description': '木力量均衡，无似五行，需调候或微调生克', 'use_god': ['水', '火'], 'post_desc': '调候日主（火、水）、泄日主（火）'}
            },
            '火': {
                '旺极': {
                    '土': {'name': '火盛土藏', 'description': '火旺极似土，燥热如土，需润泽制火', 'use_god': ['水', '木'], 'post_desc': '克日主（水）、泄日主（木）'},
                    '金': {'name': '火盛金藏', 'description': '火旺极似金，熔金之势，需水济助', 'use_god': ['水', '木'], 'post_desc': '克日主（水）、泄日主（木）'}
                },
                '衰极': {
                    '金': {'name': '火衰金藏', 'description': '火衰极似金，寒弱如金，需木生暖', 'use_god': ['木', '火'], 'post_desc': '调候日主（木）'},
                    '木': {'name': '火衰木藏', 'description': '火衰极似木，枯槁如木，需土培火', 'use_god': ['土', '木'], 'post_desc': '耗日主（土）'}
                },
                '中和': {'name': '火和无藏', 'description': '火力量均衡，无似五行，需调候或微调生克', 'use_god': ['木', '水'], 'post_desc': '调候日主（水、木）、克日主（水）'}
            },
            '土': {
                '旺极': {
                    '木': {'name': '土盛木藏', 'description': '土旺极似木，厚重如木，需伐制疏通', 'use_god': ['金', '木'], 'post_desc': '克日主（金）、疏通日主（木）'},
                    '金': {'name': '土盛金藏', 'description': '土旺极似金，金藏土中，需水洗涤', 'use_god': ['水', '金'], 'post_desc': '制化日主（水）、克日主（金）'}
                },
                '衰极': {
                    '火': {'name': '土衰火藏', 'description': '土衰极似火，焦弱如火，需水润生', 'use_god': ['水', '火'], 'post_desc': '调候日主（水）'},
                    '金': {'name': '土衰金藏', 'description': '土衰极似金，埋没如金，需木疏通', 'use_god': ['木', '水'], 'post_desc': '疏通日主（木）'}
                },
                '中和': {'name': '土和无藏', 'description': '土力量均衡，无似五行，需调候或微调生克', 'use_god': ['火', '金'], 'post_desc': '调候日主（水、金）、克日主（金）'}
            },
            '金': {
                '旺极': {
                    '火': {'name': '金盛火藏', 'description': '金旺极似火，熔炼如火，需水济助', 'use_god': ['水', '火'], 'post_desc': '制化日主（水）、泄日主（火）'},
                    '水': {'name': '金盛水藏', 'description': '金旺极似水，流动如水，需土止遏', 'use_god': ['土', '水'], 'post_desc': '耗日主（土）、泄日主（水）'}
                },
                '衰极': {
                    '土': {'name': '金衰土藏', 'description': '金衰极似土，湿弱如土，需火炼化', 'use_god': ['火', '土'], 'post_desc': '调候日主（火）'},
                    '木': {'name': '金衰木藏', 'description': '金衰极似木，枯涩如木，需水洗涤', 'use_god': ['水', '火'], 'post_desc': '制化日主（水）'}
                },
                '中和': {'name': '金和无藏', 'description': '金力量均衡，无似五行，需调候或微调生克', 'use_god': ['土', '水'], 'post_desc': '调候日主（火、水）、泄日主（水）'}
            },
            '水': {
                '旺极': {
                    '土': {'name': '水盛土藏', 'description': '水旺极似土，湿重如土，需木疏通', 'use_god': ['木', '土'], 'post_desc': '疏通日主（木）、克日主（土）'},
                    '木': {'name': '水盛木藏', 'description': '水旺极似木，生机如木，需金克伐', 'use_god': ['金', '木'], 'post_desc': '克日主（金）、泄日主（木）'}
                },
                '衰极': {
                    '金': {'name': '水衰金藏', 'description': '水衰极似金，枯竭如金，需土生扶', 'use_god': ['金', '水'], 'post_desc': '调候日主（土）'},
                    '火': {'name': '水衰火藏', 'description': '水衰极似火，蒸弱如火，需木疏通', 'use_god': ['木', '金'], 'post_desc': '疏通日主（木）'}
                },
                '中和': {'name': '水和无藏', 'description': '水力量均衡，无似五行，需调候或微调生克', 'use_god': ['金', '土'], 'post_desc': '调候日主（金、木）、克日主（土）'}
            }
        }

    def _build_dizhi_info_with_config(self):
        """根据config配置构建地支信息"""
        # 基础地支信息结构
        base_info = {
            '子': {'五行': '水', '阴阳': '阳', '藏干': ['癸']},
            '丑': {'五行': '土', '阴阳': '阴', '藏干': ['己', '癸', '辛']},
            '寅': {'五行': '木', '阴阳': '阳', '藏干': ['甲', '丙', '戊']},
            '卯': {'五行': '木', '阴阳': '阴', '藏干': ['乙']},
            '辰': {'五行': '土', '阴阳': '阳', '藏干': ['戊', '乙', '癸']},
            '巳': {'五行': '火', '阴阳': '阴', '藏干': ['丙', '戊', '庚']},
            '午': {'五行': '火', '阴阳': '阳', '藏干': ['丁', '己']},
            '未': {'五行': '土', '阴阳': '阴', '藏干': ['己', '丁', '乙']},
            '申': {'五行': '金', '阴阳': '阳', '藏干': ['庚', '壬', '戊']},
            '酉': {'五行': '金', '阴阳': '阴', '藏干': ['辛']},
            '戌': {'五行': '土', '阴阳': '阳', '藏干': ['戊', '辛', '丁']},
            '亥': {'五行': '水', '阴阳': '阴', '藏干': ['壬', '甲']}
        }

        # 从config获取权重配置
        canggan_config = self.config['藏干权重']

        # 构建带权重的地支信息
        result = {}
        for zhi, info in base_info.items():
            result[zhi] = {
                '五行': info['五行'],
                '阴阳': info['阴阳'],
                '藏干': {}
            }

            gans = info['藏干']
            if len(gans) == 1:
                # 只有本气
                result[zhi]['藏干'][gans[0]] = canggan_config['本气']
            elif len(gans) == 2:
                # 本气 + 中气
                result[zhi]['藏干'][gans[0]] = canggan_config['本气_中气']['本气']
                result[zhi]['藏干'][gans[1]] = canggan_config['本气_中气']['中气']
            elif len(gans) == 3:
                # 本气 + 中气 + 余气
                result[zhi]['藏干'][gans[0]] = canggan_config['本气_中气_余气']['本气']
                result[zhi]['藏干'][gans[1]] = canggan_config['本气_中气_余气']['中气']
                result[zhi]['藏干'][gans[2]] = canggan_config['本气_中气_余气']['余气']

        return result
    
    def get_season_from_month(self, month_zhi):
        """根据月支确定季节"""
        season_map = {
            '寅': '春', '卯': '春', '辰': '春',
            '巳': '夏', '午': '夏', '未': '夏', 
            '申': '秋', '酉': '秋', '戌': '秋',
            '亥': '冬', '子': '冬', '丑': '冬'
        }
        
        # 辰、未、戌、丑为季末土
        if month_zhi in ['辰', '未', '戌', '丑']:
            return '季末'
        
        return season_map.get(month_zhi, '春')
    
    def calculate_basic_wuxing_count(self, sizhu):
        """计算基础五行数量"""
        wuxing_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}

        # 统计天干
        for gan in [sizhu['年柱'][0], sizhu['月柱'][0], sizhu['日柱'][0], sizhu['时柱'][0]]:
            wuxing = self.tiangan_info[gan]['五行']
            wuxing_count[wuxing] += 1

        # 统计地支本气
        for zhi in [sizhu['年柱'][1], sizhu['月柱'][1], sizhu['日柱'][1], sizhu['时柱'][1]]:
            wuxing = self.dizhi_info[zhi]['五行']
            wuxing_count[wuxing] += 1

        return wuxing_count
    
    def calculate_canggan_contribution(self, sizhu):
        """计算藏干对五行的贡献"""
        canggan_contribution = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}

        for zhi in [sizhu['年柱'][1], sizhu['月柱'][1], sizhu['日柱'][1], sizhu['时柱'][1]]:
            canggan_dict = self.dizhi_info[zhi]['藏干']

            for gan, weight in canggan_dict.items():
                wuxing = self.tiangan_info[gan]['五行']
                canggan_contribution[wuxing] += weight

        return canggan_contribution
    
    def calculate_wuxing_scores(self, sizhu, lunar_info):
        """计算五行力量分数"""
        # 获取月支确定季节
        month_zhi = sizhu['月柱'][1]
        season = self.get_season_from_month(month_zhi)
        season_wangdu = self.season_wangdu[season]
        
        # 基础五行计数
        basic_count = self.calculate_basic_wuxing_count(sizhu)
        
        # 藏干贡献
        canggan_contrib = self.calculate_canggan_contribution(sizhu)
        
        # 获取配置参数
        deling_weight = self.config['五行计算参数']['得令权重']
        shiling_weight = self.config['五行计算参数']['失令权重']
        shengfu_coeff = self.config['五行计算参数']['生扶系数']
        kezhi_coeff = self.config['五行计算参数']['克制系数']
        
        # 计算每个五行的最终分数
        final_scores = {}
        
        for wuxing in ['木', '火', '土', '金', '水']:
            # 1. 基础分数 = 基础计数 + 藏干贡献
            base_score = basic_count[wuxing] + canggan_contrib[wuxing]
            
            # 2. 应用季节增益/减益
            if wuxing == season_wangdu['旺']:
                # 得令
                score = base_score * deling_weight
                status = '得令'
            elif wuxing == season_wangdu['死']:
                # 失令
                score = base_score * shiling_weight
                status = '失令'
            else:
                score = base_score
                status = '平和'
            
            # 3. 应用生扶增益
            sheng_wuxing = None
            for wx, sheng_target in self.wuxing_sheng.items():
                if sheng_target == wuxing:
                    sheng_wuxing = wx
                    break
            
            if sheng_wuxing:
                sheng_score = basic_count[sheng_wuxing] + canggan_contrib[sheng_wuxing]
                if sheng_score > 0:
                    shengfu_bonus = sheng_score * shengfu_coeff
                    score += shengfu_bonus
            
            # 4. 应用克制减益
            ke_wuxing = None
            for wx, ke_target in self.wuxing_ke.items():
                if ke_target == wuxing:
                    ke_wuxing = wx
                    break
            
            if ke_wuxing:
                ke_score = basic_count[ke_wuxing] + canggan_contrib[ke_wuxing]
                if ke_score > 0:
                    kezhi_penalty = ke_score * kezhi_coeff
                    score -= kezhi_penalty
            
            # 确保分数不为负
            score = max(0, score)
            
            # 判断强弱状态
            if score >= 4:
                strength_status = '过强'
            elif score >= 2.5:
                strength_status = '中和偏强'
            elif score >= 1.5:
                strength_status = '中和'
            elif score >= 0.8:
                strength_status = '偏弱'
            else:
                strength_status = '很弱'
            
            final_scores[wuxing] = {
                '力量值': round(score, 2),
                '状态': strength_status,
                '季节状态': status,
                '基础分数': round(base_score, 2)
            }
        
        # 添加滴天髓旺衰分析
        day_gan = sizhu['日柱'][0]
        day_wuxing = self.tiangan_info[day_gan]['五行']
        month_zhi = sizhu['月柱'][1]
        wangshui_analysis = self.analyze_wangshui_state(final_scores, day_wuxing, season)

        # 生成综合分析句式
        comprehensive_analysis = self.generate_comprehensive_analysis(
            day_gan, day_wuxing, season, month_zhi, wangshui_analysis, final_scores
        )

        return final_scores, season, wangshui_analysis, comprehensive_analysis

    def analyze_wangshui_state(self, wuxing_scores, day_wuxing, season):
        """分析五行旺衰状态 - 基于《滴天髓》理论"""
        # 计算力量百分比
        total_power = sum(score['力量值'] for score in wuxing_scores.values())
        if total_power == 0:
            return {'name': f'{day_wuxing}和无藏', 'description': '五行力量均衡', 'use_god': []}

        power_ratios = {wx: score['力量值'] / total_power for wx, score in wuxing_scores.items()}

        day_power = power_ratios[day_wuxing]
        max_power = max(power_ratios.values())
        min_power = min(power_ratios.values())

        # 1. 检查中和状态
        if (0.2 <= day_power <= 0.4 and max_power <= 0.3 and min_power >= 0.2):
            pattern_info = self.wangshui_patterns[day_wuxing]['中和']
            return {
                'name': pattern_info['name'],
                'description': pattern_info['description'],
                'use_god': pattern_info['use_god'],
                'post_desc': pattern_info['post_desc'],
                'power_ratio': day_power
            }

        # 2. 检查旺极状态 (日主>50%且某五行<10%)
        elif day_power > 0.5:
            for resemble_wx, ratio in power_ratios.items():
                if ratio < 0.1 and resemble_wx != day_wuxing and resemble_wx in self.wangshui_patterns[day_wuxing]['旺极']:
                    pattern_info = self.wangshui_patterns[day_wuxing]['旺极'][resemble_wx]
                    return {
                        'name': pattern_info['name'],
                        'description': pattern_info['description'],
                        'use_god': pattern_info['use_god'],
                        'post_desc': pattern_info['post_desc'],
                        'power_ratio': day_power,
                        'resemble_element': resemble_wx,
                        'resemble_ratio': ratio
                    }

        # 3. 检查衰极状态 (日主<20%且某五行>30%)
        elif day_power < 0.2:
            for resemble_wx, ratio in power_ratios.items():
                if ratio > 0.3 and resemble_wx != day_wuxing and resemble_wx in self.wangshui_patterns[day_wuxing]['衰极']:
                    pattern_info = self.wangshui_patterns[day_wuxing]['衰极'][resemble_wx]
                    return {
                        'name': pattern_info['name'],
                        'description': pattern_info['description'],
                        'use_god': pattern_info['use_god'],
                        'post_desc': pattern_info['post_desc'],
                        'power_ratio': day_power,
                        'resemble_element': resemble_wx,
                        'resemble_ratio': ratio
                    }

        # 4. 普通状态
        return {
            'name': f'{day_wuxing}普通',
            'description': f'{day_wuxing}五行力量适中',
            'use_god': [day_wuxing] if day_power < 0.3 else [],
            'post_desc': '生扶日主' if day_power < 0.3 else '调候日主',
            'power_ratio': day_power
        }

    def generate_comprehensive_analysis(self, day_gan, day_wuxing, season, month_zhi, wangshui_analysis, wuxing_scores):
        """生成综合分析句式"""
        # 获取月份中文名称
        month_names = {
            '子': '子月', '丑': '丑月', '寅': '寅月', '卯': '卯月',
            '辰': '辰月', '巳': '巳月', '午': '午月', '未': '未月',
            '申': '申月', '酉': '酉月', '戌': '戌月', '亥': '亥月'
        }

        # 季节中文名称
        season_names = {'春': '春天', '夏': '夏天', '秋': '秋天', '冬': '冬天', '季末': '季末'}

        # 构建基础句式
        basic_info = f"日主为{day_gan}{day_wuxing}，五行属{day_wuxing}，生于{season_names.get(season, season)}{month_names.get(month_zhi, month_zhi)}"

        # 旺衰状态描述
        wangshui_desc = wangshui_analysis['name']
        post_desc = wangshui_analysis.get('post_desc', '')

        # 分析五行强弱分布
        total_power = sum(score['力量值'] for score in wuxing_scores.values())
        power_ratios = {wx: score['力量值'] / total_power for wx, score in wuxing_scores.items()}

        # 根据力量占比分类五行
        strong_elements = []  # >25%
        weak_elements = []    # <15%
        medium_elements = []  # 15%-25%

        for wx, ratio in power_ratios.items():
            if ratio > 0.25:
                strong_elements.append(wx)
            elif ratio < 0.15:
                weak_elements.append(wx)
            else:
                medium_elements.append(wx)

        # 构建五行强弱描述
        wuxing_strength_desc = "八字"
        if strong_elements:
            wuxing_strength_desc += f"『{'、'.join(strong_elements)}』旺"
        if weak_elements:
            if strong_elements:
                wuxing_strength_desc += "，"
            wuxing_strength_desc += f"『{'、'.join(weak_elements)}』弱"
        if not strong_elements and not weak_elements and medium_elements:
            wuxing_strength_desc += "五行相对平衡"

        # 组合完整句式
        comprehensive_analysis = f"{basic_info}，{wangshui_desc}，{post_desc}。{wuxing_strength_desc}。"

        return comprehensive_analysis

    def format_wuxing_output(self, wuxing_scores, season, wangshui_analysis=None, comprehensive_analysis=None):
        """格式化五行输出结果"""
        output = f"""
=== 五行力量分析结果 ===
当前季节：{season}

五行力量分布：
"""
        for wuxing, info in wuxing_scores.items():
            output += f"{wuxing}：{info['力量值']} ({info['状态']}, {info['季节状态']})\n"

        # 添加《滴天髓》旺衰状态分析
        if wangshui_analysis:
            output += f"\n旺衰状态：{wangshui_analysis['name']}"
            if wangshui_analysis.get('description'):
                output += f"\n状态解释：{wangshui_analysis['description']}"
            if wangshui_analysis.get('use_god'):
                use_god_str = '、'.join(wangshui_analysis['use_god'])
                output += f"\n建议用神：{use_god_str}"

        # 添加综合分析句式
        if comprehensive_analysis:
            output += f"\n\n综合分析：{comprehensive_analysis}"

        return output


# 测试函数
def test_wuxing_calculator():
    """测试五行计算模块"""
    from calendar_converter import CalendarConverter
    
    # 先获取四柱信息
    converter = CalendarConverter()
    result = converter.process_birth_info(
        birth_year=1991,
        birth_month=5,
        birth_day=25,
        birth_hour=15,
        birth_minute=00,
        city_name="广州",
        name="测试用户"
    )
    
    # 计算五行
    calculator = WuxingCalculator()
    wuxing_scores, season, wangshui_analysis, comprehensive_analysis = calculator.calculate_wuxing_scores(
        result['四柱'],
        result['阴历信息']
    )

    print(calculator.format_wuxing_output(wuxing_scores, season, wangshui_analysis, comprehensive_analysis))
    return wuxing_scores


if __name__ == "__main__":
    test_wuxing_calculator()
