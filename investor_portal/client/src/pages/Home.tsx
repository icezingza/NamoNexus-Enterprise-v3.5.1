import { Button } from "@/components/ui/button";
import { ArrowRight, TrendingUp, Users, Shield, Zap } from "lucide-react";
import { useEffect, useState } from "react";

/**
 * NamoNexus Investor Portal - Landing Page
 * Design: Minimalist Tech Elegance
 * Color Scheme: Deep Indigo (#0B1026) + Gold (#D4AF37)
 * Typography: Playfair Display (headlines) + Lato (body)
 */

export default function Home() {
  const [callsProcessed, setCallsProcessed] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  // Animate counter on mount
  useEffect(() => {
    setIsVisible(true);
    const interval = setInterval(() => {
      setCallsProcessed((prev) => {
        if (prev < 847532) {
          return prev + Math.floor(Math.random() * 500) + 100;
        }
        return prev;
      });
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-border">
        <div className="container max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">N</span>
            </div>
            <span className="font-playfair font-bold text-xl text-primary">NamoNexus</span>
          </div>
          <div className="flex gap-4">
            <Button variant="ghost" className="text-foreground">
              About
            </Button>
            <Button className="bg-accent text-primary hover:bg-accent/90">
              Get Started
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5"></div>

        <div className="container max-w-7xl mx-auto px-4 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left: Text Content */}
            <div className="space-y-8">
              <div className="space-y-4">
                <h1 className="font-playfair font-bold text-5xl lg:text-6xl leading-tight text-primary">
                  ปัญญาประดิษฐ์อธิปไตย
                  <span className="block text-accent">เพื่อสุขภาพจิตไทย</span>
                </h1>
                <p className="text-lg text-muted-foreground leading-relaxed max-w-md">
                  ลงทุนในเทคโนโลยี AI ที่เข้าใจวัฒนธรรมไทย ปกป้องข้อมูลประเทศ และช่วยชีวิตคนไทยจากวิกฤตสุขภาพจิต
                </p>
              </div>

              {/* Key Stats */}
              <div className="grid grid-cols-2 gap-4 pt-4">
                <div className="bg-white border border-border rounded-lg p-4">
                  <div className="text-sm text-muted-foreground mb-2">ลดเวลารอ</div>
                  <div className="text-3xl font-bold text-accent">70%</div>
                </div>
                <div className="bg-white border border-border rounded-lg p-4">
                  <div className="text-sm text-muted-foreground mb-2">ความแม่นยำ</div>
                  <div className="text-3xl font-bold text-accent">77%</div>
                </div>
              </div>

              {/* CTA Buttons */}
              <div className="flex gap-4 pt-4">
                <Button className="bg-accent text-primary hover:bg-accent/90 px-8 py-6 text-lg">
                  ดูข้อเสนอการลงทุน
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
                <Button variant="outline" className="px-8 py-6 text-lg border-primary text-primary hover:bg-primary/5">
                  ติดต่อเรา
                </Button>
              </div>
            </div>

            {/* Right: Live Counter & Visual */}
            <div className="relative h-96 lg:h-full min-h-96">
              <div className="absolute inset-0 bg-gradient-to-br from-primary to-primary/50 rounded-2xl opacity-10"></div>

              <div className="relative h-full flex flex-col justify-center items-center space-y-8 p-8">
                {/* Animated Counter */}
                <div className="text-center space-y-4">
                  <div className="text-6xl lg:text-7xl font-bold text-accent font-playfair">
                    {callsProcessed.toLocaleString()}
                  </div>
                  <p className="text-lg text-muted-foreground">
                    สายที่ AI ประมวลผลแล้ว
                  </p>
                  <div className="w-full h-1 bg-border rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-accent to-primary transition-all duration-500"
                      style={{
                        width: `${Math.min((callsProcessed / 1000000) * 100, 100)}%`,
                      }}
                    ></div>
                  </div>
                </div>

                {/* Feature Icons */}
                <div className="grid grid-cols-2 gap-4 w-full">
                  <div className="bg-white border border-border rounded-lg p-4 text-center hover:border-accent transition-colors">
                    <Shield className="w-8 h-8 text-accent mx-auto mb-2" />
                    <p className="text-sm font-medium text-primary">ความปลอดภัย</p>
                  </div>
                  <div className="bg-white border border-border rounded-lg p-4 text-center hover:border-accent transition-colors">
                    <Zap className="w-8 h-8 text-accent mx-auto mb-2" />
                    <p className="text-sm font-medium text-primary">ความเร็ว</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="h-px bg-gradient-to-r from-transparent via-accent to-transparent"></div>

      {/* Impact Section */}
      <section className="py-20 bg-primary text-white">
        <div className="container max-w-7xl mx-auto px-4">
          <h2 className="font-playfair font-bold text-4xl mb-12 text-center">
            ผลกระทบที่วัดผลได้
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Impact Card 1 */}
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg p-8 hover:border-accent/50 transition-colors">
              <TrendingUp className="w-12 h-12 text-accent mb-4" />
              <h3 className="font-playfair font-bold text-2xl mb-2">1.5-2B THB</h3>
              <p className="text-white/80">
                มูลค่าทางเศรษฐกิจสังคมต่อปี (Social Economic Value)
              </p>
            </div>

            {/* Impact Card 2 */}
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg p-8 hover:border-accent/50 transition-colors">
              <Users className="w-12 h-12 text-accent mb-4" />
              <h3 className="font-playfair font-bold text-2xl mb-2">300K+</h3>
              <p className="text-white/80">
                ผู้ป่วยที่ได้รับการช่วยเหลือในปีแรก
              </p>
            </div>

            {/* Impact Card 3 */}
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg p-8 hover:border-accent/50 transition-colors">
              <Shield className="w-12 h-12 text-accent mb-4" />
              <h3 className="font-playfair font-bold text-2xl mb-2">100%</h3>
              <p className="text-white/80">
                ข้อมูลอยู่ภายในประเทศ (Sovereign AI)
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="h-px bg-gradient-to-r from-transparent via-accent to-transparent"></div>

      {/* Technology Section */}
      <section className="py-20">
        <div className="container max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left: Content */}
            <div className="space-y-8">
              <h2 className="font-playfair font-bold text-4xl text-primary">
                เทคโนโลยี Sovereign AI
              </h2>

              <div className="space-y-6">
                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-accent/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Zap className="w-6 h-6 text-accent" />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-primary mb-2">
                      AI Triage ที่เข้าใจภาษาไทย
                    </h3>
                    <p className="text-muted-foreground">
                      ประมวลผลสัญญาณจากใบหน้า เสียง และข้อความ ด้วยความแม่นยำ 77%
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-accent/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Shield className="w-6 h-6 text-accent" />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-primary mb-2">
                      Dhammic Moat - เกราะป้องกันเชิงธรรมะ
                    </h3>
                    <p className="text-muted-foreground">
                      AI ที่มีจริยธรรม ปกป้องคุณค่าแห่งสังคมไทย ไม่พึ่งพา API ต่างชาติ
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-accent/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <TrendingUp className="w-6 h-6 text-accent" />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-primary mb-2">
                      Grid Intelligence - ระบบอัจฉริยะ
                    </h3>
                    <p className="text-muted-foreground">
                      ปรับปรุงอย่างต่อเนื่อง ลดเวลารอจาก 40 นาทีเหลือ 12 นาที
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Right: Visual */}
            <div className="bg-gradient-to-br from-primary/10 to-accent/10 rounded-2xl p-12 border border-accent/20 h-96 flex items-center justify-center">
              <div className="text-center space-y-4">
                <div className="text-6xl font-bold text-accent font-playfair">AI</div>
                <p className="text-lg text-primary font-medium">
                  Sovereign Intelligence
                </p>
                <p className="text-sm text-muted-foreground">
                  ปัญญาประดิษฐ์ที่เป็นของไทย
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="h-px bg-gradient-to-r from-transparent via-accent to-transparent"></div>

      {/* Investment Opportunity Section */}
      <section className="py-20 bg-primary text-white">
        <div className="container max-w-7xl mx-auto px-4">
          <div className="text-center space-y-8 mb-12">
            <h2 className="font-playfair font-bold text-4xl">
              โอกาสการลงทุน
            </h2>
            <p className="text-xl text-white/80 max-w-2xl mx-auto">
              ร่วมสร้างอนาคตสุขภาพจิตไทย และเป็นส่วนหนึ่งของการปฏิวัติเทคโนโลยีอธิปไตย
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-2xl mx-auto">
            {/* Investment Details */}
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg p-8">
              <h3 className="font-playfair font-bold text-2xl mb-4">Series A Round</h3>
              <ul className="space-y-3 text-white/80">
                <li className="flex items-start gap-3">
                  <span className="text-accent font-bold">✓</span>
                  <span>R&D & Tech Development</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent font-bold">✓</span>
                  <span>Infrastructure Expansion</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent font-bold">✓</span>
                  <span>Market Development</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent font-bold">✓</span>
                  <span>Operations & Team</span>
                </li>
              </ul>
            </div>

            {/* Expected Returns */}
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg p-8">
              <h3 className="font-playfair font-bold text-2xl mb-4">Expected Returns</h3>
              <ul className="space-y-3 text-white/80">
                <li className="flex items-start gap-3">
                  <span className="text-accent font-bold">→</span>
                  <span>Financial ROI: 3-5 years horizon</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent font-bold">→</span>
                  <span>Social ROI: 1.5-2B THB/year</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent font-bold">→</span>
                  <span>Strategic Asset: Data Moat</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent font-bold">→</span>
                  <span>Market Size: 100B+ THB</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="h-px bg-gradient-to-r from-transparent via-accent to-transparent"></div>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container max-w-4xl mx-auto px-4 text-center space-y-8">
          <h2 className="font-playfair font-bold text-4xl text-primary">
            พร้อมที่จะร่วมสร้างอนาคต?
          </h2>
          <p className="text-lg text-muted-foreground">
            ติดต่อทีมงาน NamoNexus เพื่อรับเอกสารข้อเสนอการลงทุนฉบับสมบูรณ์ และนัดหมายการประชุมเพิ่มเติม
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
            <Button className="bg-accent text-primary hover:bg-accent/90 px-8 py-6 text-lg">
              ขอรับเอกสารข้อเสนอ
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            <Button variant="outline" className="px-8 py-6 text-lg border-primary text-primary hover:bg-primary/5">
              ติดต่อเรา: invest@namonexus.ai
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-primary text-white py-12 border-t border-accent/20">
        <div className="container max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="font-playfair font-bold text-lg mb-4">NamoNexus</h3>
              <p className="text-white/60 text-sm">
                ปัญญาประดิษฐ์อธิปไตยเพื่อการปฏิรูปสุขภาพจิตไทย
              </p>
            </div>
            <div>
              <h4 className="font-bold mb-4">Product</h4>
              <ul className="space-y-2 text-white/60 text-sm">
                <li><a href="#" className="hover:text-accent transition">Features</a></li>
                <li><a href="#" className="hover:text-accent transition">Technology</a></li>
                <li><a href="#" className="hover:text-accent transition">Security</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Company</h4>
              <ul className="space-y-2 text-white/60 text-sm">
                <li><a href="#" className="hover:text-accent transition">About</a></li>
                <li><a href="#" className="hover:text-accent transition">Team</a></li>
                <li><a href="#" className="hover:text-accent transition">Blog</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Contact</h4>
              <ul className="space-y-2 text-white/60 text-sm">
                <li>invest@namonexus.ai</li>
                <li>+66 2 123 4567</li>
                <li>Bangkok, Thailand</li>
              </ul>
            </div>
          </div>

          <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center text-white/60 text-sm">
            <p>&copy; 2025 NamoNexus. All rights reserved.</p>
            <div className="flex gap-6 mt-4 md:mt-0">
              <a href="#" className="hover:text-accent transition">Privacy</a>
              <a href="#" className="hover:text-accent transition">Terms</a>
              <a href="#" className="hover:text-accent transition">Cookies</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
