# ============================================
# NamoNexus MVP v0.1 - Complete Setup
# ============================================

# Step 1: Create project folder
mkdir namo-mvp
cd namo-mvp

# Step 2: Create src directory
mkdir src

# Step 3: Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.4.2
python-dotenv==1.0.0
transformers==4.34.0
torch==2.1.0
firebase-admin==6.2.0
numpy==1.24.3
requests==2.31.0
python-multipart==0.0.6
EOF

# Step 4: Install dependencies
pip install -r requirements.txt

# Step 5: Create all 7 Python files in src/

# src/config.py
cat > src/config.py << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    DEBUG = os.getenv("DEBUG", "False") == "True"
    FIREBASE_KEY = os.getenv("FIREBASE_KEY", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "localhost")
    EMOTION_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
    CRISIS_KEYWORDS = [
        "kill myself", "PIP", "harm myself",
        "hurt myself", "end it all", "don't want to live"
    ]
    MAX_MEMORY_ITEMS = 1000
    MEMORY_RETENTION_DAYS = 365
    FOUR_NOBLE_TRUTHS = {
        "dukkha": "suffering exists",
        "samudaya": "suffering has causes",
        "nirodha": "suffering can end",
        "magga": "path to end suffering"
    }

config = Config()
EOF

# src/memory_service.py
cat > src/memory_service.py << 'EOF'
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
import time

@dataclass
class Memory:
    id: str
    user_id: str
    event: str
    emotion: str
    emotion_intensity: float
    Harmonic Alignment_insight: str
    timestamp: float
    importance: float
    
    def to_dict(self):
        return asdict(self)

class MemoryService:
    def __init__(self):
        self.memory_store: Dict[str, List[Memory]] = {}
        
    def store_experience(self, user_id: str, event: str, emotion: str, 
                        emotion_intensity: float, Harmonic Alignment_insight: str = ""):
        memory_id = f"{user_id}_{int(time.time()*1000)}"
        memory = Memory(
            id=memory_id,
            user_id=user_id,
            event=event,
            emotion=emotion,
            emotion_intensity=emotion_intensity,
            Harmonic Alignment_insight=Harmonic Alignment_insight,
            timestamp=time.time(),
            importance=emotion_intensity / 10.0
        )
        
        if user_id not in self.memory_store:
            self.memory_store[user_id] = []
        
        self.memory_store[user_id].append(memory)
        return memory.to_dict()
    
    def retrieve_user_context(self, user_id: str, days_back: int = 30) -> List[Dict]:
        if user_id not in self.memory_store:
            return []
        
        cutoff_time = time.time() - (days_back * 24 * 3600)
        relevant_memories = [
            m for m in self.memory_store[user_id]
            if m.timestamp >= cutoff_time
        ]
        
        relevant_memories.sort(
            key=lambda x: (x.importance, x.timestamp),
            reverse=True
        )
        
        return [m.to_dict() for m in relevant_memories]
    
    def find_linked_memories(self, user_id: str, emotion: str, 
                            similarity_threshold: float = 0.7) -> List[Dict]:
        if user_id not in self.memory_store:
            return []
        
        linked = []
        for memory in self.memory_store[user_id]:
            if memory.emotion.lower() == emotion.lower():
                similarity = 0.9
            elif self._is_related_emotion(memory.emotion, emotion):
                similarity = 0.75
            else:
                similarity = 0.5
            
            if similarity >= similarity_threshold:
                linked.append({
                    "memory": memory.to_dict(),
                    "similarity_score": similarity
                })
        
        linked.sort(key=lambda x: x["similarity_score"], reverse=True)
        return linked[:10]
    
    def _is_related_emotion(self, emotion1: str, emotion2: str) -> bool:
        emotion_groups = {
            "sad": ["sadness", "depression", "grief", "loss", "unhappy"],
            "anxious": ["anxiety", "fear", "worry", "stressed", "nervous"],
            "angry": ["anger", "rage", "irritated", "frustrated", "resentment"],
            "happy": ["joy", "happiness", "contentment", "peace", "gratitude"]
        }
        
        for group, emotions in emotion_groups.items():
            if emotion1.lower() in emotions and emotion2.lower() in emotions:
                return True
        return False
    
    def analyze_memory_pattern(self, user_id: str) -> Dict:
        if user_id not in self.memory_store:
            return {"pattern": "no data"}
        
        memories = self.memory_store[user_id]
        emotion_counts = {}
        total_intensity = 0
        
        for mem in memories:
            emotion_counts[mem.emotion] = emotion_counts.get(mem.emotion, 0) + 1
            total_intensity += mem.emotion_intensity
        
        avg_intensity = total_intensity / len(memories) if memories else 0
        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "unknown"
        
        return {
            "total_memories": len(memories),
            "avg_emotional_intensity": round(avg_intensity, 2),
            "most_common_emotion": most_common_emotion,
            "emotion_distribution": emotion_counts,
            "trend": "improving" if len(memories) > 0 and memories[-1].emotion_intensity < avg_intensity else "stable"
        }

