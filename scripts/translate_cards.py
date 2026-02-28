#!/usr/bin/env python3
"""Translate all English card content to Traditional Chinese (Taiwanese Mandarin)."""
import json

# ========== events.json translations ==========
EVENTS_TRANSLATIONS = {
    "daily_routine": {
        "text": "普通的一週，有些輕微的不適。",
        "character_name": "小綾",
        "character_role": "同事",
        "left": {"label": "在家休息"},
        "right": {"label": "撐著上班"},
    },
    "steroid_start": {
        "text": "症狀突然加劇。醫師建議使用類固醇。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "接受類固醇"},
        "right": {"label": "先不要"},
    },
    "stop_steroid": {
        "text": "臉變得很腫脹，你想停掉類固醇。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "立刻停藥"},
        "right": {"label": "慢慢減量"},
    },
    "biologic_start": {
        "text": "醫師建議開始生物製劑治療。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "開始治療"},
        "right": {"label": "拒絕"},
    },
    "dr_lin_followup": {
        "text": "林醫師檢查你的反應，詢問副作用的情況。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "如實回報"},
        "right": {"label": "淡化症狀"},
    },
    "dr_lin_biologic_followup": {
        "text": "林醫師說明導入療程的排程，請你全力配合。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "決心遵循"},
        "right": {"label": "再考慮看看"},
    },
    "biologic_injection": {
        "text": "排定的生物製劑注射週。",
        "left": {"label": "按時注射"},
        "right": {"label": "跳過注射"},
    },
    "premium_treatment": {
        "text": "有進階的治療方案可選擇。",
        "left": {"label": "使用健保方案"},
        "right": {"label": "自費選擇"},
    },
    "dr_google": {
        "text": "網路論壇上有人推薦神奇偏方。",
        "character_name": "論壇貼文",
        "character_role": "網路傳言",
        "left": {"label": "忽略"},
        "right": {"label": "相信偏方"},
    },
    "mild_treatment": {
        "text": "發炎期間，醫師提供溫和的治療選項。",
        "left": {"label": "接受治療"},
        "right": {"label": "暫不處理"},
    },
    "urgent_bathroom": {
        "text": "開會到一半突然急著上廁所。",
        "character_name": "陳經理",
        "character_role": "主管",
        "left": {"label": "立刻衝出去"},
        "right": {"label": "硬撐"},
    },
    "placebo": {
        "text": "阿姨推薦了一款「護腸」保健品。",
        "character_name": "梅嬸",
        "character_role": "親戚",
        "left": {"label": "試試看"},
        "right": {"label": "婉拒"},
    },
    "supplement_risk": {
        "text": "你正在服用抗凝血劑，考慮加吃保健品。",
        "character_name": "梅嬸",
        "character_role": "親戚",
        "left": {"label": "吃保健品"},
        "right": {"label": "不吃"},
    },
    "social_photo": {
        "text": "朋友們想拍團體照。",
        "character_name": "同事",
        "character_role": "朋友",
        "left": {"label": "入鏡拍照"},
        "right": {"label": "婉拒"},
        "text_overrides": {"MOON_FACE": "月亮臉讓你對拍照感到很不自在。"},
    },
    "overconfidence": {
        "text": "你覺得自己好多了，大吃一頓麻辣鍋。",
        "character_name": "內心之聲",
        "character_role": "衝動的自我",
        "left": {"label": "繼續大吃"},
        "right": {"label": "克制一下"},
    },
    "megacolon": {
        "text": "毒素蓄積引發巨結腸症。",
        "left": {"label": "急診處理"},
        "right": {"label": "再等等看"},
    },
    "infection": {
        "text": "伺機性感染來襲。",
        "character_name": "王護理師",
        "character_role": "病房",
        "left": {"label": "住院治療"},
        "right": {"label": "不理會"},
    },
    "bleeding": {
        "text": "藥物交互作用導致出血事件。",
        "character_name": "急診醫師",
        "character_role": "急診室",
        "left": {"label": "就醫處理"},
        "right": {"label": "再觀察"},
    },
    "checkup": {
        "text": "季度回診檢查結果出爐。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "調整療程"},
        "right": {"label": "維持現狀"},
    },
    "surgery": {
        "text": "有穿孔風險，醫師建議手術。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "同意手術"},
        "right": {"label": "拒絕手術"},
    },
    "ostomy_care": {
        "text": "開始學習造口照護的日常。",
        "character_name": "王護理師",
        "character_role": "造口護理",
        "left": {"label": "認真練習"},
        "right": {"label": "拖延逃避"},
    },
    "winter_joint_pain": {
        "text": "寒流來襲，關節疼痛加劇。",
        "character_name": "內心之聲",
        "character_role": "疲憊",
        "left": {"label": "好好休息"},
        "right": {"label": "咬牙撐過"},
    },
    "aya_followup_1": {
        "text": "小綾幫你代班，問你感覺如何。",
        "character_name": "小綾",
        "character_role": "同事",
        "left": {"label": "向她道謝"},
        "right": {"label": "說沒事"},
    },
    "aya_followup_2": {
        "text": "小綾邀你下班後一起吃飯。",
        "character_name": "小綾",
        "character_role": "同事",
        "left": {"label": "參加"},
        "right": {"label": "婉拒"},
    },
    "family_support_1": {
        "text": "媽媽特地煮了清淡的餐點給你。",
        "character_name": "媽媽",
        "character_role": "家人",
        "left": {"label": "開心接受"},
        "right": {"label": "不想吃"},
    },
    "manager_pressure_1": {
        "text": "陳經理問你為什麼突然離席。",
        "character_name": "陳經理",
        "character_role": "主管",
        "left": {"label": "坦白說明"},
        "right": {"label": "找藉口搪塞"},
    },
    "manager_pressure_2": {
        "text": "陳經理在你發病期間排了更多工作。",
        "character_name": "陳經理",
        "character_role": "主管",
        "left": {"label": "硬撐完成"},
        "right": {"label": "設定界線"},
    },
    "adherence_warning_1": {
        "text": "林醫師警告停藥可能導致復發。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "承諾遵從"},
        "right": {"label": "仍然猶豫"},
    },
    "adherence_warning_2": {
        "text": "藥師給了一個藥盒和服藥建議。",
        "character_name": "藥師",
        "character_role": "照護團隊",
        "left": {"label": "接受藥盒"},
        "right": {"label": "婉拒"},
    },
    "support_group_1": {
        "text": "病友會分享發炎期的因應小技巧。",
        "character_name": "病友會",
        "character_role": "夥伴",
        "left": {"label": "加入討論"},
        "right": {"label": "默默旁聽"},
    },
    "support_group_2": {
        "text": "病友推薦查證過的資源，勸你別信偏方。",
        "character_name": "病友會",
        "character_role": "夥伴",
        "left": {"label": "聽從建議"},
        "right": {"label": "不理會"},
    },
    "hr_accommodation_1": {
        "text": "人資表示如果提交醫療文件，可以彈性上班。",
        "character_name": "人資",
        "character_role": "公司",
        "left": {"label": "提交文件"},
        "right": {"label": "不想揭露"},
    },
    "hr_accommodation_2": {
        "text": "主管同意幫你調整截止日期。",
        "character_name": "陳經理",
        "character_role": "主管",
        "left": {"label": "接受調整"},
        "right": {"label": "拒絕幫助"},
    },
    "monitoring_check_1": {
        "text": "安排抽血監測發炎指標。",
        "character_name": "王護理師",
        "character_role": "照護團隊",
        "left": {"label": "去抽血"},
        "right": {"label": "跳過檢查"},
    },
    "monitoring_check_2": {
        "text": "林醫師和你討論副作用，調整劑量。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "調整劑量"},
        "right": {"label": "維持劑量"},
    },
    "aya_followup_3": {
        "text": "小綾問你需不需要她幫忙跟主管溝通。",
        "character_name": "小綾",
        "character_role": "同事",
        "left": {"label": "接受幫忙"},
        "right": {"label": "自己處理"},
    },
    "aya_followup_4": {
        "text": "小綾帶你去一個安靜的地方休息。",
        "character_name": "小綾",
        "character_role": "同事",
        "left": {"label": "好好休息"},
        "right": {"label": "婉拒"},
    },
    "family_support_2": {
        "text": "家人問可以怎麼幫忙陪你看診。",
        "character_name": "媽媽",
        "character_role": "家人",
        "left": {"label": "請家人陪同"},
        "right": {"label": "說不用"},
    },
    "family_support_3": {
        "text": "家庭聚餐讓你對飲食選擇感到壓力。",
        "character_name": "家人",
        "character_role": "家庭",
        "left": {"label": "說明飲食限制"},
        "right": {"label": "隨便吃"},
    },
    "support_group_3": {
        "text": "資深病友分享了一份發炎期準備清單。",
        "character_name": "病友會",
        "character_role": "夥伴",
        "left": {"label": "收藏清單"},
        "right": {"label": "不需要"},
    },
    "support_group_4": {
        "text": "大家邀你分享自己的經歷。",
        "character_name": "病友會",
        "character_role": "夥伴",
        "left": {"label": "分享"},
        "right": {"label": "暫時不說"},
    },
    "flare_episode": {
        "text": "發炎指數飆升，凌晨三點被腹絞痛痛醒。",
        "character_name": "內心之聲",
        "character_role": "身體",
        "left": {"label": "打給林醫師"},
        "right": {"label": "撐到天亮"},
    },
    "diet_choice_flare": {
        "text": "好想吃麻辣鍋，但腸道正在發炎。",
        "character_name": "內心之聲",
        "character_role": "食慾",
        "left": {"label": "吃清淡食物"},
        "right": {"label": "大吃麻辣鍋"},
        "education": {
            "title": "飲食與 IBD",
            "content": "在發炎活動期間，避免刺激性食物有助於減輕症狀嚴重度。",
            "source": "ECCO Guidelines 2023",
        },
    },
    "sleep_crisis": {
        "text": "連續三個晚上被疼痛吵得睡不著。",
        "character_name": "內心之聲",
        "character_role": "疲憊不堪",
        "left": {"label": "吃安眠藥"},
        "right": {"label": "硬撐"},
    },
    "exercise_choice": {
        "text": "小綾約你早上去慢跑。",
        "character_name": "小綾",
        "character_role": "同事",
        "left": {"label": "改成散步"},
        "right": {"label": "今天不去"},
    },
    "anemia_onset": {
        "text": "抽血報告顯示慢性出血導致缺鐵性貧血。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "鐵劑靜脈注射"},
        "right": {"label": "口服鐵劑"},
        "education": {
            "title": "IBD 與缺鐵性貧血",
            "content": "高達 45% 的 IBD 患者會出現缺鐵性貧血。靜脈注射鐵劑效果較好但費用較高。",
            "source": "ECCO Guidelines 2023",
        },
    },
    "insurance_fight": {
        "text": "健保拒絕給付生物製劑治療。",
        "character_name": "保險專員",
        "character_role": "健保體系",
        "left": {"label": "提出申覆"},
        "right": {"label": "換成便宜的藥"},
    },
    "night_emergency": {
        "text": "半夜嚴重血便。急診室要開車 30 分鐘。",
        "character_name": "內心之聲",
        "character_role": "緊急狀況",
        "left": {"label": "衝去急診"},
        "right": {"label": "等到早上"},
    },
    "partner_strain": {
        "text": "你的另一半又因為取消約會而生氣了。",
        "character_name": "伴侶",
        "character_role": "感情",
        "left": {"label": "好好溝通"},
        "right": {"label": "迴避話題"},
    },
    "mindfulness_class": {
        "text": "護理師推薦了免費的正念課程，專為慢性病患者設計。",
        "character_name": "王護理師",
        "character_role": "照護團隊",
        "left": {"label": "報名試試"},
        "right": {"label": "沒時間"},
        "education": {
            "title": "壓力與 IBD",
            "content": "正念和認知行為治療已被證實能減少 IBD 患者的焦慮和憂鬱，並可能改善疾病預後。",
            "source": "Gastroenterology 2021",
        },
    },
    "cold_flu_season": {
        "text": "流感季來臨，身邊的人紛紛中標。",
        "character_name": "內心之聲",
        "character_role": "警覺",
        "left": {"label": "打流感疫苗"},
        "right": {"label": "賭一把"},
        "education": {
            "title": "IBD 患者的疫苗接種",
            "content": "使用免疫抑制劑的 IBD 患者應接種不活化疫苗。活性疫苗可能有禁忌。",
            "source": "ACG Clinical Guideline 2022",
        },
    },
    "steroid_side_effect": {
        "text": "月亮臉和體重增加越來越明顯，同事都在看你。",
        "character_name": "內心之聲",
        "character_role": "自我形象",
        "left": {"label": "跟林醫師討論減量"},
        "right": {"label": "默默忍受"},
    },
    "eim_joint_pain": {
        "text": "膝蓋劇烈疼痛。林醫師說這是腸外表現。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "轉診風濕科"},
        "right": {"label": "吃止痛藥"},
        "education": {
            "title": "腸外表現 (EIM)",
            "content": "高達 40% 的 IBD 患者會出現腸道以外的症狀，包括關節疼痛、皮膚病變和眼部發炎。",
            "source": "Nat Rev Gastroenterol Hepatol 2021",
        },
    },
    "eim_skin_rash": {
        "text": "小腿出現紅色壓痛結節，可能是結節性紅斑。",
        "character_name": "皮膚科醫師",
        "character_role": "專科",
        "left": {"label": "積極治療"},
        "right": {"label": "觀察追蹤"},
        "education": {
            "title": "結節性紅斑與 IBD",
            "content": "結節性紅斑是 IBD 最常見的皮膚表現，約影響 15% 的患者，通常與疾病活動度相關。",
            "source": "ECCO Guidelines 2023",
        },
    },
    "eim_eye_inflammation": {
        "text": "你的眼睛又紅又痛。眼科醫師懷疑是葡萄膜炎。",
        "character_name": "眼科醫師",
        "character_role": "專科",
        "left": {"label": "類固醇眼藥水"},
        "right": {"label": "先不處理"},
        "education": {
            "title": "IBD 與葡萄膜炎",
            "content": "葡萄膜炎（眼部發炎）發生在約 8% 的 IBD 患者身上。及時治療可防止永久性視力損傷。",
            "source": "Ophthalmology 2020",
        },
    },
    "recovery_walk": {
        "text": "你在公園散步了 20 分鐘，不用急著找廁所。",
        "character_name": "內心之聲",
        "character_role": "希望",
        "left": {"label": "慶祝這個進步"},
        "right": {"label": "還是很擔心"},
    },
    "remission_milestone": {
        "text": "林醫師說你的糞便鈣衛蛋白首次恢復正常。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "維持現有用藥"},
        "right": {"label": "能不能減藥"},
        "education": {
            "title": "糞便鈣衛蛋白",
            "content": "糞便鈣衛蛋白是腸道發炎的非侵入性指標。數值低於 150 μg/g 表示腸黏膜正在修復。",
            "source": "Gut 2022",
        },
    },
    "medication_reminder": {
        "text": "這週又忘了吃好幾次晚上的藥。",
        "character_name": "手機鬧鐘",
        "character_role": "提醒",
        "left": {"label": "買藥盒整理"},
        "right": {"label": "想到再吃"},
        "education": {
            "title": "藥物順從性",
            "content": "未規律服用維持治療藥物會使復發風險增加 2-5 倍。藥盒和鬧鐘可顯著改善順從性。",
            "source": "Inflamm Bowel Dis 2021",
        },
    },
    "biologic_switch": {
        "text": "目前的生物製劑效果不理想，林醫師建議換藥。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "換藥"},
        "right": {"label": "先不換"},
        "education": {
            "title": "生物製劑換藥",
            "content": "當一種生物製劑失效時，換用不同機制的藥物可在 30-50% 的患者中達到緩解。",
            "source": "Lancet Gastroenterol Hepatol 2023",
        },
    },
    "therapy_deescalation": {
        "text": "病情穩定好幾個月了。林醫師建議考慮減藥。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "同意減藥"},
        "right": {"label": "維持原劑量"},
    },
    "online_community": {
        "text": "IBD 病友團體邀你加入線上論壇。",
        "character_name": "線上社群",
        "character_role": "社群",
        "left": {"label": "加入參與"},
        "right": {"label": "潛水旁觀"},
    },
    "therapist_referral": {
        "text": "林醫師建議你去看專攻慢性病的心理師。",
        "character_name": "林醫師",
        "character_role": "腸胃科主治",
        "left": {"label": "預約看診"},
        "right": {"label": "還沒準備好"},
        "education": {
            "title": "心理治療與 IBD",
            "content": "心理介入（認知行為治療、接受與承諾治療）能減少 IBD 患者的焦慮和憂鬱，並可能改善疾病結果。",
            "source": "Cochrane Review 2023",
        },
    },
    "diet_hotpot": {
        "text": "部門聚餐在麻辣鍋店，紅油正在滾。",
        "left": {"label": "跟大家一起吃辣"},
        "right": {"label": "只喝清湯"},
    },
    "diet_supplements": {
        "text": "廣告寫著「護腸薑黃素膠囊」，很貴但看起來很厲害。",
        "left": {"label": "買一瓶"},
        "right": {"label": "省錢"},
    },
    "diet_fiber_smoothie": {
        "text": "媽媽打了一杯高纖維羽衣甘藍汁。「排毒用的！」她說。",
        "left": {"label": "喝了讓她開心"},
        "right": {"label": "堅定拒絕"},
    },
    "diet_peer_pressure_alcohol": {
        "text": "喜宴上大家都在敬酒乾杯，你感覺格格不入。",
        "left": {"label": "喝一杯"},
        "right": {"label": "用水乾杯"},
    },
    "diet_midnight_snack": {
        "text": "凌晨兩點肚子餓了，冰箱裡有剩下的披薩。",
        "left": {"label": "吃披薩"},
        "right": {"label": "吃根香蕉"},
    },
    "surgery_consult_decision": {
        "text": "狹窄越來越嚴重，外科醫師在圖上劃出切除範圍。",
        "left": {"label": "安排手術"},
        "right": {"label": "拖延觀察"},
    },
    "surgery_pre_op_marking": {
        "text": "護理師在你的腹部畫了造口的預備位置。「以防萬一。」她說。",
        "left": {"label": "詢問造口照護"},
        "right": {"label": "害怕地別過頭"},
    },
    "surgery_procedure_day": {
        "text": "你從麻醉中醒來。肚子上多了一個袋子。手術結束了。",
        "left": {"label": "看看造口袋"},
        "right": {"label": "閉上眼睛"},
    },
    "ostomy_learning_curve": {
        "text": "造口護理師正在教你怎麼更換底座。看起來很複雜。",
        "left": {"label": "認真練習"},
        "right": {"label": "讓護理師代勞"},
    },
    "ostomy_leak_public": {
        "text": "在超市逛到一半，皮膚上感覺一股溫熱⋯⋯天啊。",
        "left": {"label": "衝進廁所"},
        "right": {"label": "慌張呆住"},
    },
    "ostomy_leak_event": {
        "text": "底座黏膠鬆脫了。你聞到味道，感覺到濕氣。",
        "left": {"label": "立刻更換"},
        "right": {"label": "用膠帶撐一下"},
        "text_overrides": {"emergency": "趕快找無障礙廁所"},
    },
    "social_breakdown": {
        "text": "朋友們不再約你出門了。你覺得徹底被孤立。",
        "left": {"label": "打給好朋友"},
        "right": {"label": "接受孤獨"},
    },
}

