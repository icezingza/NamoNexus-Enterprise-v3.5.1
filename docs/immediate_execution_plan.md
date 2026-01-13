# แผนปฏิบัติการเร่งด่วน (This Week + 3 Months)

## สิ่งที่ต้องทำทันที (This Week)

### Code Cleanup
- ใช้สคริปต์ใน Simplification Plan: `scripts/simplify_codebase.py`
- ย้าย research modules ออกจาก production codebase
- วัด test coverage ปัจจุบัน

### Testing
- เขียน safety tests ตาม Testing Strategy (`docs/testing_strategy.md`)
- ตั้งเป้า 80% coverage ใน 2 สัปดาห์
- ทำ performance baseline

### Business Validation
- จัด 5 customer interviews
- เตรียม pilot proposal
- อัปเดตการเงินตาม Business Validation Plan (`docs/business_model_validation_plan.md`)

## สิ่งที่ต้องหยุดทำ (Stop Doing)
- หยุดเพิ่ม features ใหม่จนกว่าจะมีลูกค้าจริง
- หยุด over-engineering (quantum consciousness ไม่จำเป็น)
- หยุดวางแผนระยะยาวโดยไม่มี validation
- หยุดสมมติว่าราคาที่ตั้งไว้ถูกต้อง ต้องทดสอบ

## แผนที่ชัดเจน 3 เดือนข้างหน้า

| Month | Focus | Key Deliverable | Budget |
| --- | --- | --- | --- |
| 1 | Simplify + Test | Production-ready code | 200K THB |
| 2 | Pilot Setup | Live pilot, first metrics | 300K THB |
| 3 | Pilot Execute | Decision report + testimonial | 200K THB |

Gate 1 Decision (Month 3): มี evidence พอจะขายหรือไม่?

## ความเสี่ยงสูงสุด 3 อันดับ

### Over-Engineering Risk
ปัญหา: มี code มากเกินไป ทำให้ maintain ยาก
ทางแก้: ใช้ simplification plan ทันที

### Pricing Risk
ปัญหา: ราคาอาจสูงเกินไป ยังไม่ validated
ทางแก้: ทำ customer discovery + pricing experiments

### Regulatory Risk
ปัญหา: Thai FDA ใช้เวลา 18 เดือน + costly
ทางแก้: รอ validate business ก่อน ค่อยทำ FDA

## ข้อเสนอแนะสำคัญ

### สำหรับ Technical Lead
- ทำ code cleanup ตาม Simplification Plan
- เน้น testing และ production readiness
- พร้อม deploy ได้ทันทีเมื่อมี pilot customer

### สำหรับ Business Lead
- หา pilot customer 1 รายภายใน 4 สัปดาห์
- ทดสอบราคาจริง อย่าสมมติ
- เตรียมแผน pivot ถ้าไม่ได้ลูกค้า

### สำหรับ Leadership
- อนุมัติงบ 700K THB สำหรับ 3 เดือนแรก
- ตั้ง decision gate ชัดเจนที่เดือนที่ 3
- พร้อมปรับกลยุทธ์ถ้า validation ไม่ผ่าน

## Artifacts ที่พร้อมใช้งาน
- Simplification Plan: `scripts/simplify_codebase.py`
- Testing Strategy: `docs/testing_strategy.md`
- Deployment Checklist: `docs/deployment_checklist.md`
- Business Validation Plan: `docs/business_model_validation_plan.md`
- 12-Month Roadmap: `docs/roadmap_12_month_prioritized.md`

## คำถามสำคัญที่ต้องตอบ
- มีงบประมาณเท่าไหร่สำหรับ 12 เดือนข้างหน้า?
  - Conservative: 6M THB
  - Minimum: 3M THB (ถ้าระวังมาก)
- พร้อม pivot หรือหยุดเมื่อไหร่?
  - ถ้าเดือนที่ 3 ไม่มี pilot สำเร็จ
  - ถ้าเดือนที่ 6 ไม่มีลูกค้าจ่ายเงิน

## Owner ของแต่ละ artifact
- Technical: CTO/Lead Engineer
- Business: CEO/BD Lead
- Decision: Board/Founder
