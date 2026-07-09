"""
排盘详细信息计算模块
包含主星、副星、星运、自坐、空亡、纳音、神煞等详细信息
"""

import json

class PaipanDetailCalculator:
    def __init__(self, config_path="config.json"):
        """初始化排盘详细计算器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 十天干生旺死绝表
        self.shengwang_table = {
            '亥': {'甲': '长生', '丙': '绝', '戊': '绝', '庚': '病', '壬': '临官', '乙': '死', '丁': '胎', '己': '胎', '辛': '沐浴', '癸': '帝旺'},
            '子': {'甲': '沐浴', '丙': '胎', '戊': '胎', '庚': '死', '壬': '帝旺', '乙': '长生', '丁': '绝', '己': '绝', '辛': '长生', '癸': '临官'},
            '丑': {'甲': '冠带', '丙': '养', '戊': '养', '庚': '墓', '壬': '衰', '乙': '败', '丁': '墓', '己': '墓', '辛': '养', '癸': '冠带'},
            '寅': {'甲': '临官', '丙': '长生', '戊': '长生', '庚': '绝', '壬': '病', '乙': '临官', '丁': '沐浴', '己': '沐浴', '辛': '绝', '癸': '衰'},
            '卯': {'甲': '帝旺', '丙': '沐浴', '戊': '沐浴', '庚': '胎', '壬': '死', '乙': '帝旺', '丁': '长生', '己': '长生', '辛': '胎', '癸': '病'},
            '辰': {'甲': '衰', '丙': '冠带', '戊': '冠带', '庚': '养', '壬': '墓', '乙': '衰', '丁': '冠带', '己': '冠带', '辛': '养', '癸': '墓'},
            '巳': {'甲': '病', '丙': '临官', '戊': '临官', '庚': '长生', '壬': '绝', '乙': '病', '丁': '临官', '己': '临官', '辛': '长生', '癸': '绝'},
            '午': {'甲': '死', '丙': '帝旺', '戊': '帝旺', '庚': '沐浴', '壬': '胎', '乙': '死', '丁': '帝旺', '己': '帝旺', '辛': '沐浴', '癸': '胎'},
            '未': {'甲': '墓', '丙': '衰', '戊': '衰', '庚': '冠带', '壬': '养', '乙': '墓', '丁': '衰', '己': '衰', '辛': '冠带', '癸': '养'},
            '申': {'甲': '绝', '丙': '病', '戊': '病', '庚': '临官', '壬': '长生', '乙': '绝', '丁': '病', '己': '病', '辛': '临官', '癸': '长生'},
            '酉': {'甲': '胎', '丙': '死', '戊': '死', '庚': '帝旺', '壬': '沐浴', '乙': '胎', '丁': '死', '己': '死', '辛': '帝旺', '癸': '沐浴'},
            '戌': {'甲': '养', '丙': '墓', '戊': '墓', '庚': '衰', '壬': '冠带', '乙': '养', '丁': '墓', '己': '墓', '辛': '衰', '癸': '冠带'}
        }
        
        # 空亡（旬空）表
        self.kongwang_table = {
            '甲子': ['戌', '亥'], '乙丑': ['戌', '亥'], '丙寅': ['戌', '亥'], '丁卯': ['戌', '亥'], '戊辰': ['戌', '亥'],
            '己巳': ['戌', '亥'], '庚午': ['戌', '亥'], '辛未': ['戌', '亥'], '壬申': ['戌', '亥'], '癸酉': ['戌', '亥'],
            '甲戌': ['申', '酉'], '乙亥': ['申', '酉'], '丙子': ['申', '酉'], '丁丑': ['申', '酉'], '戊寅': ['申', '酉'],
            '己卯': ['申', '酉'], '庚辰': ['申', '酉'], '辛巳': ['申', '酉'], '壬午': ['申', '酉'], '癸未': ['申', '酉'],
            '甲申': ['午', '未'], '乙酉': ['午', '未'], '丙戌': ['午', '未'], '丁亥': ['午', '未'], '戊子': ['午', '未'],
            '己丑': ['午', '未'], '庚寅': ['午', '未'], '辛卯': ['午', '未'], '壬辰': ['午', '未'], '癸巳': ['午', '未'],
            '甲午': ['辰', '巳'], '乙未': ['辰', '巳'], '丙申': ['辰', '巳'], '丁酉': ['辰', '巳'], '戊戌': ['辰', '巳'],
            '己亥': ['辰', '巳'], '庚子': ['辰', '巳'], '辛丑': ['辰', '巳'], '壬寅': ['辰', '巳'], '癸卯': ['辰', '巳'],
            '甲辰': ['寅', '卯'], '乙巳': ['寅', '卯'], '丙午': ['寅', '卯'], '丁未': ['寅', '卯'], '戊申': ['寅', '卯'],
            '己酉': ['寅', '卯'], '庚戌': ['寅', '卯'], '辛亥': ['寅', '卯'], '壬子': ['寅', '卯'], '癸丑': ['寅', '卯'],
            '甲寅': ['子', '丑'], '乙卯': ['子', '丑'], '丙辰': ['子', '丑'], '丁巳': ['子', '丑'], '戊午': ['子', '丑'],
            '己未': ['子', '丑'], '庚申': ['子', '丑'], '辛酉': ['子', '丑'], '壬戌': ['子', '丑'], '癸亥': ['子', '丑']
        }
        
        # 纳音表
        self.nayin_table = {
            '甲子': '海中金', '乙丑': '海中金', '丙寅': '炉中火', '丁卯': '炉中火', '戊辰': '大林木', '己巳': '大林木',
            '庚午': '路旁土', '辛未': '路旁土', '壬申': '剑锋金', '癸酉': '剑锋金', '甲戌': '山头火', '乙亥': '山头火',
            '丙子': '涧下水', '丁丑': '涧下水', '戊寅': '城头土', '己卯': '城头土', '庚辰': '白蜡金', '辛巳': '白蜡金',
            '壬午': '杨柳木', '癸未': '杨柳木', '甲申': '泉中水', '乙酉': '泉中水', '丙戌': '屋上土', '丁亥': '屋上土',
            '戊子': '霹雳火', '己丑': '霹雳火', '庚寅': '松柏木', '辛卯': '松柏木', '壬辰': '长流水', '癸巳': '长流水',
            '甲午': '沙中金', '乙未': '沙中金', '丙申': '山下火', '丁酉': '山下火', '戊戌': '平地木', '己亥': '平地木',
            '庚子': '壁上土', '辛丑': '壁上土', '壬寅': '金箔金', '癸卯': '金箔金', '甲辰': '覆灯火', '乙巳': '覆灯火',
            '丙午': '天河水', '丁未': '天河水', '戊申': '大驿土', '己酉': '大驿土', '庚戌': '钗钏金', '辛亥': '钗钏金',
            '壬子': '桑柘木', '癸丑': '桑柘木', '甲寅': '大溪水', '乙卯': '大溪水', '丙辰': '沙中土', '丁巳': '沙中土',
            '戊午': '天上火', '己未': '天上火', '庚申': '石榴木', '辛酉': '石榴木', '壬戌': '大海水', '癸亥': '大海水'
        }
        
        # 神煞查询表（主类型）
        self.shensha_table = {
            '天乙贵人': {
                '甲': ['丑', '未'], '戊': ['丑', '未'], '庚': ['丑', '未'],
                '乙': ['子', '申'], '己': ['子', '申'],
                '丙': ['亥', '酉'], '丁': ['亥', '酉'],
                '壬': ['巳', '卯'], '癸': ['巳', '卯'],
                '辛': ['寅', '午']
            },
            '太极贵人': {
                '甲': ['子', '午'], '乙': ['子', '午'],
                '丙': ['卯', '酉'], '丁': ['卯', '酉'],
                '戊': ['辰', '戌', '丑', '未'], '己': ['辰', '戌', '丑', '未'],
                '庚': ['寅', '亥'], '辛': ['寅', '亥'],
                '壬': ['巳', '申'], '癸': ['巳', '申']
            },
            '文昌贵人': {
                '甲': ['巳'], '乙': ['午'], '丙': ['申'], '丁': ['酉'],
                '戊': ['申'], '己': ['酉'], '庚': ['亥'], '辛': ['子'],
                '壬': ['寅'], '癸': ['卯']
            },
            '桃花': {
                '申子辰': '酉', '寅午戌': '卯', '巳酉丑': '午', '亥卯未': '子'
            },
            '华盖': {
                '申子辰': '辰', '寅午戌': '戌', '巳酉丑': '丑', '亥卯未': '未'
            },
            '驿马': {
                '申子辰': '寅', '寅午戌': '申', '巳酉丑': '亥', '亥卯未': '巳'
            },
            '羊刃': {
                '甲': '卯', '乙': '寅', '丙': '午', '丁': '巳', '戊': '午',
                '己': '巳', '庚': '酉', '辛': '申', '壬': '子', '癸': '亥'
            },
            '禄神': {
                '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午', '戊': '巳',
                '己': '午', '庚': '申', '辛': '酉', '壬': '亥', '癸': '子'
            }
        }

    def calculate_main_star(self, day_gan):
        """计算日柱主星"""
        yang_gan = ['甲', '丙', '戊', '庚', '壬']
        return '元男' if day_gan in yang_gan else '元女'

    def calculate_star_fortune(self, gan, zhi):
        """计算星运（长生十二宫）"""
        return self.shengwang_table.get(zhi, {}).get(gan, '未知')

    def calculate_self_sitting(self, day_gan, day_zhi):
        """计算自坐（仅日柱）"""
        return self.calculate_star_fortune(day_gan, day_zhi)

    def calculate_kongwang(self, day_ganzhi):
        """计算空亡"""
        return self.kongwang_table.get(day_ganzhi, [])

    def calculate_nayin(self, gan_zhi):
        """计算纳音"""
        return self.nayin_table.get(gan_zhi, '未知')

    def determine_shishen(self, day_gan, target_gan):
        """确定十神"""
        # 简化的十神判断逻辑
        tiangan_info = {
            '甲': {'五行': '木', '阴阳': '阳'}, '乙': {'五行': '木', '阴阳': '阴'},
            '丙': {'五行': '火', '阴阳': '阳'}, '丁': {'五行': '火', '阴阳': '阴'},
            '戊': {'五行': '土', '阴阳': '阳'}, '己': {'五行': '土', '阴阳': '阴'},
            '庚': {'五行': '金', '阴阳': '阳'}, '辛': {'五行': '金', '阴阳': '阴'},
            '壬': {'五行': '水', '阴阳': '阳'}, '癸': {'五行': '水', '阴阳': '阴'}
        }

        day_wuxing = tiangan_info[day_gan]['五行']
        day_yinyang = tiangan_info[day_gan]['阴阳']
        target_wuxing = tiangan_info[target_gan]['五行']
        target_yinyang = tiangan_info[target_gan]['阴阳']

        # 五行生克关系
        wuxing_sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        wuxing_ke = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}

        # 判断生克关系
        if day_wuxing == target_wuxing:
            # 同我
            if day_yinyang == target_yinyang:
                return '比肩'
            else:
                return '劫财'
        elif wuxing_sheng[day_wuxing] == target_wuxing:
            # 我生
            if day_yinyang != target_yinyang:
                return '伤官'
            else:
                return '食神'
        elif wuxing_sheng[target_wuxing] == day_wuxing:
            # 生我
            if day_yinyang != target_yinyang:
                return '正印'
            else:
                return '偏印'
        elif wuxing_ke[day_wuxing] == target_wuxing:
            # 我克
            if day_yinyang != target_yinyang:
                return '正财'
            else:
                return '偏财'
        elif wuxing_ke[target_wuxing] == day_wuxing:
            # 克我
            if day_yinyang != target_yinyang:
                return '正官'
            else:
                return '七杀'
        else:
            return '未知'

    def calculate_shensha(self, sizhu, day_gan):
        """计算神煞"""
        shensha_results = {}
        
        for pillar_name, (gan, zhi) in sizhu.items():
            pillar_shensha = []
            
            # 天乙贵人
            if day_gan in self.shensha_table['天乙贵人']:
                if zhi in self.shensha_table['天乙贵人'][day_gan]:
                    pillar_shensha.append('天乙贵人')
            
            # 太极贵人
            if day_gan in self.shensha_table['太极贵人']:
                if zhi in self.shensha_table['太极贵人'][day_gan]:
                    pillar_shensha.append('太极贵人')
            
            # 文昌贵人
            if day_gan in self.shensha_table['文昌贵人']:
                if zhi in self.shensha_table['文昌贵人'][day_gan]:
                    pillar_shensha.append('文昌贵人')
            
            # 桃花
            year_zhi = sizhu['年柱'][1]
            day_zhi = sizhu['日柱'][1]
            for group, taohua_zhi in self.shensha_table['桃花'].items():
                if year_zhi in group or day_zhi in group:
                    if zhi == taohua_zhi:
                        pillar_shensha.append('桃花')
                    break
            
            # 华盖
            for group, huagai_zhi in self.shensha_table['华盖'].items():
                if year_zhi in group or day_zhi in group:
                    if zhi == huagai_zhi:
                        pillar_shensha.append('华盖')
                    break
            
            # 驿马
            for group, yima_zhi in self.shensha_table['驿马'].items():
                if year_zhi in group or day_zhi in group:
                    if zhi == yima_zhi:
                        pillar_shensha.append('驿马')
                    break
            
            # 羊刃（仅日干）
            if day_gan in self.shensha_table['羊刃']:
                if zhi == self.shensha_table['羊刃'][day_gan]:
                    pillar_shensha.append('羊刃')
            
            # 禄神（仅日干）
            if day_gan in self.shensha_table['禄神']:
                if zhi == self.shensha_table['禄神'][day_gan]:
                    pillar_shensha.append('禄神')
            
            shensha_results[pillar_name] = pillar_shensha if pillar_shensha else ['无']
        
        return shensha_results

    def calculate_paipan_detail(self, sizhu, shishen_result):
        """计算完整的排盘详细信息"""
        day_gan = sizhu['日柱'][0]
        day_ganzhi = sizhu['日柱'][0] + sizhu['日柱'][1]
        
        # 计算空亡
        kongwang = self.calculate_kongwang(day_ganzhi)
        
        result = {}
        
        for pillar_name, (gan, zhi) in sizhu.items():
            gan_zhi = gan + zhi
            
            # 主星（仅日柱显示）
            main_star = self.calculate_main_star(day_gan) if pillar_name == '日柱' else ''
            
            # 副星（地支藏干对应的十神）
            vice_star = self.determine_shishen(day_gan, gan)
            
            # 星运
            star_fortune = self.calculate_star_fortune(gan, zhi)
            
            # 自坐（仅日柱）
            self_sitting = self.calculate_self_sitting(day_gan, zhi) if pillar_name == '日柱' else ''
            
            # 纳音
            nayin = self.calculate_nayin(gan_zhi)
            
            result[pillar_name] = {
                '主星': main_star,
                '天干': gan,
                '地支': zhi,
                '副星': vice_star,
                '星运': star_fortune,
                '自坐': self_sitting,
                '空亡': ', '.join(kongwang),
                '纳音': nayin
            }
        
        # 计算神煞
        shensha_results = self.calculate_shensha(sizhu, day_gan)
        for pillar_name in result:
            result[pillar_name]['神煞'] = ', '.join(shensha_results[pillar_name])
        
        return result

    def get_wuxing_info(self, gan_or_zhi):
        """获取天干地支的五行属性信息（基于传统五方色系统）"""
        # 天干五行属性（基于《周礼》、《礼记》五方色系统）
        tiangan_wuxing = {
            '甲': {'五行': '木', '正统主色': '青色', '衍生色系': '绿色', '方位': '东方', '星运数字': 3},
            '乙': {'五行': '木', '正统主色': '青色', '衍生色系': '绿色', '方位': '东方', '星运数字': 8},
            '丙': {'五行': '火', '正统主色': '赤色（红）', '衍生色系': '紫色', '方位': '南方', '星运数字': 2},
            '丁': {'五行': '火', '正统主色': '赤色（红）', '衍生色系': '紫色', '方位': '南方', '星运数字': 7},
            '戊': {'五行': '土', '正统主色': '黄色', '衍生色系': '棕色', '方位': '中央', '星运数字': 5},
            '己': {'五行': '土', '正统主色': '黄色', '衍生色系': '棕色', '方位': '中央', '星运数字': 10},
            '庚': {'五行': '金', '正统主色': '白色', '衍生色系': '银色', '方位': '西方', '星运数字': 4},
            '辛': {'五行': '金', '正统主色': '白色', '衍生色系': '银色', '方位': '西方', '星运数字': 9},
            '壬': {'五行': '水', '正统主色': '玄色（黑）', '衍生色系': '蓝色', '方位': '北方', '星运数字': 1},
            '癸': {'五行': '水', '正统主色': '玄色（黑）', '衍生色系': '蓝色', '方位': '北方', '星运数字': 6}
        }

        # 地支五行属性（基于《周礼》、《礼记》五方色系统）
        dizhi_wuxing = {
            '子': {'五行': '水', '正统主色': '玄色（黑）', '衍生色系': '蓝色', '方位': '北方', '星运数字': 1},
            '丑': {'五行': '土', '正统主色': '黄色', '衍生色系': '棕色', '方位': '东北', '星运数字': 8},
            '寅': {'五行': '木', '正统主色': '青色', '衍生色系': '绿色', '方位': '东北', '星运数字': 3},
            '卯': {'五行': '木', '正统主色': '青色', '衍生色系': '绿色', '方位': '东方', '星运数字': 4},
            '辰': {'五行': '土', '正统主色': '黄色', '衍生色系': '棕色', '方位': '东南', '星运数字': 5},
            '巳': {'五行': '火', '正统主色': '赤色（红）', '衍生色系': '紫色', '方位': '东南', '星运数字': 6},
            '午': {'五行': '火', '正统主色': '赤色（红）', '衍生色系': '紫色', '方位': '南方', '星运数字': 7},
            '未': {'五行': '土', '正统主色': '黄色', '衍生色系': '棕色', '方位': '西南', '星运数字': 8},
            '申': {'五行': '金', '正统主色': '白色', '衍生色系': '银色', '方位': '西南', '星运数字': 9},
            '酉': {'五行': '金', '正统主色': '白色', '衍生色系': '银色', '方位': '西方', '星运数字': 10},
            '戌': {'五行': '土', '正统主色': '黄色', '衍生色系': '棕色', '方位': '西北', '星运数字': 11},
            '亥': {'五行': '水', '正统主色': '玄色（黑）', '衍生色系': '蓝色', '方位': '西北', '星运数字': 12}
        }

        if gan_or_zhi in tiangan_wuxing:
            return tiangan_wuxing[gan_or_zhi]
        elif gan_or_zhi in dizhi_wuxing:
            return dizhi_wuxing[gan_or_zhi]
        else:
            return {'五行': '', '正统主色': '', '衍生色系': '', '方位': ''}

    def format_paipan_table(self, paipan_info):
        """格式化排盘信息为表格形式（增强版，包含五行属性）"""
        try:
            # 表头
            header = f"{'':14}{'年柱':>8}{'月柱':>8}{'日柱':>8}{'时柱':>8}"

            # 主星行
            zhuxing_row = f"{'主星':12}"
            for pillar in ['年柱', '月柱', '日柱', '时柱']:
                zhuxing = paipan_info[pillar].get('主星', '') or ''
                zhuxing_row += f"{zhuxing:>8}"

            # 天干行（带五行属性）
            tiangan_row = f"{'天干':12}"
            for pillar in ['年柱', '月柱', '日柱', '时柱']:
                ganzhi = paipan_info[pillar].get('干支', ('', ''))
                gan = ganzhi[0] if isinstance(ganzhi, tuple) and len(ganzhi) > 0 else ''
                if gan:
                    wuxing_info = self.get_wuxing_info(gan)
                    gan_with_wuxing = f"{gan}{wuxing_info['五行']}"
                else:
                    gan_with_wuxing = gan or ''
                tiangan_row += f"{gan_with_wuxing:>8}"

            # 地支行（带五行属性）
            dizhi_row = f"{'地支':12}"
            for pillar in ['年柱', '月柱', '日柱', '时柱']:
                ganzhi = paipan_info[pillar].get('干支', ('', ''))
                zhi = ganzhi[1] if isinstance(ganzhi, tuple) and len(ganzhi) > 1 else ''
                if zhi:
                    wuxing_info = self.get_wuxing_info(zhi)
                    zhi_with_wuxing = f"{zhi}{wuxing_info['五行']}"
                else:
                    zhi_with_wuxing = zhi or ''
                dizhi_row += f"{zhi_with_wuxing:>8}"

            # 副星行
            fuxing_row = f"{'副星':12}"
            for pillar in ['年柱', '月柱', '日柱', '时柱']:
                fuxing = paipan_info[pillar].get('副星', '') or ''
                fuxing_row += f"{fuxing:>8}"

            # 星运行
            xingyun_row = f"{'星运':12}"
            for pillar in ['年柱', '月柱', '日柱', '时柱']:
                xingyun = paipan_info[pillar].get('星运', '') or ''
                xingyun_row += f"{xingyun:>8}"

            # 自坐行
            zizuo_row = f"{'自坐':12}"
            for pillar in ['年柱', '月柱', '日柱', '时柱']:
                zizuo = paipan_info[pillar].get('自坐', '') or ''
                zizuo_row += f"{zizuo:>8}"

            # 空亡行
            kongwang_row = f"{'空亡':12}"
            for pillar in ['年柱', '月柱', '日柱', '时柱']:
                kongwang = paipan_info[pillar].get('空亡', '') or ''
                if isinstance(kongwang, list):
                    kongwang = ', '.join(kongwang)
                kongwang_row += f"{kongwang:>8}"

            # 纳音行
            nayin_row = f"{'纳音':12}"
            for pillar in ['年柱', '月柱', '日柱', '时柱']:
                nayin = paipan_info[pillar].get('纳音', '') or ''
                nayin_row += f"{nayin:>8}"

            # 神煞行
            shensha_row = f"{'神煞':12}"
            for pillar in ['年柱', '月柱', '日柱', '时柱']:
                shensha = paipan_info[pillar].get('神煞', []) or []
                if isinstance(shensha, list):
                    shensha_text = ', '.join(shensha[:2])  # 只显示前两个
                    if len(shensha) > 2:
                        shensha_text += '等'
                else:
                    shensha_text = str(shensha) if shensha else ''
                shensha_row += f"{shensha_text:>8}"


            # 组合所有行
            table_lines = [
                header,
                zhuxing_row,
                tiangan_row,
                dizhi_row,
                fuxing_row,
                xingyun_row,
                zizuo_row,
                kongwang_row,
                nayin_row,
                shensha_row
            ]

            return '\n'.join(table_lines)

        except Exception as e:
            return f"排盘表格格式化失败: {e}"