memory_service = MemoryService()
EOF

# src/emotion_service.py
cat > src/emotion_service.py << 'EOF'
from typing import Dict, List
from transformers import pipeline

class EmotionService:
    def __init__(self):
        self.emotion_classifier = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
    
    def analyze_sentiment(self, text: str) -> Dict:
        try:
            result = self.emotion_classifier(text[:512])[0]
            sentiment = result['label']
            score = result['score']
            
            emotion_map = {
                "POSITIVE": "joy",
                "NEGATIVE": "sadness"
            }
            
            emotion = emotion_map.get(sentiment, "neutral")
            intensity = score if sentiment == "NEGATIVE" else (1 - score)
            
            return {
                "emotion": emotion,
                "intensity": round(intensity * 10, 2),
                "confidence": round(score, 3),
                "raw_sentiment": sentiment
            }
        except Exception as e:
            return {
                "emotion": "unknown",
                "intensity": 5.0,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def detect_emotion_shift(self, previous_emotion: str, 
                            current_emotion: str) -> Dict:
        shift_patterns = {
            ("sadness", "hope"): "positive_breakthrough",
            ("anxiety", "calm"): "anxiety_relief",
            ("anger", "peace"): "anger_resolution",
            ("despair", "determination"): "motivation_found",
            ("joy", "sadness"): "emotional_decline",
        }
        
        shift_key = (previous_emotion.lower(), current_emotion.lower())
        shift_type = shift_patterns.get(shift_key, "emotion_change")
        
        return {
            "from_emotion": previous_emotion,
            "to_emotion": current_emotion,
            "shift_type": shift_type,
            "positive_shift": shift_type in [
                "positive_breakthrough",
                "anxiety_relief",
                "anger_resolution",
                "motivation_found"
            ]
        }
    
    def generate_Harmonic Alignment_insight_from_emotion(self, emotion: str, 
                                            intensity: float) -> str:
        insights = {
            "sadness": [
                "ทุกข์นี้ไม่เที่ยง... มันจะเปลี่ยนแปลง",
                "ความเศร้าคือครูที่สอนให้รู้คุณค่า",
                "อนุญาตให้ตัวเองเศร้า... นั่นคือการยอมรับ"
            ],
            "anxiety": [
                "ความกังวลเกิดจากอนาคต... ปัจจุบันนี้ปลอดภัย",
                "ปล่อยวางการควบคุม เรียนรู้ที่จะเชื่อใจ",
                "ความกลัวบ่งชี้ว่าคุณดูแลตัวเอง"
            ],
            "anger": [
                "โครธคือสัญญาณที่บอกว่ามีขอบเขตถูกลั่วง",
                "แปลงความโกรธเป็นเอนร์จี่สำหรับการเปลี่ยนแปลง",
                "โครธที่เข้าใจแล้ว จะกลายเป็นพลังที่ชาญฉลาด"
            ],
            "joy": [
                "ความสุขชั่วขณะ... ซาบซึ้งด้วยสติ",
                "ความสุขที่แบ่งปัน จึงเพิ่มพูนขึ้น",
                "ขอบคุณสำหรับช่วงเวลาที่ดีนี้"
            ]
        }
        
        emotion_insights = insights.get(emotion.lower(), [
            "ทุกอารมณ์คือข้อมูล ไม่ใช่ความจริง",
            "สังเกตด้วยสติ ไม่ต้องตัดสิน"
        ])
        
        if intensity > 7:
            return emotion_insights[0]
        elif intensity > 4:
            return emotion_insights[1] if len(emotion_insights) > 1 else emotion_insights[0]
        else:
            return emotion_insights[-1]

emotion_service = EmotionService()
EOF

# src/personalization_engine.py
cat > src/personalization_engine.py << 'EOF'
from typing import Dict, List
from memory_service import memory_service
from emotion_service import emotion_service

class PersonalizationEngine:
    def __init__(self):
        pass
    
    def generate_personalized_response(self, user_id: str, 
                                      current_emotion: str,
                                      current_message: str) -> Dict:
        user_memories = memory_service.retrieve_user_context(user_id, days_back=30)
        user_pattern = memory_service.analyze_memory_pattern(user_id)
        linked_memories = memory_service.find_linked_memories(user_id, current_emotion)
        
        current_analysis = emotion_service.analyze_sentiment(current_message)
        
        base_response = self._generate_base_compassion_response(
            current_emotion,
            current_analysis['intensity']
        )
        
        personalized_response = self._enhance_with_context(
            base_response,
            user_memories,
            user_pattern,
            linked_memories,
            current_emotion
        )
        
        return {
            "personalized_response": personalized_response,
            "emotion": current_emotion,
            "intensity": current_analysis['intensity'],
            "user_pattern": user_pattern,
            "similar_past_experiences": len(linked_memories),
            "recommendations": self._generate_recommendations(
                current_emotion,
                user_pattern,
                current_analysis['intensity']
            )
        }
    
    def _generate_base_compassion_response(self, emotion: str, 
                                         intensity: float) -> str:
        responses = {
            "sadness": {
                "high": "ความเศร้าที่คุณรู้สึก... มันสำคัญ ผมรับรู้",
                "medium": "ความเศร้านี้คือส่วนหนึ่งของการเป็นมนุษย์",
                "low": "ความเศร้าก็ผ่านไป เหมือนเมฆในท้องฟ้า"
            },
            "anxiety": {
                "high": "ความกังวลมาแรง... ให้ผมอยู่ตรงนี้กับคุณ",
                "medium": "ความกลัวบ่งชี้ว่าคุณเนื้อใจดูแล",
                "low": "ความวิตกกังวลเพียงเล็กน้อย... ลองหายใจลึก"
            },
            "anger": {
                "high": "โครธนี้ถูกต้อง... ขอบเขตถูกละเมิด",
                "medium": "โครธบ่งชี้ว่ามีอะไรต้องเปลี่ยน",
                "low": "ความรำคาญเล็กน้อย... สังเกตแล้วปล่อย"
            },
            "joy": {
                "high": "ความสุขนี้มาจากไหน... ตัวแสง",
                "medium": "ความพึงพอใจนี้... ซาบซึ้งมันไว้",
                "low": "สามารถหาความยินดีเพิ่มในช่วงนี้"
            }
        }
        
        emotion_key = emotion.lower()
        intensity_key = "high" if intensity > 7 else ("medium" if intensity > 4 else "low")
        
        return responses.get(emotion_key, {}).get(intensity_key, 
            "ผมรับรู้ความรู้สึกของคุณ... พยายามเข้าใจมัน")
    
    def _enhance_with_context(self, base_response: str, 
                             user_memories: List[Dict],
                             user_pattern: Dict,
                             linked_memories: List[Dict],
                             current_emotion: str) -> str:
        enhancements = []
        
        if linked_memories:
            past_intensity = linked_memories[0]['memory']['emotion_intensity']
            enhancements.append(
                f"เคยผ่านจุดนี้มาแล้ว... และคุณได้มาได้ (ครั้งที่ {len(linked_memories)})"
            )
        
        if user_pattern.get('trend') == 'improving':
            enhancements.append("ผมเห็นคุณกำลังเพิ่มขึ้น... ตั้งแต่ที่เรารู้จัก")
        
        if user_memories:
            most_recent = user_memories[0]
            if most_recent.get('Harmonic Alignment_insight'):
                enhancements.append(f"จำไว้: {most_recent['Harmonic Alignment_insight']}")
        
        enhanced = base_response
        if enhancements:
            enhanced += "\n\n" + "\n".join(enhancements)
        
        return enhanced
    
    def _generate_recommendations(self, emotion: str, user_pattern: Dict,
                                 intensity: float) -> List[str]:
        recommendations = []
        
        if intensity > 7:
            recommendations.append("ลองการหายใจเชิงสติ: หายใจเข้า 4 วินาที หายใจออก 6 วินาที")
            recommendations.append("เขียนบันทึกสิ่งที่รู้สึก (5-10 นาที)")
        
        if emotion.lower() == "anxiety":
            recommendations.append("ลองการนั่งสมาธิ 5 นาที")
            recommendations.append("ไปเดินสักครู่นึง หรือยืดเหยียด")
        
        if user_pattern.get('most_common_emotion') == emotion.lower():
            recommendations.append("ดูเหมือนเรื่องนี้ขึ้นมาบ่อย... อาจต้องพูดกับที่ปรึกษา")
        
        return recommendations

personalization_engine = PersonalizationEngine()
EOF

# src/Harmonic Alignment_service.py
cat > src/Harmonic Alignment_service.py << 'EOF'
from typing import Dict

class Harmonic AlignmentService:
    def __init__(self):
        self.four_noble_truths = {
            "dukkha": "Suffering exists",
            "samudaya": "Suffering has causes", 
            "nirodha": "Suffering can end",
            "magga": "Path to end suffering"
        }
    
    def apply_four_noble_truths(self, problem: str, emotion: str, 
                               intensity: float) -> Dict:
        return {
            "dukkha": self._analyze_dukkha(problem, intensity),
            "samudaya": self._analyze_samudaya(problem, emotion),
            "nirodha": self._analyze_nirodha(problem),
            "magga": self._analyze_magga(problem, emotion),
            "dharmic_path": self._suggest_dharmic_path(emotion, intensity)
        }
    
    def _analyze_dukkha(self, problem: str, intensity: float) -> Dict:
        return {
            "truth": "ทุกข์นี้มีจริง",
            "validation": f"ความเจ็บปวดของคุณเป็นของจริง (ระดับ {intensity}/10)",
            "Harmonic Alignment_insight": "การยอมรับทุกข์ คือขั้นแรกของการปลดปล่อย",
            "reflection": "คุณรู้สึกถูกต้องที่จะรู้สึกแบบนี้"
        }
    
    def _analyze_samudaya(self, problem: str, emotion: str) -> Dict:
        cause_patterns = {
            "sadness": "การสูญเสีย การปฏิเสธ การคาดหวังที่ไม่เป็นจริง",
            "anxiety": "ความไม่แน่นอน การพยายามควบคุม การกำหนดจำกัด",
            "anger": "ขอบเขตถูกละเมิด ความรู้สึกไม่เป็นธรรม ความอยุติธรรม",
            "guilt": "ความท้อแท้ ความไม่ยอมรับตนเอง การติเตียน"
        }
        
        probable_cause = cause_patterns.get(emotion.lower(), "ความต้องการที่ไม่ได้รับ")
        
        return {
            "truth": "ทุกข์เกิดจากสาเหตุ",
            "probable_cause": probable_cause,
            "Harmonic Alignment_insight": "เมื่อเข้าใจสาเหตุ เราจึงมีพลังเปลี่ยนแปลง",
            "deeper_question": "อะไรคือความปรารถนาที่ยังไม่ได้รับ?"
        }
    
    def _analyze_nirodha(self, problem: str) -> Dict:
        return {
            "truth": "ทุกข์นี้สามารถสิ้นสุดได้",
            "vision": "คุณอาจไม่สามารถเปลี่ยนแปลงปัญหา แต่คุณสามารถเปลี่ยนแปลงความสัมพันธ์กับมัน",
            "Harmonic Alignment_insight": "การปลดปล่อย คือการปล่อยวางการต่อสู้ ไม่ใช่การยอมแพ้",
            "future_state": "คุณสามารถอยู่ร่วมกับปัญหานี้ได้ โดยไม่ให้มันปกครองใจ"
        }
    
    def _analyze_magga(self, problem: str, emotion: str) -> Dict:
        eightfold_path = {
            "Right View": "เข้าใจความจริง",
            "Right Intention": "ตั้งใจอย่างสุขมีไมตร",
            "Right Speech": "พูดจาตรวจสอบความจริง",
            "Right Action": "ปฏิบัติตามคุณธรรม",
            "Right Livelihood": "มีชีวิตอย่างสุจริต",
            "Right Effort": "พยายามเพาะเพิ่มสิ่งดี",
            "Right Mindfulness": "สังเกตการณ์ด้วยสติ",
            "Right Concentration": "หมั่นสมาธิ"
        }
        
        return {
            "truth": "มีทางออก (Noble Eightfold Path)",
            "path": eightfold_path,
            "practical_steps": self._suggest_practical_steps(emotion),
            "Harmonic Alignment_insight": "ทางออกมีอยู่ในทุกช่วงเวลา"
        }
    
    def _suggest_practical_steps(self, emotion: str) -> list:
        steps = {
            "sadness": [
                "1. ยอมรับความเศร้า (Right View)",
                "2. สมาธิสั้นๆ 5 นาที (Right Concentration)",
                "3. เขียนบันทึกการสูญเสีย (Right Speech to self)",
                "4. ถ้าพร้อม ให้อภัยตัวเอง (Right Action)"
            ],
            "anxiety": [
                "1. สังเกตว่าไม่เป็นจริง (Right View)",
                "2. หายใจลึก 3 ครั้ง (Right Effort)",
                "3. ติดตัวเองกับปัจจุบัน (Right Mindfulness)",
                "4. ทำสิ่งเล็กๆ หนึ่งสิ่ง (Right Action)"
            ],
            "anger": [
                "1. สัญญาของโครธเป็นเสียง (Right View)",
                "2. เดินอย่างรู้สึก (Right Action)",
                "3. ระบายด้วยสติ (Right Speech to self)",
                "4. ปล่อยการต่อสู้ (Right Intention)"
            ]
        }
        
        return steps.get(emotion.lower(), [
            "1. สังเกตด้วยสติ",
            "2. หายใจเชิงสติ",
            "3. เวลา และการยอมรับ",
            "4. ปล่อยการยึดมั่น"
        ])
    
    def _suggest_dharmic_path(self, emotion: str, intensity: float) -> str:
        if intensity > 8:
            return "ทุกข์นี้คือการเรียกหา... เรียกหาการเปลี่ยนแปลง เรียกหาจิตสำนึก เรียกหากรรมทีดี"
        elif intensity > 5:
            return "สิ่งที่คุณรู้สึกนี้... คือโอกาส ให้เกิดปัญญา"
        else:
            return "ดำเนินต่อไปด้วยสติ... ยิ่งเบา ยิ่งชาญฉลาด"

Harmonic Alignment_service = Harmonic AlignmentService()
EOF

# src/safety_service.py
cat > src/safety_service.py << 'EOF'
from typing import Dict, List
from config import config

class SafetyService:
    def __init__(self):
        self.crisis_keywords = config.CRISIS_KEYWORDS
        self.crisis_escalation_log = []
    
    def detect_crisis(self, user_message: str, user_id: str, 
                     emotion_intensity: float) -> Dict:
        has_crisis_keywords = any(
            keyword in user_message.lower() 
            for keyword in self.crisis_keywords
        )
        
        high_emotion = emotion_intensity > 8
        is_crisis = has_crisis_keywords or (high_emotion and emotion_intensity > 9)
        
        return {
            "is_crisis": is_crisis,
            "crisis_indicators": {
                "has_dangerous_keywords": has_crisis_keywords,
                "extreme_emotion": high_emotion,
                "emotion_intensity": emotion_intensity
            },
            "action_required": is_crisis
        }
    
    def handle_crisis_escalation(self, user_id: str, user_message: str,
                                emotion: str) -> Dict:
        escalation_response = {
            "user_id": user_id,
            "status": "CRISIS_PROTOCOL_ACTIVATED",
            "message": self._generate_crisis_response(emotion),
            "resources": self._get_crisis_resources(),
            "action": "ESCALATE_TO_HUMAN",
            "alert_sent": True,
            "timestamp": str(__import__('time').time())
        }
        
        self.crisis_escalation_log.append(escalation_response)
        return escalation_response
    
    def _generate_crisis_response(self, emotion: str) -> str:
        return (
            "🚨 ผมรู้สึกว่าสถานการณ์นี้ร้ายแรง\n\n"
            "ขอให้คุณติดต่อผู้เชี่ยวชาญด้านจิตสุขภาพ ด้วยตนเดียวหรือให้ผู้ใหญ่ช่วย\n\n"
            "⚠️ หากมีความคิดอันตราย ให้โทร:\n"
            "🆘 สายด่วนจิตสุขภาพ: 1300 NAMO AI\n"
            "🏥 โรงพยาบาล: 1669\n\n"
            "คุณไม่ได้อยู่คนเดียว"
        )
    
    def _get_crisis_resources(self) -> List[Dict]:
        return [
            {
                "type": "hotline",
                "name": "Crisis Hotline",
                "number": "1300-NAMO-AI",
                "available": "24/7"
            },
            {
                "type": "text",
                "name": "Crisis Text Line",
                "code": "Text HOME to 741741",
                "available": "24/7"
            },
            {
                "type": "online",
                "name": "Mental Health Organization",
                "url": "www.mentalhealth.org",
                "available": "24/7"
            }
        ]
    
    def validate_response_safety(self, response_text: str) -> Dict:
        unsafe_patterns = [
            "you should hurt yourself",
            "take your life",
            "you are worthless",
            "nobody cares"
        ]
        
        is_safe = not any(
            pattern in response_text.lower()
            for pattern in unsafe_patterns
        )
        
        return {
            "is_safe": is_safe,
            "validation_passed": is_safe,
            "message": "Response is safe" if is_safe else "Response flagged for review"
        }

safety_service = SafetyService()
EOF

# src/main.py
cat > src/main.py << 'EOF'
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import config
from memory_service import memory_service
from emotion_service import emotion_service
from personalization_engine import personalization_engine
from Harmonic Alignment_service import Harmonic Alignment_service
from safety_service import safety_service

app = FastAPI(
    title="NamoNexus MVP",
    description="AI Mental Health Companion with Harmonic Alignment Engine",
    version="0.1.0"
)

class UserMessage(BaseModel):
    user_id: str
    message: str
    previous_emotion: Optional[str] = None

class HealthCheck(BaseModel):
    status: str
    version: str

@app.get("/health", response_model=HealthCheck)
async def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0"
    }

