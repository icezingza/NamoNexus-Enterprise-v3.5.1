# src/services/dharma_service.py
"""
Dharma Alignment Service - Four Noble Truths Framework
Provides wisdom-based emotional support through Buddhist principles
"""

from typing import Dict
from enum import Enum


class DharmaStage(str, Enum):
    """Four Noble Truths Stages"""

    DUKKHA = "dukkha"  # Suffering/Problem identification
    SAMUDAYA = "samudaya"  # Origin/Root cause analysis
    NIRODHA = "nirodha"  # Cessation/Solution emergence
    MAGGA = "magga"  # Path/Implementation strategy


class DharmaAlignmentService:
    """
    Four-stage Dharma alignment analysis engine.
    Core insight: Problems have roots, solutions have paths
    """

    def __init__(self):
        self.four_noble_truths = {
            "dukkha": {
                "name": "ทุกข์ (Suffering exists)",
                "principle": "Acknowledge the pain is real",
                "thai": "ยอมรับว่าความทุกข์เป็นของจริง",
            },
            "samudaya": {
                "name": "สาเหตุ (Root cause)",
                "principle": "Understand why it hurts",
                "thai": "ทำความเข้าใจที่มาของความทุกข์",
            },
            "nirodha": {
                "name": "ปลดปล่อย (Release)",
                "principle": "It can end through understanding",
                "thai": "ปลดปล่อยการยึดติด",
            },
            "magga": {
                "name": "เส้นทาง (The path forward)",
                "principle": "Practical steps to freedom",
                "thai": "เส้นทางไปสู่ความสุข",
            },
        }

        self.eightfold_path = {
            "Right View": "เห็นความจริงให้ชัดเจน",
            "Right Intention": "ตั้งใจอย่างบริสุทธิ์",
            "Right Speech": "พูดด้วยความจริงใจ",
            "Right Action": "ปฏิบัติตามธรรมชาติ",
            "Right Livelihood": "มีชีวิตอย่างสุจริต",
            "Right Effort": "พยายามปลูกสิ่งดี",
            "Right Mindfulness": "สังเกตด้วยสติ",
            "Right Concentration": "เจริญสมาธิ",
        }

    def apply_four_noble_truths(
        self, problem: str, emotion: str, intensity: float
    ) -> Dict:
        """
        Apply Four Noble Truths framework to user's problem

        Args:
            problem: User's problem statement
            emotion: Detected emotion (sadness, anxiety, anger, etc.)
            intensity: Emotional intensity (0-10)

        Returns:
            Complete four-stage analysis with wisdom insights
        """

        # STAGE 1: DUKKHA - Validate the suffering
        stage_1 = self._analyze_dukkha(problem, intensity)

        # STAGE 2: SAMUDAYA - Find root causes
        stage_2 = self._analyze_samudaya(problem, emotion)

        # STAGE 3: NIRODHA - Show the way to release
        stage_3 = self._analyze_nirodha(problem)

        # STAGE 4: MAGGA - Provide practical steps
        stage_4 = self._analyze_magga(emotion, intensity)

        return {
            "dukkha": stage_1,
            "samudaya": stage_2,
            "nirodha": stage_3,
            "magga": stage_4,
            "eightfold_path": self.eightfold_path,
            "dharmic_path": self._suggest_dharmic_path(emotion, intensity),
            "coherence_score": self._compute_coherence(
                stage_1, stage_2, stage_3, stage_4
            ),
        }

    def _analyze_dukkha(self, problem: str, intensity: float) -> Dict:
        """
        STAGE 1: ทุกข์ (Suffering Validation)
        Key: "Your pain is real. That's valid."
        """
        return {
            "truth": "ทุกข์นี้มีจริง (This suffering is real)",
            "validation": f"คุณรู้สึกเจ็บปวดในระดับ {intensity}/10 - นั่นถูกต้อง",
            "insight": "การยอมรับความเจ็บปวด คือขั้นแรกของการปลดปล่อย",
            "reflection": "คุณไม่ได้ผิด สถานการณ์ที่ยากลำบาก",
        }

    def _analyze_samudaya(self, problem: str, emotion: str) -> Dict:
        """
        STAGE 2: สาเหตุ (Root Cause Analysis)
        Key: "Let's understand what's actually causing this"
        """

        cause_patterns = {
            "sadness": {
                "likely_causes": [
                    "การสูญเสีย",
                    "การถูกปฏิเสธ",
                    "ความคาดหวังที่ผิดหวัง",
                    "ความรู้สึกโดดเดี่ยว",
                ],
                "insight": "ความเศร้าเป็นการสื่อสารว่า เราสูญเสียสิ่งที่สำคัญ",
            },
            "anxiety": {
                "likely_causes": [
                    "ความไม่แน่นอนในอนาคต",
                    "พยายามควบคุมสิ่งที่ไม่อาจควบคุม",
                    "การกำหนดมาตรฐานที่สูงเกินไป",
                    "ความกลัวจากประสบการณ์เก่า",
                ],
                "insight": "ความกังวล = พยายามป้องกันสิ่งที่ยังมาไม่ถึง",
            },
            "anger": {
                "likely_causes": [
                    "ขอบเขตถูกละเมิด",
                    "รู้สึกไม่ยุติธรรม",
                    "ความเสียหายต่อศักดิ์ศรี",
                    "ความคาดหวังที่ไม่ตรงกัน",
                ],
                "insight": "โกรธบ่งชี้ว่า ค่านิยมของเรากำลังถูกละเมิด",
            },
        }

        pattern = cause_patterns.get(
            emotion.lower(),
            {
                "likely_causes": ["ความต้องการที่ไม่ได้รับการตอบสนอง"],
                "insight": "ทุกอารมณ์มีที่มา เมื่อเข้าใจได้ ก็จัดการได้",
            },
        )

        return {
            "truth": "ทุกข์เกิดจากสาเหตุ (Causes exist)",
            "emotion": emotion,
            "probable_causes": pattern["likely_causes"],
            "deeper_insight": pattern["insight"],
            "deeper_question": "สิ่งใดที่คุณต้องการจริงๆ ที่ยังไม่ได้รับ?",
        }

    def _analyze_nirodha(self, problem: str) -> Dict:
        """
        STAGE 3: นิโรธ (Cessation/Release)
        Key: "This can change. Not by avoiding, but by understanding"
        """
        return {
            "truth": "ทุกข์นี้สามารถสิ้นสุดได้ (Suffering can end)",
            "path_to_peace": "ปลดปล่อยการยึดติด ไม่ใช่การหลบหนี",
            "liberating_insight": "เมื่อคุณปล่อยการต่อสู้ ความทุกข์เบาบางลง",
            "perspective": "คุณไม่สามารถเปลี่ยนปัญหา แต่เปลี่ยนความสัมพันธ์กับมันได้",
            "future_state": "คุณสามารถอยู่ร่วมกับปัญหานี้ได้ โดยไม่ให้มันครอบงำ",
        }

    def _analyze_magga(self, emotion: str, intensity: float) -> Dict:
        """
        STAGE 4: มรรค (The Path Forward)
        Key: "Here are 8 dimensions to cultivate wisdom"
        """

        practical_steps = {
            "sadness": [
                "1. (Right View) ยอมรับว่าสิ่งทั้งหมดเปลี่ยนแปลง",
                "2. (Right Intention) ตั้งใจให้อภัยตัวเอง",
                "3. (Right Speech) พูดจาเชิญชวนตัวเองด้วยเมตตา",
                "4. (Right Action) โทรหาเพื่อน หรือขอความช่วยเหลือ",
                "5. (Right Livelihood) ทำสิ่งที่ทำให้คุณมีชีวิตชีวา",
                "6. (Right Effort) เดินทีละก้าว",
                "7. (Right Mindfulness) สังเกตอารมณ์ โดยไม่ปฏิเสธ",
                "8. (Right Concentration) ทำสิ่งที่คุณรัก",
            ],
            "anxiety": [
                "1. (Right View) เข้าใจว่ากำลังคิดถึงสิ่งที่ยังไม่เกิด",
                "2. (Right Intention) ตั้งใจปล่อยวางการควบคุม",
                "3. (Right Speech) พูดประโยคเชิญชวนสติ",
                "4. (Right Action) หายใจลึกช้า 5 ครั้ง",
                "5. (Right Livelihood) ทำเพียงสิ่งที่จำเป็นวันนี้",
                "6. (Right Effort) สร้างนิสัยเล็กน้อยทีละนิด",
                "7. (Right Mindfulness) สังเกตความกังวล ไม่ต่อสู้",
                "8. (Right Concentration) โยคะ หรือสมาธิสั้นๆ",
            ],
            "anger": [
                "1. (Right View) โกรธบ่งชี้ว่าขอบเขตถูกล่วงละเมิด",
                "2. (Right Intention) ตั้งใจแสดงความแข็งแกร่งอย่างสร้างสรรค์",
                "3. (Right Speech) เขียนจดหมาย (ไม่ต้องส่ง)",
                "4. (Right Action) เดินออกไป หรือออกกำลังกาย",
                "5. (Right Livelihood) จัดระเบียบพื้นที่ของคุณ",
                "6. (Right Effort) ระบายพลังงาน ไม่ทำลาย",
                "7. (Right Mindfulness) สังเกตเมื่อมันผ่านไป",
                "8. (Right Concentration) ถามตัวเอง: จริงๆ ฉันต้องการอะไร?",
            ],
        }

        steps = practical_steps.get(
            emotion.lower(),
            [
                "1. หยุดเพื่อสังเกตสถานการณ์",
                "2. หายใจด้วยสติ",
                "3. ยอมรับความรู้สึก",
                "4. ค่อยๆ ปล่อยวาง",
            ],
        )

        return {
            "truth": "มีเส้นทางออก (A path exists)",
            "eightfold_path_steps": steps,
            "immediate_action": f"ในนี้ 5 นาที: {steps[0] if steps else 'หายใจด้วยสติ'}",
            "intensity_guidance": self._get_intensity_guidance(intensity),
        }

    def _suggest_dharmic_path(self, emotion: str, intensity: float) -> str:
        """
        Generate wisdom message based on emotion intensity
        """
        if intensity > 8:
            return "🙏 ทุกข์นี้คือการเรียกหา เรียกหาการเปลี่ยนแปลง เรียกหาสติ เรียกหาความเมตตา"
        elif intensity > 5:
            return "✨ สิ่งที่คุณรู้สึก คือโอกาสให้เกิดปัญญา"
        else:
            return "🌱 ดำเนินต่อไปด้วยสติ ยิ่งเบา ยิ่งชาญฉลาด"

    def _get_intensity_guidance(self, intensity: float) -> str:
        """Guidance based on emotional intensity"""
        if intensity > 8:
            return "🚨 ความเจ็บปวดหนัก - ลองขอความช่วยเหลือจากผู้อื่น"
        elif intensity > 5:
            return "⚠️ ปานกลาง - ต้องการความสนใจ แต่สามารถจัดการได้"
        else:
            return "💚 เบา - สามารถจัดการได้ด้วยตัวเอง"

    def _compute_coherence(self, s1: Dict, s2: Dict, s3: Dict, s4: Dict) -> float:
        """
        Calculate coherence score (0-1)
        Shows how well the four stages align together
        """
        # Simple model: all stages present = high coherence
        all_stages_present = all([s1, s2, s3, s4])
        return 0.95 if all_stages_present else 0.75


# Singleton instance
dharma_service = DharmaAlignmentService()