# ========== scenarios_expansion.json translations ==========
SCENARIOS_TRANSLATIONS = {
    "work_overtime_flare": {
        "text": "發炎期間主管要求你加班趕專案。",
        "character_name": "主管",
        "character_role": "經理",
        "left": {"label": "咬牙加班"},
        "right": {"label": "請假回家"},
    },
    "work_toilet_meeting": {
        "text": "重要會議中，你的肚子突然翻攪。",
        "character_name": "內心獨白",
        "character_role": "腸道直覺",
        "left": {"label": "藉口離席"},
        "right": {"label": "忍到結束"},
    },
    "work_promotion_stress": {
        "text": "升遷機會來了，但壓力可能讓病情惡化。",
        "character_name": "人資",
        "character_role": "經理",
        "left": {"label": "接受升遷"},
        "right": {"label": "放棄機會"},
    },
    "travel_backpack": {
        "text": "朋友約你去東南亞背包旅行。",
        "character_name": "好友",
        "character_role": "冒險家",
        "left": {"label": "一起出發"},
        "right": {"label": "安全留守"},
    },
    "travel_meds_timezone": {
        "text": "跨時區旅行，用藥時間全亂了。",
        "character_name": "內心獨白",
        "character_role": "旅人",
        "left": {"label": "設鬧鐘調整"},
        "right": {"label": "隨緣吃藥"},
    },
    "travel_food_poison": {
        "text": "路邊攤的食物飄著誘人的香氣，但你不確定衛生狀況。",
        "character_name": "攤販",
        "character_role": "旅途",
        "left": {"label": "大膽嚐鮮"},
        "right": {"label": "吃安全的"},
    },
    "family_plan": {
        "text": "伴侶提起想要小孩的事。你的病情讓這件事更複雜。",
        "character_name": "伴侶",
        "character_role": "摯愛",
        "left": {"label": "開始計劃"},
        "right": {"label": "暫時延後"},
    },
    "pregnancy_meds_worry": {
        "text": "你擔心藥物會影響胎兒，考慮自行停藥。",
        "character_name": "內心獨白",
        "character_role": "準父母",
        "left": {"label": "停掉藥物"},
        "right": {"label": "繼續服藥"},
    },
    "child_genetic_worry": {
        "text": "你擔心 IBD 會遺傳給下一代。",
        "character_name": "內心獨白",
        "character_role": "準父母",
        "left": {"label": "陷入焦慮"},
        "right": {"label": "接受現實"},
    },
}


def apply_translations(filepath: str, translations: dict) -> None:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    for card in data:
        card_id = card.get("id")
        if card_id not in translations:
            continue
        t = translations[card_id]

        # Top-level fields
        for key in ("text", "character_name", "character_role"):
            if key in t:
                card[key] = t[key]

        # Options
        for side in ("left", "right"):
            if side in t:
                if side in card:
                    card[side]["label"] = t[side]["label"]

        # text_overrides
        if "text_overrides" in t:
            card["text_overrides"] = t["text_overrides"]

        # education
        if "education" in t:
            card["education"] = t["education"]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"✅ {filepath}: {len(translations)} cards translated")


if __name__ == "__main__":
    apply_translations("assets/events.json", EVENTS_TRANSLATIONS)
    apply_translations("assets/scenarios_expansion.json", SCENARIOS_TRANSLATIONS)
    print("🎉 All translations applied!")