@app.post("/namo/interact")
async def namo_interact(user_msg: UserMessage):
    user_id = user_msg.user_id
    message = user_msg.message
    
    try:
        emotion_analysis = emotion_service.analyze_sentiment(message)
        emotion = emotion_analysis['emotion']
        intensity = emotion_analysis['intensity']
        
        crisis_check = safety_service.detect_crisis(message, user_id, intensity)
        
        if crisis_check['is_crisis']:
            crisis_response = safety_service.handle_crisis_escalation(
                user_id, message, emotion
            )
            memory_service.store_experience(
                user_id, message, emotion, intensity,
                Harmonic Alignment_insight="⚠️ Crisis detected - Human escalation initiated"
            )
            return crisis_response
        
        personalized = personalization_engine.generate_personalized_response(
            user_id, emotion, message
        )
        
        Harmonic Alignment_analysis = Harmonic Alignment_service.apply_four_noble_truths(
            message, emotion, intensity
        )
        
        final_response = (
            personalized['personalized_response'] + "\n\n" +
            f"🙏 {Harmonic Alignment_analysis['dharmic_path']}"
        )
        
        safety_check = safety_service.validate_response_safety(final_response)
        
        if not safety_check['is_safe']:
            final_response = "ผมเข้าใจความรู้สึกของคุณ... โปรดติดต่อที่ปรึกษาสำหรับการช่วยเหลือลึกขึ้น"
        
        Harmonic Alignment_insight = Harmonic Alignment_analysis.get('dukkha', {}).get('Harmonic Alignment_insight', '')
        memory_service.store_experience(
            user_id, message, emotion, intensity, Harmonic Alignment_insight
        )
        
        return {
            "user_id": user_id,
            "response": final_response,
            "emotion_detected": emotion,
            "emotion_intensity": intensity,
            "recommendations": personalized['recommendations'],
            "Harmonic Alignment_path": Harmonic Alignment_analysis['magga'],
            "memory_stored": True,
            "crisis_status": "normal"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/namo/user-context/{user_id}")
async def get_user_context(user_id: str, days: int = 30):
    try:
        context = memory_service.retrieve_user_context(user_id, days_back=days)
        pattern = memory_service.analyze_memory_pattern(user_id)
        return {
            "user_id": user_id,
            "memory_count": len(context),
            "pattern": pattern,
            "recent_memories": context[:5]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/namo/user-pattern/{user_id}")
async def get_user_pattern(user_id: str):
    try:
        pattern = memory_service.analyze_memory_pattern(user_id)
        return pattern
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/namo/analyze-emotion")
async def analyze_emotion(text: str):
    try:
        analysis = emotion_service.analyze_sentiment(text)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/namo/Harmonic Alignment-guidance")
async def get_Harmonic Alignment_guidance(problem: str, emotion: str = "sadness", 
                             intensity: float = 5.0):
    try:
        guidance = Harmonic Alignment_service.apply_four_noble_truths(
            problem, emotion, intensity
        )
        return guidance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/namo/crisis-check")
async def crisis_check(user_id: str, message: str):
    try:
        analysis = emotion_service.analyze_sentiment(message)
        crisis = safety_service.detect_crisis(message, user_id, analysis['intensity'])
        return crisis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG
    )
EOF

# Step 6: Create .env file
cat > .env << 'EOF'
DEBUG=True
FIREBASE_KEY=
DATABASE_URL=localhost
EOF

# Step 7: Run server
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting NamoNexus MVP..."
echo ""
python src/main.py

📝 Test Commands (ให้ Jules รัน หลังจากเซิร์ฟเวอร์เริ่ม):

# ============================================
# TEST COMMANDS - Run in NEW Terminal
# ============================================

# Test 1: Health Check
curl -X GET http://localhost:8000/health

# Test 2: Main Interaction (Sadness)
curl -X POST http://localhost:8000/namo/interact \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "ผมรู้สึกเหงาและเศร้า"
  }'

# Test 3: Emotion Analysis
curl -X POST http://localhost:8000/namo/analyze-emotion?text=ผมรู้สึกดีใจ

# Test 4: Harmonic Alignment Guidance
curl -X POST http://localhost:8000/namo/Harmonic Alignment-guidance \
  -H "Content-Type: application/json" \
  -d '{
    "problem": "ผมรู้สึกเศร้า",
    "emotion": "sadness",
    "intensity": 7.5
  }'

# Test 5: User Context
curl -X GET http://localhost:8000/namo/user-context/user123

# Test 6: Crisis Detection
curl -X POST http://localhost:8000/namo/crisis-check \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "ผมอยากตัดสินใจสิ้นสุดชีวิต"
  }'
